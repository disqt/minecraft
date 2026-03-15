#!/usr/bin/env python3
"""
Analyze a Spark profiler JSON export and produce a structured report.

Usage:
    python analyze_spark.py <path-to-json>
    python analyze_spark.py --fetch <spark-id>

The JSON should be the full export from:
    https://spark.lucko.me/<id>?raw=1&full=true
"""

import json
import sys
import os

def fetch_profile(spark_id: str, output_path: str) -> str:
    """Download a Spark profile JSON via curl."""
    import subprocess
    url = f"https://spark.lucko.me/{spark_id}?raw=1&full=true"
    result = subprocess.run(
        ["curl", "-sL", url],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        print(f"ERROR: curl failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result.stdout)
    return output_path


def extract_metadata(data: dict) -> dict:
    """Extract system info, performance metrics, and mod list from metadata."""
    meta = data.get("metadata", {})
    plat = meta.get("platform", {})
    stats = meta.get("platformStatistics", {})
    sys_stats = meta.get("systemStatistics", data.get("systemStatistics", {}))
    heap = stats.get("memory", {}).get("heap", {})
    tps = stats.get("tps", {})
    mspt_1m = stats.get("mspt", {}).get("last1m", {})
    mspt_5m = stats.get("mspt", {}).get("last5m", {})
    cpu = sys_stats.get("cpu", {})
    mem = sys_stats.get("memory", {})
    gc = sys_stats.get("gc", {})
    java = sys_stats.get("java", {})
    jvm = sys_stats.get("jvm", {})
    os_info = sys_stats.get("os", {})
    world = stats.get("world", {})

    physical = mem.get("physical", {})
    ram_used = physical.get("used", 0)
    ram_total = physical.get("total", 0)
    swap = mem.get("swap", {})

    start = meta.get("startTime", 0)
    end = meta.get("endTime", data.get("endTime", 0))
    duration_s = (end - start) / 1000 if end and start else 0

    # Entity counts sorted by count
    entity_counts = world.get("entityCounts", {})
    top_entities = sorted(entity_counts.items(), key=lambda x: -x[1])[:10]

    # Mod/plugin sources
    sources = meta.get("sources", data.get("sources", {}))
    mod_list = sorted(sources.keys())

    # GC info
    gc_info = []
    for name, info in gc.items():
        gc_info.append({
            "name": name,
            "total": info.get("total", 0),
            "avgTime": info.get("avgTime", 0),
            "avgFrequency": info.get("avgFrequency", 0),
        })

    # JVM args
    vm_args = java.get("vmArgs", [])

    return {
        "player": meta.get("user", {}).get("name", "Unknown"),
        "platform": f"{plat.get('name', '?')} {plat.get('version', '')}",
        "mc_version": plat.get("minecraftVersion", "?"),
        "spark_version": plat.get("sparkVersion", "?"),
        "duration_s": round(duration_s, 1),
        "ticks": meta.get("numberOfTicks", data.get("numberOfTicks", 0)),
        "cpu_model": cpu.get("modelName", "Unknown"),
        "cpu_threads": cpu.get("threads", 0),
        "cpu_process_1m": round(cpu.get("processUsage", {}).get("last1m", 0) * 100, 1),
        "cpu_system_1m": round(cpu.get("systemUsage", {}).get("last1m", 0) * 100, 1),
        "ram_used_gb": round(ram_used / 1024**3, 1),
        "ram_total_gb": round(ram_total / 1024**3, 1),
        "ram_pct": round(ram_used * 100 / ram_total, 1) if ram_total else 0,
        "swap_used_gb": round(swap.get("used", 0) / 1024**3, 1),
        "swap_total_gb": round(swap.get("total", 0) / 1024**3, 1),
        "heap_used_mb": round(heap.get("used", 0) / 1024**2),
        "heap_max_mb": round(heap.get("max", 0) / 1024**2),
        "heap_pct": round(heap.get("used", 0) * 100 / heap.get("max", 1)),
        "tps_1m": round(tps.get("last1m", 0), 1),
        "tps_5m": round(tps.get("last5m", 0), 1),
        "tps_15m": round(tps.get("last15m", 0), 1),
        "mspt_mean_1m": round(mspt_1m.get("mean", 0), 1),
        "mspt_median_1m": round(mspt_1m.get("median", 0), 1),
        "mspt_p95_1m": round(mspt_1m.get("percentile95", 0), 1),
        "mspt_max_1m": round(mspt_1m.get("max", 0), 1),
        "mspt_max_5m": round(mspt_5m.get("max", 0), 1),
        "total_entities": world.get("totalEntities", 0),
        "top_entities": top_entities,
        "gc": gc_info,
        "jvm_args": vm_args,
        "java_version": f"{java.get('vendor', '')} {java.get('version', '')}",
        "os": f"{os_info.get('name', '')} {os_info.get('version', '')}",
        "mod_count": len(mod_list),
        "mods": mod_list,
    }


def compute_hotspots(data: dict, top_n: int = 20) -> tuple:
    """
    Walk the thread trees and compute self-time for each node.
    Returns (hotspots_by_method, hotspots_by_mod, thread_breakdown).
    """
    threads = data.get("threads", [])
    class_sources = data.get("classSources", {})
    time_windows = data.get("timeWindows", [])

    all_nodes = []  # (self_samples, total_samples, className, methodName, mod)
    thread_totals = {}  # thread_name -> total_samples

    for thread in threads:
        thread_name = thread.get("name", "Unknown")
        children = thread.get("children", [])
        if not children:
            continue

        # Compute total samples for this thread
        thread_times = thread.get("times", [])
        thread_total = sum(thread_times)
        thread_totals[thread_name] = thread_total

        # Build parent -> children mapping from childrenRefs
        # Each node's total = sum(times), self = total - sum(children totals)
        node_totals = {}  # index -> total samples
        node_child_indices = {}  # index -> list of child indices

        for i, node in enumerate(children):
            times = node.get("times", [])
            node_totals[i] = sum(times)
            node_child_indices[i] = node.get("childrenRefs", [])

        for i, node in enumerate(children):
            total = node_totals[i]
            children_total = sum(node_totals.get(ci, 0) for ci in node_child_indices[i])
            self_time = total - children_total

            if self_time <= 0:
                continue

            class_name = node.get("className", "")
            method_name = node.get("methodName", "")

            # Attribute to mod via classSources
            mod = class_sources.get(class_name, "")
            if not mod:
                # Try common prefixes
                if "lwjgl" in class_name.lower() or "opengl" in class_name.lower():
                    mod = "lwjgl"
                elif "net.minecraft" in class_name or class_name.startswith("class_"):
                    mod = "minecraft"
                elif "java." in class_name or "jdk." in class_name or "sun." in class_name:
                    mod = "java-runtime"
                elif "it.unimi" in class_name:
                    mod = "fastutil"
                elif "org.tukaani" in class_name:
                    mod = "xz-compression"
                elif "org.sqlite" in class_name:
                    mod = "sqlite"

            all_nodes.append((self_time, total, class_name, method_name, mod))

    # Sort by self-time descending
    all_nodes.sort(key=lambda x: -x[0])

    # Total samples across all threads
    grand_total = sum(thread_totals.values()) or 1

    # Top methods
    top_methods = []
    for self_time, total, class_name, method_name, mod in all_nodes[:top_n]:
        top_methods.append({
            "self_pct": round(self_time * 100 / grand_total, 2),
            "total_pct": round(total * 100 / grand_total, 2),
            "self_samples": self_time,
            "class": class_name,
            "method": method_name,
            "mod": mod or "unknown",
        })

    # Aggregate by mod
    mod_totals = {}
    for self_time, total, class_name, method_name, mod in all_nodes:
        mod = mod or "unknown"
        mod_totals[mod] = mod_totals.get(mod, 0) + self_time

    mod_ranking = sorted(mod_totals.items(), key=lambda x: -x[1])
    top_mods = []
    for mod, self_total in mod_ranking[:15]:
        top_mods.append({
            "mod": mod,
            "self_pct": round(self_total * 100 / grand_total, 2),
            "self_samples": self_total,
        })

    return top_methods, top_mods, thread_totals, grand_total


def print_report(metadata: dict, top_methods: list, top_mods: list,
                 thread_totals: dict, grand_total: int):
    """Print a structured text report."""
    m = metadata

    print(f"# Spark Profile Analysis: {m['player']}")
    print()
    print(f"**System:** {m['cpu_model']} ({m['cpu_threads']}T) | "
          f"{m['ram_used_gb']}/{m['ram_total_gb']} GB RAM ({m['ram_pct']}%) | "
          f"{m['os']}")
    print(f"**Java:** {m['java_version']} | Heap: {m['heap_used_mb']}/{m['heap_max_mb']} MB ({m['heap_pct']}%)")
    print(f"**Minecraft:** {m['mc_version']} | {m['platform']} | {m['mod_count']} mods")
    print(f"**Profile:** {m['duration_s']}s | {m['ticks']} ticks")
    print()

    # Health metrics
    print("## Health Summary")
    print()
    print("| Metric | Value | Status |")
    print("|--------|-------|--------|")

    def status(val, warn, bad, higher_is_worse=True):
        if higher_is_worse:
            return "BAD" if val >= bad else ("WARN" if val >= warn else "OK")
        else:
            return "BAD" if val <= bad else ("WARN" if val <= warn else "OK")

    print(f"| TPS (1m) | {m['tps_1m']} | {status(m['tps_1m'], 19.5, 19.0, False)} |")
    print(f"| MSPT median (1m) | {m['mspt_median_1m']}ms | {status(m['mspt_median_1m'], 30, 45)} |")
    print(f"| MSPT max (5m) | {m['mspt_max_5m']}ms | {status(m['mspt_max_5m'], 50, 100)} |")
    print(f"| Heap | {m['heap_pct']}% | {status(m['heap_pct'], 80, 90)} |")
    print(f"| System RAM | {m['ram_pct']}% | {status(m['ram_pct'], 80, 90)} |")
    if m['swap_used_gb'] > 0.5:
        print(f"| Swap | {m['swap_used_gb']} GB active | BAD |")

    # GC
    for gc in m['gc']:
        if 'major' in gc['name'].lower() or 'old' in gc['name'].lower():
            print(f"| GC ({gc['name']}) | avg {gc['avgTime']:.0f}ms, every {gc['avgFrequency']/1000:.0f}s | "
                  f"{status(gc['avgTime'], 500, 2000)} |")
    print()

    # Entities
    if m['total_entities'] > 0:
        print(f"**Entities:** {m['total_entities']} total | Top: ", end="")
        print(", ".join(f"{name.replace('minecraft:','')}({count})" for name, count in m['top_entities'][:5]))
        print()

    # JVM args of interest
    gc_type = "Unknown"
    for arg in m['jvm_args']:
        if 'UseZGC' in arg: gc_type = "ZGC"
        elif 'UseG1GC' in arg: gc_type = "G1GC"
        elif 'UseShenandoahGC' in arg: gc_type = "Shenandoah"
    heap_args = [a for a in m['jvm_args'] if a.startswith('-Xm')]
    print(f"**GC:** {gc_type} | **Heap args:** {' '.join(heap_args)}")
    print()

    # Thread breakdown
    print("## Thread Breakdown")
    print()
    print("| Thread | Samples | % |")
    print("|--------|---------|---|")
    for name, total in sorted(thread_totals.items(), key=lambda x: -x[1]):
        print(f"| {name} | {total:,} | {total*100/grand_total:.1f}% |")
    print()

    # Top methods
    print("## Top Methods by Self-Time")
    print()
    print("| # | Self% | Mod | Method |")
    print("|---|-------|-----|--------|")
    for i, m in enumerate(top_methods, 1):
        class_short = m['class'].split('.')[-1]
        print(f"| {i} | {m['self_pct']}% | {m['mod']} | `{class_short}.{m['method']}` |")
    print()

    # Top mods
    print("## Top Mods by Aggregate Self-Time")
    print()
    print("| # | Self% | Mod |")
    print("|---|-------|-----|")
    for i, m in enumerate(top_mods, 1):
        print(f"| {i} | {m['self_pct']}% | {m['mod']} |")
    print()

    # Mod list
    print("## Loaded Mods")
    print()
    print(", ".join(metadata['mods']))
    print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--fetch":
        if len(sys.argv) < 3:
            print("Usage: analyze_spark.py --fetch <spark-id>")
            sys.exit(1)
        spark_id = sys.argv[2]
        json_path = f"/tmp/spark-{spark_id}.json"
        print(f"Fetching profile {spark_id}...", file=sys.stderr)
        fetch_profile(spark_id, json_path)
    else:
        json_path = sys.argv[1]

    if not os.path.exists(json_path):
        print(f"ERROR: File not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    file_size = os.path.getsize(json_path)
    print(f"Loading {json_path} ({file_size/1024/1024:.1f} MB)...", file=sys.stderr)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    metadata = extract_metadata(data)
    top_methods, top_mods, thread_totals, grand_total = compute_hotspots(data)
    print_report(metadata, top_methods, top_mods, thread_totals, grand_total)


if __name__ == "__main__":
    main()
