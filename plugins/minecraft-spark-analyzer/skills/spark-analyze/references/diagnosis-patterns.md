# Spark Diagnosis Patterns

Heavy reference for client-side FPS and server-side TPS diagnosis from Spark profiler data.

## Thread Breakdown (Client)

The game loop on a Fabric client breaks into these categories. Healthy idle time is 70%+.

| Activity | Method pattern | Healthy | Problem |
|----------|---------------|---------|---------|
| Idle | `waitForNextTick`, `Thread.sleep` | 70-90% | <50% = CPU-bound |
| Rendering | `render`, `renderLevel`, `renderWorld` | 10-25% | >40% = rendering bottleneck |
| Client tick | `runTick`, `tick` | 5-15% | >25% = game logic bottleneck |
| Network | packet processing methods | <5% | >10% = network overhead (or DH) |
| VSync/swap | `glfwSwapBuffers` | 2-8% | >15% = GPU-bound (waiting for GPU) |

## Common Bottleneck Patterns

### Distant Horizons render-thread blocking

**Signature:** High time in `FullDataSourceV2DTO`, `LZMA2InputStream`, `NativeDB.step`, `FullDataOcclusionCuller` under network/packet processing on the render thread.

**Cause:** DH processes LOD data (decompression, SQLite writes, occlusion culling) synchronously on the render thread when receiving from a server. Known architectural issue in DH multiplayer.

**Fix:** Not user-configurable. DH team needs to move processing off render thread. Reducing DH render distance in its config can reduce the volume of data.

### EMF/ETF animation overhead

**Signature:** High time in `EMFAnimation.getResultViaCalculate`, EMF/ETF texture processing methods.

**Cause:** Entity Model Features + Entity Texture Features compute custom entity model animations. Amplified by FreshAnimations resource pack and high entity counts (especially villagers).

**Fix:** Disable FreshAnimations resource pack, reduce entity render distance, or remove EMF/ETF if custom entity models aren't needed.

### Shader overhead (Iris)

**Signature:** High time in shadow pass rendering, Iris composite/final passes, shader-related methods in the rendering breakdown.

**Cause:** Shader packs add shadow maps, post-processing, volumetric lighting. Cost varies enormously by pack.

**Fix:** Switch to a lighter shader pack (Complementary Reimagined < BSL < SEUS PTGI), disable shadow rendering in shader settings, or disable shaders entirely.

### Chunk rendering pressure

**Signature:** High time in `compileChunks`, `uploadChunks`, chunk worker threads saturated.

**Cause:** High render distance, exploring new terrain, complex worldgen.

**Fix:** Reduce render distance (8-10 is good), reduce simulation distance.

### Entity rendering

**Signature:** High time in `renderEntities`, `renderBlockEntities`, `EntityRenderDispatcher`.

**Cause:** Many visible entities — item frames, chests, signs, banners, mob farms.

**Fix:** Add EntityCulling mod, add Enhanced Block Entities mod, reduce entity render distance.

### Subtle Effects / ambient mods

**Signature:** High time in `FireflyManager.tick`, `GeyserManager.tick`, ambient particle/sound methods.

**Cause:** Ambient effect mods doing per-tick work (often with inefficient data structures like linear list scans).

**Fix:** Remove or configure the ambient mod to reduce effect density.

### GC pressure

**Signature:** Not directly visible in Spark profiler stacks. Manifests as periodic stutters (not constant low FPS). Check `systemStatistics.gc` for major collection frequency and duration.

**Indicators:**
- Old/major generation collections occurring at all = problem
- High heap usage (>85%) cycling in sawtooth pattern
- High allocation rate (visible in F3: >500 MB/s)

**Fix:** See JVM Arguments section below.

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

### Tier 1 — Essential

| Mod | Fixes |
|-----|-------|
| Sodium | Rendering pipeline rewrite. Up to 300% FPS improvement |
| Lithium | Game logic optimization (physics, mob AI, block ticking) |
| FerriteCore | Memory optimization, dramatically reduces heap usage |

### Tier 2 — Major gains

| Mod | Fixes |
|-----|-------|
| ImmediatelyFast | Batches immediate-mode draw calls. Entity rendering 3.75x faster |
| EntityCulling | Skips rendering entities behind walls |
| Enhanced Block Entities | Converts block entity rendering to baked models |
| C2ME | Parallelizes chunk generation/loading |
| ModernFix | Memory leaks, dynamic model loading, launch speed |
| MoreCulling | Aggressive block face culling |

### Tier 3 — Supplementary

| Mod | Fixes |
|-----|-------|
| Nvidium | NVIDIA-only mesh shader rendering (incompatible with Iris) |
| Exordium | Renders HUD at lower framerate |
| Dynamic FPS | Reduces resources when in background |
| ThreadTweak | Thread scheduling improvements |

## Hardware Bottleneck Identification

### CPU-bound vs GPU-bound

| Indicator | CPU-bound | GPU-bound |
|-----------|-----------|-----------|
| F3 GPU% | Low (30-60%) | High (95%+) |
| `glfwSwapBuffers` time | Low | High (CPU waiting for GPU) |
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
| `/sparkc profiler start --alloc` | Profile memory allocations |
| `/sparkc profiler start --only-ticks-over 50` | Only profile slow ticks |
| `/sparkc gcmonitor` | Live GC monitoring |
| `/sparkc heapsummary` | Heap object breakdown |

## Known Software Conflicts

| Software | Issue |
|----------|-------|
| RivaTuner (RTSS) v7.3.3 or older | Extreme FPS drops with Sodium |
| ASUS GPU Tweak III | Injects into Java process, severe slowdown |
| OptiFine | Conflicts with Sodium, outdated rendering |
