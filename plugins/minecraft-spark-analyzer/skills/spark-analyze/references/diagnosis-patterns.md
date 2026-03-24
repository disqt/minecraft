# Spark Diagnosis Patterns

Heavy reference for client-side FPS and server-side TPS diagnosis from Spark profiler data.

## Profiling Best Practices

### When and how to profile

| Scenario | Command | Notes |
|----------|---------|-------|
| Constant low FPS/TPS | `/sparkc profiler start --timeout 60` | Standard profile, 30-60s is ideal |
| Intermittent lag spikes | `/sparkc profiler --only-ticks-over 100 --timeout 180` | Filters out normal ticks, isolates spike data |
| Memory/GC investigation | `/sparkc profiler start --alloc` | Allocation profiling (Linux/macOS only) |
| Always-ready profiling | Enable `backgroundProfiler: true` in config | Then `/sparkc profiler open` anytime |
| All threads | `/sparkc profiler start --thread *` | When render thread alone doesn't explain the issue |

### Common profiling mistakes

- **Profiling too short (<30s):** Insufficient sample size, false leads.
- **Profiling too long (>5min):** Dilutes spikes in a sea of normal data.
- **Not using `--only-ticks-over` for spikes:** Default profiling averages everything, hiding intermittent issues. This is the most common mistake.
- **Profiling idle/empty server:** Shows "Timed wait" (sleep) because there's nothing to do. The problem area must be loaded and active.
- **Profiling right after startup:** Data is skewed by world loading, plugin init, chunk gen. Wait a few minutes.
- **Wrong location:** If lag only happens near a specific base/farm, a player must be present there during profiling.
- **Confusing percentages with severity:** 80% of a 4ms tick = 3.2ms (fine). 30% of a 200ms tick = 60ms (crisis). Always check absolute MSPT.

### Understanding self-time vs total-time

- **Total time:** How long a method and everything it calls took. High total-time means the bottleneck is somewhere in this call chain.
- **Self time:** How long the method's own code took, excluding child calls. High self-time means this specific method is the actual hot code.
- If `CraftScheduler.mainThreadHeartbeat()` shows 66% total but its children account for 65.9%, only 0.1% is self-time -- the method itself isn't slow, something it calls is.
- Use the Flat view with self-time sorting to find actual hot methods, then use the call tree to understand their context.

### Using the flame graph

- Width of each bar = time consumption. Wider = more time.
- Click any bar to "focus" it, expanding to fill width. Children scale proportionally.
- Best for getting a visual overview -- bottlenecks literally jump out as wide bars.
- Access via flame icon in controls, or right-click a thread/method.

### Mod attribution caveat

The Sources/Plugins view "blames" the mod that triggers an action for all downstream cost. Example: if a plugin activates a lever that triggers expensive redstone calculations, the plugin gets blamed for the redstone time. Always drill deeper to check if the slowness is the mod's own code or downstream vanilla processing.

## Thread Breakdown (Client)

The game loop on a Fabric client breaks into these categories. Healthy idle time is 70%+.

| Activity | Method pattern | Healthy | Problem |
|----------|---------------|---------|---------|
| Idle | `waitForNextTick`, `Thread.sleep` | 70-90% | <50% = CPU-bound |
| Rendering | `render`, `renderLevel`, `renderWorld` | 10-25% | >40% = rendering bottleneck |
| Client tick | `runTick`, `tick` | 5-15% | >25% = game logic bottleneck |
| Network | packet processing methods | <5% | >10% = network overhead (or DH) |
| VSync/swap | `glfwSwapBuffers` | 2-8% | >15% = GPU-bound (waiting for GPU) |

## Thread Breakdown (Server)

Server profiles focus on the **Server thread** (main game loop). Healthy idle/sleep time means the server has spare capacity.

| Activity | Method pattern | Healthy | Problem |
|----------|---------------|---------|---------|
| Idle/sleep | `waitForNextTick`, `Timed waiting` | 50-80% | <30% = overloaded |
| Entity ticking | `EntityTickList.forEach`, `tickNonPassengers` | 10-25% | >50% = too many entities |
| Chunk management | `ServerChunkCache.tick`, `getChunk` | 5-15% | >30% = chunk gen/loading pressure |
| Block ticking | `tickChunk`, `randomTick` | 3-10% | >20% = redstone/tile entity lag |
| Network/packets | `handle`, `Connection.tick` | 2-5% | >15% = packet processing overhead |
| Plugin/mod handlers | Event handlers, scheduled tasks | varies | check Sources view for per-plugin breakdown |

## Common Bottleneck Patterns

### Distant Horizons render-thread blocking

**Signature:** High time in `FullDataSourceV2DTO`, `LZMA2InputStream`, `NativeDB.step`, `FullDataOcclusionCuller` under network/packet processing on the render thread.

**Cause:** DH processes LOD data (decompression, SQLite writes, occlusion culling) synchronously on the render thread when receiving from a server. Known architectural issue in DH multiplayer.

**Fix:** Not user-configurable. DH team needs to move processing off render thread. Reducing DH render distance in its config can reduce the volume of data. DH also uses significant off-heap memory (not visible in Java heap stats) -- check DH's memory config if system RAM is high.

### EMF/ETF animation overhead

**Signature:** High time in `EMFAnimation.getResultViaCalculate`, EMF/ETF texture processing methods.

**Cause:** Entity Model Features + Entity Texture Features compute custom entity model animations. Amplified by FreshAnimations resource pack and high entity counts (especially villagers).

**Fix:** Disable FreshAnimations resource pack, reduce entity render distance, or remove EMF/ETF if custom entity models aren't needed.

### Shader overhead (Iris)

**Signature:** High time in shadow pass rendering, Iris composite/final passes, shader-related methods in the rendering breakdown. High LWJGL/OpenGL self-time (glDrawElements, glUseProgram, etc.) indicating GPU-bound rendering.

**Cause:** Shader packs add shadow maps, post-processing, volumetric lighting. Cost varies enormously by pack.

**Fix:** Switch to a lighter shader pack (Complementary Reimagined < BSL < SEUS PTGI), disable shadow rendering in shader settings, or disable shaders entirely.

### Chunk rendering pressure

**Signature:** High time in `compileChunks`, `uploadChunks`, chunk worker threads saturated.

**Cause:** High render distance, exploring new terrain, complex worldgen.

**Fix:** Reduce render distance (8-10 is good), reduce simulation distance.

### Entity rendering

**Signature:** High time in `renderEntities`, `renderBlockEntities`, `EntityRenderDispatcher`.

**Cause:** Many visible entities -- item frames, chests, signs, banners, mob farms.

**Fix:** Add EntityCulling mod, add Enhanced Block Entities mod, reduce entity render distance.

### Subtle Effects / ambient mods

**Signature:** High time in `FireflyManager.tick`, `GeyserManager.tick`, `GeyserTicker.isSpawnableBlock`, ambient particle/sound methods.

**Cause:** Ambient effect mods doing per-tick work (often with inefficient data structures like linear list scans).

**Fix:** Remove or configure the ambient mod to reduce effect density.

### GC pressure

**Signature:** Not directly visible in Spark profiler stacks. Manifests as periodic stutters (not constant low FPS). Check `systemStatistics.gc` for major collection frequency and duration.

**Indicators:**
- Old/major generation collections occurring at all = problem
- High heap usage (>85%) cycling in sawtooth pattern
- High allocation rate (visible in F3: >500 MB/s)

**Diagnosis:**
- `/sparkc gcmonitor` -- real-time GC event alerts
- `/sparkc tickmonitor --without-gc` -- separates GC-caused spikes from code-caused spikes
- `/sparkc heapsummary` -- class-level memory breakdown
- `/sparkc profiler start --alloc` -- allocation profiling (Linux/macOS only, requires async-profiler engine)
- `/sparkc heapdump --compress gzip` -- full HPROF for Eclipse MAT / VisualVM analysis

**Fix:** See JVM Arguments section below.

### Hopper chains (server-side)

**Signature:** High time in `HopperBlockEntity.tick`, item transfer methods.

**Cause:** Large hopper chains or hopper-based sorting systems with many active hoppers.

**Fix:** Replace hoppers with water streams where possible, use hopper-locking with composters/redstone, install optimization plugins (e.g., Lithium optimizes hopper lookups).

### Redstone machines (server-side)

**Signature:** High time in redstone tick methods, `TileEntity.tick`, block update propagation.

**Cause:** Complex redstone contraptions, flying machines, or redstone clocks.

**Fix:** Identify and optimize or disable the specific contraption. Use `/sparkc profiler --only-ticks-over 50` while near the contraption to isolate its impact.

## JVM Arguments

Source: [brucethemoose/Minecraft-Performance-Flags-Benchmarks](https://github.com/brucethemoose/Minecraft-Performance-Flags-Benchmarks) -- the most comprehensive Minecraft JVM tuning reference. Client flags differ significantly from server flags (Aikar's flags are server-only).

### Client GC recommendations

**ZGC is NOT recommended for clients** despite low-pause characteristics. It has a measurable FPS penalty.

**Shenandoah (best for clients):**
```
-XX:+UseShenandoahGC -XX:ShenandoahGCMode=iu -XX:ShenandoahGuaranteedGCInterval=1000000 -XX:AllocatePrefetchStyle=1
```

**G1GC (client-tuned, NOT Aikar's server flags, Java 21 compatible):**
```
-XX:+UseG1GC -XX:MaxGCPauseMillis=37 -XX:G1HeapRegionSize=16M -XX:G1NewSizePercent=23 -XX:G1ReservePercent=20 -XX:SurvivorRatio=32 -XX:G1MixedGCCountTarget=3 -XX:G1HeapWastePercent=20 -XX:InitiatingHeapOccupancyPercent=10 -XX:G1RSetUpdatingPauseTimePercent=0 -XX:MaxTenuringThreshold=1 -XX:G1SATBBufferEnqueueingThresholdPercent=30 -XX:G1ConcMarkStepDurationMillis=5.0 -XX:GCTimeRatio=99
```

Note: `G1ConcRSHotCardLimit` and `G1ConcRefinementServiceIntervalMillis` were removed in Java 20/21. Do not include them.

**Common base flags (Java 11+):**
```
-XX:+UnlockExperimentalVMOptions -XX:+UnlockDiagnosticVMOptions -XX:+AlwaysActAsServerClassMachine -XX:+AlwaysPreTouch -XX:+DisableExplicitGC -XX:+UseNUMA -XX:NmethodSweepActivity=1 -XX:ReservedCodeCacheSize=400M -XX:NonNMethodCodeHeapSize=12M -XX:ProfiledCodeHeapSize=194M -XX:NonProfiledCodeHeapSize=194M -XX:-DontCompileHugeMethods -XX:MaxNodeLimit=240000 -XX:NodeLimitFudgeFactor=8000 -XX:+UseVectorCmov -XX:+PerfDisableSharedMem -XX:+UseFastUnorderedTimeStamps -XX:+UseCriticalJavaThreadPriority -XX:ThreadPriorityPolicy=1 -XX:AllocatePrefetchStyle=3
```

**Heap sizing:** Set `-Xms` = `-Xmx`. Use only what's needed (4-8GB for modded). Too much heap = longer GC pauses.

### Known bad JVM configurations

| Pattern | Problem |
|---------|---------|
| ZGC on client | FPS penalty vs Shenandoah/G1GC |
| Aikar's flags on client | Server-tuned G1GC causes long client stutters |
| `-Xmx` much larger than needed | Longer GC pauses |
| `-Xms` != `-Xmx` | Heap resizing causes pauses |
| Missing `-XX:+AlwaysPreTouch` | First access to pages causes faults |

## Video Settings Impact

| Setting | Impact | Reduce when |
|---------|--------|-------------|
| Render Distance | Highest | GPU% high, chunk compilation dominant |
| Simulation Distance | High | Entity tick methods dominant |
| Graphics Quality | Medium | "Fabulous" is significantly more expensive |
| Particles | Medium | Particle rendering high in profile |
| Entity Distance | Medium | Entity rendering dominant |
| Mipmap Levels | Low-medium | GPU memory pressure |
| Biome Blend | Low | Minor rendering cost |

## Performance Mods (Fabric)

### Tier 1 -- Essential

| Mod | Fixes |
|-----|-------|
| Sodium | Rendering pipeline rewrite. Up to 300% FPS improvement |
| Lithium | Game logic optimization (physics, mob AI, block ticking) |
| FerriteCore | Memory optimization, dramatically reduces heap usage |

### Tier 2 -- Major gains

| Mod | Fixes |
|-----|-------|
| ImmediatelyFast | Batches immediate-mode draw calls. Entity rendering 3.75x faster |
| EntityCulling | Skips rendering entities behind walls |
| Enhanced Block Entities | Converts block entity rendering to baked models |
| C2ME | Parallelizes chunk generation/loading |
| ModernFix | Memory leaks, dynamic model loading, launch speed |
| MoreCulling | Aggressive block face culling |

### Tier 3 -- Supplementary

| Mod | Fixes |
|-----|-------|
| Nvidium | NVIDIA-only mesh shader rendering (incompatible with Iris) |
| Exordium | Renders HUD at lower framerate |
| Dynamic FPS | Reduces resources when in background |
| ThreadTweak | Thread scheduling improvements |

### Diagnostic mods

| Mod | Purpose |
|-----|---------|
| Observable | Visual in-world heat map of tick times per entity/block entity. Green = fast, red = slow. Great for pinpointing exactly which entity or block is lagging. Server-side diagnostic tool (measures tick time, not rendering). |

## Hardware Bottleneck Identification

### CPU-bound vs GPU-bound

| Indicator | CPU-bound | GPU-bound |
|-----------|-----------|-----------|
| F3 GPU% | Low (30-60%) | High (95%+) |
| `glfwSwapBuffers` time | Low | High (CPU waiting for GPU) |
| LWJGL/OpenGL self-time | Low | High (>50% in glDrawElements, glUseProgram, etc.) |
| Spark profile | High time in tick/logic methods | High time in render submission |
| Fix direction | Reduce entities, mods, simulation distance | Reduce render distance, disable shaders, lower graphics |

### Memory/GC vs rendering

| Indicator | GC issue | Rendering issue |
|-----------|----------|-----------------|
| Symptom | Periodic stutters/freezes | Consistently low FPS |
| FPS pattern | Spikes down then recovers | Steady low number |
| Varies with view | No | Yes (sky vs complex scene) |
| Varies with area | Less | More (entity-heavy areas) |
| Spark clue | Missing time, GC stats show major collections | Rendering methods dominate |

## Spark Commands for Further Diagnosis

| Command | Purpose |
|---------|---------|
| `/sparkc profiler start --thread *` | Profile all threads |
| `/sparkc profiler start --alloc` | Profile memory allocations (Linux/macOS) |
| `/sparkc profiler --only-ticks-over 100 --timeout 180` | Only profile slow ticks (spike isolation) |
| `/sparkc tickmonitor --threshold-tick 50` | Real-time tick duration alerts |
| `/sparkc tickmonitor --without-gc` | Tick alerts excluding GC-caused spikes |
| `/sparkc gcmonitor` | Live GC event monitoring |
| `/sparkc heapsummary` | Heap object breakdown |
| `/sparkc heapdump --compress gzip` | Full HPROF for Eclipse MAT / VisualVM |
| `/sparkc profiler open` | Open background profiler (must be enabled in config) |
| `/sparkc healthreport --memory` | System snapshot with JVM memory details |

## External Tools

| Tool | Purpose |
|------|---------|
| [Birdflop Spark Analyzer](https://www.birdflop.com/resources/sparkprofile/) | Paste a Spark URL for automated config recommendations. Created by Birdflop (501(c)(3) nonprofit). Caveat: suggestions are guidelines, not magic values. |
| [spark2json](https://github.com/lucko/spark2json) | Convert raw Spark protobuf data to JSON for custom analysis |
| Eclipse MAT / VisualVM | Analyze HPROF heap dumps from `/sparkc heapdump` |
| Observable (mod) | In-world visual heat map of tick times per entity/block entity |

## Platform-Specific Notes

### Windows swap false alarm

Spark reports Windows page file *allocated* size as "swap used", not actual usage. A "38 GB swap" reading is normal on Windows and does NOT indicate memory pressure. To check actual swap usage on Windows, run:
```powershell
Get-CimInstance Win32_PageFileUsage
```
The `CurrentUsage` field shows actual usage in MB. Only flag swap as a problem if `CurrentUsage` is high, or if the OS is Linux/macOS (where swap reporting is accurate).

### async-profiler availability

The async-profiler engine (superior to the default Java sampler) is auto-selected on Linux/macOS. It avoids safe-point sampling bias. Allocation profiling (`--alloc`) and live-only allocation profiling (`--alloc-live-only`) require async-profiler. On Windows, the Java sampler is used instead -- allocation profiling is not available.

## Known Software Conflicts

| Software | Issue |
|----------|-------|
| RivaTuner (RTSS) v7.3.3 or older | Extreme FPS drops with Sodium |
| ASUS GPU Tweak III | Injects into Java process, severe slowdown |
| OptiFine | Conflicts with Sodium, outdated rendering |
