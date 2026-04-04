#!/usr/bin/env python3
"""Modpack Release Tool -- zip, upload, changelog, publish."""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DEFAULT_CONFIG = SCRIPT_DIR / "modpack-release.json"


def load_config(path: Path) -> dict:
    return json.loads(path.read_text())


def parse_args():
    parser = argparse.ArgumentParser(description="Release a Prism Launcher modpack version")
    parser.add_argument("instance_path", type=Path, help="Path to Prism instance directory")
    parser.add_argument("--version", required=True, help="Version to publish (e.g. 2.10)")
    parser.add_argument("--keep", type=int, help="Versions to retain on VPS (default: from config)")
    parser.add_argument("--no-notify", action="store_true", help="Skip Discord notification")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without executing")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Config file path")
    return parser.parse_args()


def validate_instance(instance_path: Path):
    """Check that the path looks like a valid Prism instance."""
    if not instance_path.is_dir():
        sys.exit(f"Error: {instance_path} is not a directory")
    if not (instance_path / "mmc-pack.json").exists():
        sys.exit(f"Error: {instance_path}/mmc-pack.json not found (not a Prism instance?)")
    mods_dir = instance_path / ".minecraft" / "mods"
    if not mods_dir.is_dir():
        sys.exit(f"Error: {mods_dir} not found")


def load_packignore(instance_path: Path) -> list[str]:
    """Read .packignore patterns (one per line, relative to instance root)."""
    packignore = instance_path / ".packignore"
    if not packignore.exists():
        return []
    return [line.strip() for line in packignore.read_text().splitlines() if line.strip()]


def should_exclude(rel_path: str, ignore_patterns: list[str]) -> bool:
    """Check if a relative path matches any .packignore pattern."""
    for pattern in ignore_patterns:
        normalized = pattern.replace("\\", "/")
        if rel_path.startswith(normalized) or rel_path.startswith(normalized + "/"):
            return True
    return False


def zip_instance(instance_path: Path, output_path: Path, root_name: str) -> int:
    """Zip the instance directory, respecting .packignore.
    Returns the zip file size in bytes.
    """
    ignore_patterns = load_packignore(instance_path)
    ignore_patterns.extend([
        ".minecraft/logs",
        ".minecraft/crash-reports",
    ])

    print("Zipping instance...")
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(instance_path.rglob("*")):
            if file_path.is_dir():
                continue
            rel = file_path.relative_to(instance_path).as_posix()
            if should_exclude(rel, ignore_patterns):
                continue
            arcname = f"{root_name}/{rel}"
            zf.write(file_path, arcname)

    size = output_path.stat().st_size
    size_mb = size / (1024 * 1024)
    print(f"  Created {output_path.name} ({size_mb:.0f} MB)")
    return size


def main():
    args = parse_args()
    config = load_config(args.config)
    validate_instance(args.instance_path)

    mc_version = config["mc_version"]
    version = args.version
    filename = f"{mc_version} v{version}.zip"
    keep = args.keep or config.get("keep", 3)

    print(f"Modpack Release: {mc_version} v{version}")
    print("=" * 50)
    print(f"  Instance: {args.instance_path}")
    print(f"  Filename: {filename}")
    print(f"  VPS:      {config['vps_host']}:{config['vps_path']}")
    print()

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / filename
        zip_size = zip_instance(args.instance_path, zip_path, f"{mc_version} v{version}")
        size_str = f"{zip_size / (1024 * 1024):.0f} MB"
        print()

        if args.dry_run:
            print("[dry-run] Would upload, update manifest, and notify.")
            return

        # Steps continue in next tasks...


if __name__ == "__main__":
    main()
