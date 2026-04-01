---
name: publish-modpack
description: Use when the user wants to publish, release, or upload a new Prism Launcher modpack version to disqt.com/minecraft/modpack/. Triggers on "publish modpack", "push modpack", "release modpack", "new modpack version", "upload modpack", or when making a new version available to players.
disable-model-invocation: true
---

# Publish Modpack

Automates the full modpack publishing pipeline: select instance, zip it, upload to VPS, update manifest, cleanup old versions, and reload the version checker plugin.

## Prerequisites

Before starting, warn the user: **Minecraft must be closed** before copying instance files. Locked files cause incomplete copies.

## Path Resolution

Detect the Prism Launcher instances directory at runtime:
- **Windows**: `%APPDATA%/PrismLauncher/instances/`
- **Linux**: `~/.local/share/PrismLauncher/instances/`
- **macOS**: `~/Library/Application Support/PrismLauncher/instances/`

Use the system temp directory for intermediate zip files (e.g., `$TMPDIR`, `%TEMP%`, or `/tmp`).

For Minecraft console access, find the tmux socket dynamically:
```bash
ssh minecraft "ls /tmp/tmux-*/pmcserver-*"
```

## Step 1: Select Instance

List available instances from the resolved Prism instances directory, filtering out `instgroups.json`. Present as a numbered list and ask the user to pick one.

## Step 2: Read Version Info

Read the version from `<instance>/.minecraft/modpack-version.txt`. The instance directory name is the modpack name (e.g., `1.21.11 v2.8`). The version file contains just the version number (e.g., `2.8`). Confirm both with the user.

## Step 3: Ask for Changelog

Ask the user for changelog entries (bullet points describing what changed). These go into `manifest.json`.

## Step 4: Zip the Instance

Create a zip archive named after the instance (e.g., `1.21.11 v2.8.zip`). The archive root folder should match the instance name.

**Exclude these directories:**
- `Distant_Horizons_server_data`
- `screenshots`
- `saves`
- `downloads`
- `.mixin.out`
- `debug`
- `logs`

Use Python `zipfile` or `7z`, whichever is available. Report the zip file size when done.

## Step 5: Upload to VPS

```bash
scp "<zip-path>" dev:/home/dev/prism/
```

## Step 6: Update Symlink

```bash
ssh dev "cd /home/dev/prism && ln -sf '<name>.zip' latest.zip"
```

## Step 7: Update manifest.json

Download the current manifest from VPS, prepend the new version entry to `versions` array, and update `latest` with the same data:

```json
{
  "version": "<instance name>",
  "file": "<instance name>.zip",
  "date": "<today YYYY-MM-DD>",
  "mc": "<mc version from instance name>",
  "modloader": "Fabric",
  "size": "<zip size in MB, rounded>",
  "changelog": ["<entry 1>", "<entry 2>"]
}
```

Upload the updated manifest back to `dev:/home/dev/prism/manifest.json`.

## Step 8: Cleanup Old Zips

Keep only the 3 most recent zip files on the VPS (plus `latest.zip` symlink):

```bash
ssh dev "cd /home/dev/prism && ls -t *.zip | grep -v latest.zip | tail -n +4 | while IFS= read -r f; do rm -f \"\$f\"; done"
```

## Step 9: Reload Version Checker

Send `plugman reload DisqtVersion` to the Minecraft server console via tmux (use the dynamically resolved socket path). Wait 3 seconds and check the console output to confirm success.

## Step 10: Update CLAUDE.md

Update the "Current modpack" line in `./CLAUDE.md` to reflect the new version.

## Summary

After all steps complete, show:
- Instance published
- Version number
- Zip size
- Manifest updated
- Old versions cleaned up
- Version checker reloaded
