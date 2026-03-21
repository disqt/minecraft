#!/usr/bin/env python3
"""World migration trim tool — download, analyze, and trim Minecraft world chunks."""

import argparse
import sys
from pathlib import Path

# Allow running as `python migrate.py` from within world-migration-cli/
# or `python world-migration-cli/migrate.py` from repo root
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse and validate command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze and trim low-activity Minecraft world chunks.",
    )

    # Source: local world path OR SSH host + remote path
    parser.add_argument(
        "world_path", nargs="?", default=None,
        help="Local world directory path",
    )
    parser.add_argument("--host", default=None, help="SSH host (uses ~/.ssh/config)")
    parser.add_argument("--remote-path", default=None, help="Remote world directory path")

    # Dimensions
    parser.add_argument(
        "--dimensions", nargs="+", default=None,
        choices=["overworld", "nether", "end"],
        help="Dimensions to process (default: auto-detect)",
    )

    # Query mode: threshold shorthand OR raw query string (mutually exclusive)
    query_group = parser.add_mutually_exclusive_group()
    query_group.add_argument(
        "--threshold", type=int, default=None,
        help="InhabitedTime threshold in ticks",
    )
    query_group.add_argument(
        "--query", default=None,
        help="MCA Selector query string",
    )

    # Tool and output paths
    parser.add_argument("--mcaselector", default=None, help="Path to MCA Selector JAR")
    parser.add_argument("--html", default=None, help="HTML output path")
    parser.add_argument("--raw", default=None, help="Raw binary output path")

    # Safety / execution flags
    parser.add_argument(
        "--dangerously-perform-the-trim", action="store_true",
        help="Actually delete chunks (default: analyze only)",
    )
    parser.add_argument(
        "--safety-pct", type=int, default=90,
        help="Abort if deletion exceeds this %% per dimension (default: 90)",
    )
    parser.add_argument("--force", action="store_true", help="Override safety abort")

    args = parser.parse_args(argv)

    # --- Validation ---

    # Rule 1: exactly one of local path or SSH pair
    has_local = args.world_path is not None
    has_ssh = args.host is not None or args.remote_path is not None

    if has_local and has_ssh:
        parser.error("Specify either <world-path> or --host/--remote-path, not both.")
    if not has_local and not has_ssh:
        parser.error("Specify either <world-path> or --host + --remote-path.")
    if has_ssh and (args.host is None or args.remote_path is None):
        parser.error("--host and --remote-path must be used together.")

    # Rule 2: --threshold and --query are mutually exclusive (handled by argparse group above)

    # Rule 3: --query requires --mcaselector
    if args.query is not None and args.mcaselector is None:
        parser.error("--query requires --mcaselector.")

    # Rule 4: default threshold when neither is specified
    if args.threshold is None and args.query is None:
        args.threshold = 120

    return args


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

DIMENSION_LABELS = {"overworld": "Overworld", "nether": "Nether", "end": "End"}


def _trim_pure_python(dimensions, layout, dims):
    """Zero location+timestamp header entries for chunks marked for deletion.

    If all 1024 entries in a region file become zero, delete the .mca file.
    """
    import struct
    from collections import defaultdict

    for dim in dims:
        region_dir = layout.region_dir(dim)
        if region_dir is None:
            continue
        grid = dimensions[dim]["grid"]
        # Index chunks by region coords for O(1) lookup per region file
        by_region = defaultdict(list)
        for (cx, cz), v in grid.items():
            if v["delete"]:
                by_region[(cx // 32, cz // 32)].append((cx, cz))

        for mca_file in region_dir.glob("r.*.*.mca"):
            parts = mca_file.stem.split(".")
            region_x, region_z = int(parts[1]), int(parts[2])
            region_chunks = by_region.get((region_x, region_z))
            if not region_chunks:
                continue
            data = bytearray(mca_file.read_bytes())
            modified = False
            for cx, cz in region_chunks:
                local_x = cx % 32
                local_z = cz % 32
                slot = local_z * 32 + local_x
                loc_offset = slot * 4
                ts_offset = 4096 + slot * 4
                data[loc_offset:loc_offset + 4] = b"\x00\x00\x00\x00"
                data[ts_offset:ts_offset + 4] = b"\x00\x00\x00\x00"
                modified = True
            if modified:
                all_zero = all(
                    struct.unpack_from(">I", data, i * 4)[0] == 0
                    for i in range(1024)
                )
                if all_zero:
                    mca_file.unlink()
                else:
                    mca_file.write_bytes(bytes(data))


def _trim_mcaselector(args, world_path, dims):
    """Delete chunks via MCA Selector for each dimension."""
    from migrate_mca import build_delete_command, run_mcaselector

    for dim in dims:
        delete_cmd = build_delete_command(
            mcaselector_jar=Path(args.mcaselector),
            world_dir=world_path,
            dimension=dim,
            query=args.query,
        )
        run_mcaselector(delete_cmd, f"Trimming {DIMENSION_LABELS[dim]}")


def run_pipeline(args) -> int:
    """Execute the full migration pipeline and return an exit code.

    Exit codes:
        0 — success
        1 — safety abort (outputs still generated)
        2 — dependency / environment error
    """
    from migrate_regions import analyze_dimension, count_chunks_in_directory
    from migrate_remote import (
        detect_local_layout,
        detect_remote_layout,
        download_world,
    )
    from migrate_display import (
        format_stats_table,
        format_safety_abort,
        format_report,
    )
    from migrate_html import generate_html_file
    from migrate_raw import generate_raw_file

    # ------------------------------------------------------------------
    # 1. Resolve world
    # ------------------------------------------------------------------
    if args.host:
        # SSH mode: detect remote layout, download, re-detect locally
        layout = detect_remote_layout(args.host, args.remote_path)
        dims = args.dimensions or layout.available_dimensions(check_filesystem=False)
        if not dims:
            print("ERROR: No dimensions found on remote server.", file=sys.stderr)
            return 2

        world_path = Path(args.remote_path).name
        local_world = Path("worlds") / world_path
        local_world.mkdir(parents=True, exist_ok=True)

        print(f"Downloading {', '.join(dims)} from {args.host}...", file=sys.stderr)
        download_world(args.host, layout, local_world, args.remote_path)

        # Re-detect locally after download
        layout = detect_local_layout(local_world)
        world_path = local_world
    else:
        world_path = Path(args.world_path)
        layout = detect_local_layout(world_path)

    # ------------------------------------------------------------------
    # 2. Determine dimensions
    # ------------------------------------------------------------------
    dims = args.dimensions or layout.available_dimensions()
    if not dims:
        print("ERROR: No dimensions found in world directory.", file=sys.stderr)
        return 2

    # ------------------------------------------------------------------
    # 3. Analyze
    # ------------------------------------------------------------------
    query_str = args.query or f"InhabitedTime < {args.threshold}"
    dimensions: dict = {}

    for dim in dims:
        region_dir = layout.region_dir(dim)
        if region_dir is None:
            continue

        if args.threshold is not None:
            # Pure Python analysis
            stats, grid = analyze_dimension(region_dir, args.threshold)
        else:
            # MCA Selector query mode
            import tempfile
            from migrate_mca import (
                build_select_command,
                run_mcaselector,
                count_selected_chunks,
            )

            total = count_chunks_in_directory(region_dir)
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
                csv_path = Path(tmp.name)

            try:
                select_cmd = build_select_command(
                    mcaselector_jar=Path(args.mcaselector),
                    world_dir=world_path,
                    dimension=dim,
                    query=args.query,
                    output_csv=csv_path,
                )
                run_mcaselector(select_cmd, f"Selecting {DIMENSION_LABELS[dim]}")
                delete_count = count_selected_chunks(csv_path)
            finally:
                csv_path.unlink(missing_ok=True)

            stats = {
                "total": total,
                "delete": delete_count,
                "keep": total - delete_count,
            }
            grid = {}  # MCA Selector mode: no per-chunk grid data

        dimensions[dim] = {"stats": stats, "grid": grid}

    # ------------------------------------------------------------------
    # 4. Print stats
    # ------------------------------------------------------------------
    stats_list = []
    for dim in dims:
        if dim not in dimensions:
            continue
        s = dict(dimensions[dim]["stats"])
        s["dimension"] = DIMENSION_LABELS[dim]
        stats_list.append(s)

    print(format_stats_table(stats_list), file=sys.stderr)

    # ------------------------------------------------------------------
    # 5. Generate outputs
    # ------------------------------------------------------------------
    if args.html:
        generate_html_file(dimensions, query_str, Path(args.html))
        print(f"\nHTML preview: {args.html}", file=sys.stderr)

    if args.raw:
        generate_raw_file(dimensions, query_str, Path(args.raw))
        print(f"Raw output: {args.raw}", file=sys.stderr)

    # ------------------------------------------------------------------
    # 6. Safety check + trim
    # ------------------------------------------------------------------
    if args.dangerously_perform_the_trim:
        # Safety check: per-dimension deletion percentage
        for dim in dims:
            if dim not in dimensions:
                continue
            s = dimensions[dim]["stats"]
            if s["total"] == 0:
                continue
            pct = s["delete"] / s["total"] * 100
            if pct > args.safety_pct and not args.force:
                print(
                    "\n" + format_safety_abort(DIMENSION_LABELS[dim], pct),
                    file=sys.stderr,
                )
                return 1

        # Perform trim
        if args.query and args.mcaselector:
            _trim_mcaselector(args, world_path, dims)
        else:
            _trim_pure_python(dimensions, layout, dims)

        print(
            "\n" + format_report(stats_list, str(world_path), dims),
            file=sys.stderr,
        )

    return 0


def main():
    args = parse_args()
    code = run_pipeline(args)
    sys.exit(code)


if __name__ == "__main__":
    main()
