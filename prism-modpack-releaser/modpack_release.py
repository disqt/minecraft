#!/usr/bin/env python3
"""Modpack Release Tool -- zip, upload, changelog, publish."""

import argparse
import json
import re
import shlex
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
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
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
    if not ignore_patterns:
        print("  Warning: no .packignore found, zipping everything")
    print("Zipping instance...")
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in instance_path.rglob("*"):
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


def ssh_cmd(host: str, cmd: str) -> str:
    """Run a command on the VPS via SSH and return stdout."""
    result = subprocess.run(
        ["ssh", host, cmd],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"SSH command failed: {cmd}\n{result.stderr}")
    return result.stdout


def get_previous_zip_contents(config: dict) -> tuple[set[str], set[str]]:
    """Get mod jar names and config paths from the latest version on VPS.
    Returns (mod_jars, config_paths). Single SSH round-trip for manifest + unzip.
    """
    host = config["vps_host"]
    vps_path = config["vps_path"]
    try:
        manifest_raw = ssh_cmd(host, f"cat {vps_path}/manifest.json")
        manifest = json.loads(manifest_raw)
    except Exception:
        return set(), set()
    if not manifest.get("latest"):
        return set(), set()
    prev_file = manifest["latest"]["file"]
    try:
        output = ssh_cmd(host, f"unzip -l '{vps_path}/{prev_file}' 2>/dev/null")
    except Exception:
        return set(), set()
    jars = set()
    configs = set()
    for line in output.splitlines():
        parts = line.strip().split()
        if not parts:
            continue
        path = parts[-1]
        if "/mods/" in path and path.endswith(".jar"):
            jars.add(path.split("/")[-1])
        elif "/config/" in path and not path.endswith("/"):
            configs.add(path.split("/config/", 1)[-1])
    return jars, configs


def extract_mod_version(jar_name: str) -> tuple[str, str]:
    """Split a jar filename into (prefix, version).
    E.g. 'ModName-1.2.3.jar' -> ('ModName', '1.2.3')
    """
    base = jar_name.removesuffix(".jar").removesuffix(".jar.disabled")
    m = re.match(r"^(.+?)[_-](\d+\.\d+.*)$", base)
    if m:
        return m.group(1), m.group(2)
    return base, ""


def get_local_mod_list(instance_path: Path) -> set[str]:
    """Get mod jar filenames from the local instance."""
    mods_dir = instance_path / ".minecraft" / "mods"
    return {f.name for f in mods_dir.iterdir() if f.suffix == ".jar"}


def get_config_diff(instance_path: Path, prev_configs: set[str]) -> list[str]:
    """Diff local config directory against previous version's config paths."""
    local_configs = set()
    config_dir = instance_path / ".minecraft" / "config"
    if config_dir.is_dir():
        for f in config_dir.rglob("*"):
            if f.is_file():
                local_configs.add(f.relative_to(config_dir).as_posix())
    added = local_configs - prev_configs
    removed = prev_configs - local_configs
    changes = []
    if added:
        changes.append(f"Added {len(added)} config files")
    if removed:
        changes.append(f"Removed {len(removed)} config files")
    return changes


def get_disquests_changelog(old_jars: dict, new_jars: dict, repo: str) -> list[str]:
    """If disquests version changed, fetch first 3 lines from GitHub release."""
    old_ver, new_ver = None, None
    for name in old_jars:
        if "disquests-client" in name.lower():
            _, old_ver = extract_mod_version(name)
    for name in new_jars:
        if "disquests-client" in name.lower():
            _, new_ver = extract_mod_version(name)
    if not new_ver or new_ver == old_ver:
        return []
    try:
        result = subprocess.run(
            ["gh", "release", "view", f"v{new_ver}", "--repo", repo, "--json", "body", "--jq", ".body"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            return [f"Updated Disquests to v{new_ver}"]
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip() and not l.startswith("#")]
        return [f"Disquests v{new_ver}:"] + [f"  {l}" for l in lines[:3]]
    except Exception:
        return [f"Updated Disquests to v{new_ver}"]


def generate_changelog(instance_path: Path, config: dict) -> list[str]:
    """Generate changelog by diffing mod jars and configs against previous VPS version."""
    old_jars, old_configs = get_previous_zip_contents(config)
    new_jars = get_local_mod_list(instance_path)
    changelog = []

    if not old_jars:
        changelog.append("Initial release")
        return changelog

    old_by_prefix = {}
    for name in old_jars:
        prefix, ver = extract_mod_version(name)
        old_by_prefix[prefix.lower()] = (name, ver)
    new_by_prefix = {}
    for name in new_jars:
        prefix, ver = extract_mod_version(name)
        new_by_prefix[prefix.lower()] = (name, ver)

    for prefix in sorted(set(old_by_prefix) | set(new_by_prefix)):
        old_entry = old_by_prefix.get(prefix)
        new_entry = new_by_prefix.get(prefix)
        if old_entry and not new_entry:
            changelog.append(f"Removed {old_entry[0]}")
        elif new_entry and not old_entry:
            changelog.append(f"Added {new_entry[0]}")
        elif old_entry and new_entry and old_entry[1] != new_entry[1]:
            name = new_entry[0].split("-")[0] if "-" in new_entry[0] else prefix
            changelog.append(f"Updated {name} {old_entry[1]} -> {new_entry[1]}")

    config_changes = get_config_diff(instance_path, old_configs)
    changelog.extend(config_changes)

    dq_lines = get_disquests_changelog(old_jars, new_jars, config.get("disquests_repo", ""))
    if dq_lines:
        changelog.extend(dq_lines)

    return changelog


def upload_zip(zip_path: Path, config: dict):
    """SCP the zip to VPS."""
    host = config["vps_host"]
    vps_path = config["vps_path"]
    dest = f"{host}:{vps_path}/{zip_path.name}"
    print(f"Uploading {zip_path.name}...")
    subprocess.run(["scp", str(zip_path), dest], check=True)
    print("  Upload complete.")


def update_manifest(config: dict, version: str, filename: str, size_str: str, changelog: list[str]):
    """Read manifest from VPS, prepend new version, write back."""
    host = config["vps_host"]
    vps_path = config["vps_path"]
    mc_version = config["mc_version"]
    modloader = config["modloader"]

    try:
        raw = ssh_cmd(host, f"cat {vps_path}/manifest.json")
        manifest = json.loads(raw)
    except Exception:
        manifest = {"latest": None, "versions": []}

    new_entry = {
        "version": f"{mc_version} v{version}",
        "file": filename,
        "date": date.today().isoformat(),
        "mc": mc_version,
        "modloader": modloader,
        "size": size_str,
        "changelog": changelog,
    }

    manifest["latest"] = new_entry
    manifest["versions"].insert(0, new_entry)

    manifest_json = json.dumps(manifest, indent=2, ensure_ascii=False)
    ssh_cmd(host, f"cat > {vps_path}/manifest.json <<'MANIFEST_EOF'\n{manifest_json}\nMANIFEST_EOF")
    print("  Manifest updated.")


def update_symlink(config: dict, filename: str):
    """Update the latest.zip symlink on VPS."""
    host = config["vps_host"]
    vps_path = config["vps_path"]
    ssh_cmd(host, f"cd {vps_path} && ln -sf '{filename}' latest.zip")
    print("  Symlink updated.")


def prune_old_versions(config: dict, keep: int):
    """Remove old zip files beyond the keep count, and trim manifest versions array."""
    host = config["vps_host"]
    vps_path = config["vps_path"]

    raw = ssh_cmd(host, f"cat {vps_path}/manifest.json")
    manifest = json.loads(raw)
    versions = manifest.get("versions", [])

    if len(versions) <= keep:
        return

    to_remove = versions[keep:]
    manifest["versions"] = versions[:keep]

    manifest_json = json.dumps(manifest, indent=2, ensure_ascii=False)
    ssh_cmd(host, f"cat > {vps_path}/manifest.json <<'MANIFEST_EOF'\n{manifest_json}\nMANIFEST_EOF")

    for entry in to_remove:
        old_file = entry.get("file", "")
        if old_file:
            ssh_cmd(host, f"rm -f '{vps_path}/{old_file}'")
            print(f"  Pruned {old_file}")


def notify_discord(config: dict, version: str, changelog: list[str]):
    """Send a release notification to Discord via the bot's notify endpoint."""
    host = config["vps_host"]
    channel_id = config["discord_channel_id"]
    mc_version = config["mc_version"]
    role_id = config.get("discord_role_id", "")

    description = "\n".join(changelog) if changelog else "No changes listed."
    description += "\n\n[disqt.com/minecraft](https://disqt.com/minecraft/)"

    payload = {
        "channel_id": channel_id,
        "embed": {
            "title": f"Modpack {mc_version} v{version}",
            "description": description,
            "color": 0x2dd4bf,
        },
    }

    if role_id:
        payload["content"] = f"<@&{role_id}>"

    payload_json = json.dumps(payload, ensure_ascii=False)
    try:
        ssh_cmd(
            host,
            f"curl -sf -X POST http://localhost:9800/send "
            f"-H 'Content-Type: application/json' "
            f"-d {shlex.quote(payload_json)}",
        )
        print("  Discord notification sent.")
    except Exception as e:
        print(f"  Discord notification failed: {e}")


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

        # Generate changelog
        changelog = generate_changelog(args.instance_path, config)
        print("Changelog:")
        for line in changelog:
            print(f"  {line}")
        print()

        if args.dry_run:
            print("[dry-run] Would upload, update manifest, and notify.")
            return

        if not args.yes:
            confirm = input("Publish? [y/n] ").strip().lower()
            if confirm != "y":
                print("Aborted.")
                return

        # Upload
        upload_zip(zip_path, config)
        print()

        # Update manifest
        print("Updating manifest...")
        update_manifest(config, version, filename, size_str, changelog)

        # Update symlink
        print("Updating symlink...")
        update_symlink(config, filename)

        # Prune old versions
        print("Pruning old versions...")
        prune_old_versions(config, keep)
        print()

        # Discord notification (next task)
        if not args.no_notify and config.get("discord_channel_id"):
            notify_discord(config, version, changelog)

        print(f"Released {mc_version} v{version}")


if __name__ == "__main__":
    main()
