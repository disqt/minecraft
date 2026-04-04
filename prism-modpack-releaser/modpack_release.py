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

    # Steps follow in subsequent tasks...


if __name__ == "__main__":
    main()
