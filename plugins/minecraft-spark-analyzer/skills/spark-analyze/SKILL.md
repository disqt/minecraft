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

1. **Identify the thread breakdown** — What percentage goes to rendering vs tick vs network vs idle?
2. **Find the top bottlenecks** — Which mods/methods consume the most time?
3. **Check for known bad patterns** — DH render-thread blocking, EMF/ETF overhead, GC issues, etc.
4. **Assess hardware constraints** — CPU-bound vs GPU-bound, RAM pressure, swap usage.

## Step 4: Present findings

Structure the report as:

```markdown
## Spark Profile Analysis: <player name>

**System:** <CPU> | <RAM used/total> | <OS> | <Java version> | <GC type> | <heap>
**Minecraft:** <MC version> | <loader + version> | <mod count> mods
**Profile duration:** <seconds>s | **Sampled thread:** <thread name>

### Health Summary

| Metric | Value | Status |
|--------|-------|--------|
| TPS | ... | OK/Warning/Bad |
| MSPT (median) | ... | OK/Warning/Bad |
| MSPT (max) | ... | OK/Warning/Bad |
| Heap usage | ... | OK/Warning/Bad |
| System RAM | ... | OK/Warning/Bad |
| GC pauses | ... | OK/Warning/Bad |

### Thread Breakdown

| Activity | % | Notes |
|----------|---|-------|
| Rendering | ... | ... |
| Client tick | ... | ... |
| Network | ... | ... |
| Idle/sleep | ... | ... |

### Top Bottlenecks

Ranked by impact, with:
- What's happening (the method/mod and what it does)
- Why it's a problem
- Specific fix recommendation

### Recommendations

Numbered list of actionable changes, ordered by expected impact:
1. **[Category]** Specific action — expected benefit
```

Categories for recommendations: `JVM Args`, `Video Settings`, `Mod Config`, `Add Mod`, `Remove Mod`, `Hardware`, `Server-side`.
