---
name: spark-analyze
description: Use when a player sends a spark.lucko.me profiler link and you need to diagnose FPS or TPS issues. Also use when the user asks about Minecraft performance problems, lag, stuttering, low FPS, or wants to analyze a Spark profile.
---

# Spark Profile Analyzer

Fetches a Spark profiler report via JSON API, identifies performance bottlenecks, and produces actionable recommendations (settings, mods, JVM args, hardware notes).

## Inputs

The user provides a `spark.lucko.me/<id>` URL. Extract the profile ID from the URL.

## Step 1: Fetch metadata

Fetch the lightweight metadata first to understand the system and check for obvious issues before pulling the full thread data.

```
https://spark.lucko.me/<id>?raw=1
```

Use `WebFetch` with the prompt: "Return the complete JSON response exactly as-is, do not summarize."

From the metadata, extract and note:

| Field | Path |
|-------|------|
| Platform | `metadata.platform` (Fabric/Paper/etc, MC version, Spark version) |
| User | `metadata.user.name` |
| Duration | `(endTime - metadata.startTime) / 1000` seconds |
| Heap | `metadata.platformStatistics.memory.heap` (used/max) |
| TPS | `metadata.platformStatistics.tps` (1m/5m/15m) |
| MSPT | `metadata.platformStatistics.mspt` (mean/median/p95/max for 1m and 5m) |
| Entities | `metadata.platformStatistics.world` (total + top counts) |
| CPU | `metadata.systemStatistics.cpu` (model, threads, process/system usage) |
| RAM | `metadata.systemStatistics.memory.physical` (used/total) |
| GC | `metadata.systemStatistics.gc` (collector name, avg time, avg frequency) |
| JVM args | `metadata.systemStatistics.java.vmArgs` |
| Java | `metadata.systemStatistics.java` (vendor, version) |
| OS | `metadata.systemStatistics.os` |
| Mods/plugins | `metadata.sources` (map of mod name to metadata) |

**Quick health check from metadata alone:**

- **TPS below 19:** Server-side issue. Check MSPT for severity.
- **MSPT p95 above 40ms:** Tick spikes causing stuttering.
- **Heap usage above 85%:** Memory pressure, likely GC issues.
- **Physical RAM above 85%:** System-wide memory pressure, swapping.
- **GC major cycle avg time above 500ms:** GC tuning needed.
- **ZGC or G1GC on client:** Check JVM args against recommendations in `references/diagnosis-patterns.md`.
- **Swap on Windows:** Spark reports Windows page file *allocated* size, not actual usage. Do NOT flag swap as a problem on Windows based on Spark data alone -- it's almost always a false alarm. Only flag if there are correlated symptoms (MSPT spikes, GC issues, or OS = Linux/macOS where swap reporting is accurate).

## Step 2: Run the analysis script

A bundled Python script handles fetching the full profile (including thread data), parsing the call tree, computing self-time per method, attributing CPU time to mods via `classSources`, and producing a structured report.

```bash
python3 <skill-dir>/scripts/analyze_spark.py --fetch <spark-id>
```

Resolve `<skill-dir>` relative to this SKILL.md's directory. The script:
- Fetches the full JSON (5-30MB) from `spark.lucko.me/<id>?raw=1&full=true`
- Extracts system info, TPS, MSPT, heap, RAM, GC, JVM args, entities, mod list
- Walks the thread call trees and computes self-time per node (total samples minus children's samples)
- Groups self-time by source mod using the `classSources` map
- Outputs: health summary, thread breakdown, top 20 methods, top 15 mods, loaded mod list

Read the script output carefully -- it provides the raw data. Your job is to interpret it and add the diagnosis and recommendations (Steps 3 and 4).

## Step 3: Diagnose

Read `references/diagnosis-patterns.md` for the full pattern catalog. Cross-reference the hotspot data against known patterns:

1. **Identify the thread breakdown** -- What percentage goes to rendering vs tick vs network vs idle?
2. **Find the top bottlenecks** -- Which mods/methods consume the most time?
3. **Check for known bad patterns** -- DH render-thread blocking, EMF/ETF overhead, GC issues, etc.
4. **Assess hardware constraints** -- CPU-bound vs GPU-bound, RAM pressure, swap usage.
5. **Check JVM args** -- Compare against recommended flags for client vs server.
6. **Consider what the profile does NOT show** -- Spark samples CPU time, not I/O waits or GPU time. High LWJGL% means GPU-bound. Missing time may indicate GC pauses or I/O stalls.

**Important analysis principles:**

- **Self-time vs total-time:** Self-time is the time spent in a method's own code. Total-time includes all child calls. A method with 60% total-time but 0.05% self-time is NOT the bottleneck -- the problem is deeper in its call chain. Always look at self-time to find the actual hot code.
- **Percentages vs absolute time:** Always consider the tick duration when reading percentages. 80% of a 3.9ms tick is harmless (~3.1ms). 30% of a 200ms spike tick is a crisis (~60ms). Include estimated absolute times in the report.
- **Mod attribution caveat:** The Sources/Plugins view "blames" the mod that triggers an action for all downstream cost. If a mod activates a lever that triggers expensive redstone, the mod gets blamed for the redstone time. Always drill deeper to check whether the slowness is the mod's own code or downstream vanilla/other-mod processing.
- **Sampling limitations:** Spark measures duration, not frequency. Thousands of individually cheap operations (item checks, hopper scans) collectively cause lag through sheer repetition, but each call looks insignificant. Note this when relevant.

## Step 4: Present findings

Structure the report as:

```markdown
## Spark Profile Analysis: <player name>

**System:** <CPU> | <RAM used/total> | <OS> | <Java version> | <GC type> | <heap>
**Minecraft:** <MC version> | <loader + version> | <mod count> mods
**Profile duration:** <seconds>s | **Sampled thread:** <thread name>

**Interactive viewer:** https://spark.lucko.me/<id>
Use the viewer to explore the flame graph, bookmark methods (Alt+click), switch between All/Flat/Sources views, and toggle between percentage and millisecond display.

### Health Summary

| Metric | Value | Absolute Time | Status |
|--------|-------|---------------|--------|
| TPS | ... | -- | OK/Warning/Bad |
| MSPT (median) | ... | ...ms per tick | OK/Warning/Bad |
| MSPT (max) | ... | ...ms for a single tick | OK/Warning/Bad |
| Heap usage | ... | -- | OK/Warning/Bad |
| System RAM | ... | -- | OK/Warning/Bad |
| GC pauses | ... | -- | OK/Warning/Bad |

> Context note on what the percentages mean in absolute time for this profile.

### Thread Breakdown

| Activity | % | Est. time per tick | Notes |
|----------|---|--------------------|-------|
| Rendering | ... | ...ms | ... |
| Client tick | ... | ...ms | ... |
| Network | ... | ...ms | ... |
| Idle/sleep | ... | ...ms | ... |

> Note: mod attribution in the Sources view may overstate a mod's direct cost if it triggers downstream vanilla processing. Drill into the viewer's Sources tab to verify.

### Top Bottlenecks

Ranked by impact, with:
- What's happening (the method/mod and what it does)
- Why it's a problem
- Specific fix recommendation

### Recommendations

Split into three sections:

#### Immediate fixes (high impact)
Numbered list of critical changes, ordered by expected impact:
1. **[Category]** Specific action -- expected benefit

#### Performance tuning (medium impact)
Numbered list of tuning changes:
1. **[Category]** Specific action -- expected benefit

#### Further diagnosis
Numbered list of follow-up profiling steps to investigate root causes:
1. **[Diagnosis]** Specific command/tool -- what it reveals

### Current JVM Args

Show the full JVM args block with inline annotations for any changes needed. This helps the user copy-paste corrected args.
```

Categories for recommendations: `JVM Args`, `Video Settings`, `Mod Config`, `Add Mod`, `Remove Mod`, `Hardware`, `Server-side`, `System`, `Diagnosis`.

### Diagnosis recommendations to always consider including

Include whichever of these are relevant to the profile:

1. **Spike-only profiling** -- If the profile shows MSPT spikes (max >> median), recommend:
   ```
   /sparkc profiler --only-ticks-over 100 --timeout 180
   ```
   This filters normal ticks and only captures spike data, making the cause much clearer. The threshold should be between 50ms and the actual spike duration. This is the #1 technique for intermittent lag.

2. **Tick monitoring** -- For ongoing spike diagnosis:
   ```
   /sparkc tickmonitor --threshold-tick 50
   ```
   Alerts in chat when ticks exceed the threshold, helping correlate spikes with gameplay events.

3. **Background profiler** -- Recommend enabling in `config/spark/config.json`:
   ```json
   { "backgroundProfiler": true }
   ```
   Then use `/sparkc profiler open` at any time to get a live view of the last hour. No need to reproduce the issue.

4. **GC monitoring** -- If GC is suspected:
   ```
   /sparkc gcmonitor
   ```
   Cross-reference with tick monitor output. If spikes always coincide with GC events, the issue is memory pressure, not code. Use `/sparkc tickmonitor --without-gc` to separate GC-caused spikes from code-caused spikes.

5. **Heap analysis** -- If memory is high:
   ```
   /sparkc heapsummary
   ```
   Shows which classes consume the most heap. Look for unexpected accumulation.

6. **Allocation profiling** -- To find what creates the most objects:
   ```
   /sparkc profiler start --alloc
   ```
   Note: requires the async-profiler engine (Linux/macOS only). On Windows, use `/sparkc heapsummary` instead.

7. **Birdflop analyzer** -- Recommend pasting the profile URL into https://www.birdflop.com/resources/sparkprofile/ for automated config-level recommendations. Caveat: its suggestions are guidelines, not magic values.
