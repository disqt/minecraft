"""MCA Selector CLI wrapper — build and run select/delete commands."""

import subprocess
import sys
from pathlib import Path

from migrate_remote import dimension_region_subpath


def _base_command(
    mcaselector_jar: Path,
    world_dir: Path,
    dimension: str,
    mode: str,
    query: str,
) -> list[str]:
    """Build the base MCA Selector command with common flags."""
    cmd = [
        "java", "-jar", str(mcaselector_jar),
        "--mode", mode,
        "--world", str(world_dir),
        "--query", query,
    ]
    if dimension != "overworld":
        region_path = world_dir / dimension_region_subpath(dimension)
        cmd.extend(["--region", str(region_path)])
    return cmd


def build_select_command(
    mcaselector_jar: Path,
    world_dir: Path,
    dimension: str,
    query: str,
    output_csv: Path,
) -> list[str]:
    """Build MCA Selector --mode select command."""
    cmd = _base_command(mcaselector_jar, world_dir, dimension, "select", query)
    cmd.extend(["--output", str(output_csv)])
    return cmd


def build_delete_command(
    mcaselector_jar: Path,
    world_dir: Path,
    dimension: str,
    query: str,
) -> list[str]:
    """Build MCA Selector --mode delete command."""
    return _base_command(mcaselector_jar, world_dir, dimension, "delete", query)


def run_mcaselector(cmd: list[str], description: str) -> None:
    """Execute an MCA Selector command, exit on failure."""
    print(f"  {description}...", file=sys.stderr)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(
            f"ERROR: MCA Selector failed: {result.stderr}",
            file=sys.stderr,
        )
        sys.exit(3)


def count_selected_chunks(csv_path: Path) -> int:
    """Count chunks in a MCA Selector selection CSV (one x;z pair per line)."""
    if not csv_path.exists():
        return 0
    text = csv_path.read_text().strip()
    if not text:
        return 0
    return len(text.splitlines())
