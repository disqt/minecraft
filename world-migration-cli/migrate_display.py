"""Output formatting — stats table, report, prompts."""


def format_stats_table(stats: list[dict]) -> str:
    """Format dimension stats as an aligned table.

    Each stats dict has: dimension, total, delete, keep.
    """
    header = f"{'Dimension':<15} {'Total':>8} {'Delete':>8} {'Keep':>8} {'Delete %':>10}"
    separator = "\u2500" * len(header)

    lines = [header, separator]
    agg_total = 0
    agg_delete = 0

    for s in stats:
        total = s["total"]
        delete = s["delete"]
        keep = s["keep"]
        pct = (delete / total * 100) if total > 0 else 0.0
        lines.append(
            f"{s['dimension']:<15} {total:>8,} {delete:>8,} {keep:>8,} {pct:>9.1f}%"
        )
        agg_total += total
        agg_delete += delete

    if len(stats) > 1:
        agg_keep = agg_total - agg_delete
        agg_pct = (agg_delete / agg_total * 100) if agg_total > 0 else 0.0
        lines.append(separator)
        lines.append(
            f"{'Total':<15} {agg_total:>8,} {agg_delete:>8,} {agg_keep:>8,} {agg_pct:>9.1f}%"
        )

    return "\n".join(lines)


def format_report(
    stats: list[dict],
    world_path: str,
    dimensions: list[str],
) -> str:
    """Format the post-trim report with next steps."""
    lines = ["Trim complete."]
    for s in stats:
        lines.append(f"  {s['dimension']}: deleted {s['delete']:,} chunks")

    lines.append(f"\nTrimmed world at: {world_path}/")
    lines.append("\nNext steps:")
    lines.append("  1. (Optional) Open in MCA Selector GUI to visually verify")
    lines.append("  2. Stop the Minecraft server")
    lines.append("  3. Back up the current world on the server")
    lines.append("  4. Delete server region dirs and upload trimmed ones")
    lines.append("  5. Start the server")
    lines.append("  6. Run Chunky pre-generation for the trimmed areas")
    lines.append("  7. Purge and re-render BlueMap")

    return "\n".join(lines)


def format_safety_abort(dimension: str, pct: float) -> str:
    """Format the safety abort message."""
    return (
        f"SAFETY ABORT: Would delete {pct:.1f}% of {dimension} chunks "
        f"\u2014 this looks wrong.\n"
        f"Use --force to override, or adjust --threshold / --query."
    )
