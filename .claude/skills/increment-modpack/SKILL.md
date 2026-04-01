---
name: increment-modpack
description: Use when the user wants to create, bump, or clone a Prism Launcher modpack instance to a new version. Triggers on "increment modpack", "new modpack version", "copy instance to vX", "bump modpack", "create v2.10", or preparing a new instance before publishing.
---

# Increment Modpack

Creates a new Prism Launcher instance by copying the latest (or specified) version and bumping version numbers in the folder name, display name, and config.

## Path Resolution

Detect the Prism Launcher instances directory at runtime:
- **Windows**: `%APPDATA%/PrismLauncher/instances/`
- **Linux**: `~/.local/share/PrismLauncher/instances/`
- **macOS**: `~/Library/Application Support/PrismLauncher/instances/`

## Step 1: Identify Source and Target

List instances matching `*.* v*` pattern (e.g., `1.21.11 v2.8`). Sort by version number to find the latest, or use the one the user specifies.

Compute the next version by incrementing the minor number (e.g., `v2.8` -> `v2.9`, `v2.9` -> `v2.10`). Confirm source and target with the user if ambiguous.

## Step 2: Copy Instance

```bash
cp -r "<instances>/<source>" "<instances>/<target>"
```

Warn the user: **Minecraft and Prism Launcher must be closed** before copying, or locked files will cause incomplete copies.

## Step 3: Update instance.cfg

The file `<target>/instance.cfg` is an INI-like config. Update these fields to match the new version:

| Field | Example old | Example new |
|-------|-------------|-------------|
| `name=` | `1.21.11 v2.8` | `1.21.11 v2.9` |
| `ExportVersion=` | `2.8.0` | `2.9.0` |

Do NOT reset play time counters (`lastTimePlayed`, `totalTimePlayed`) -- they carry over as historical data.

## Step 4: Update modpack-version.txt

If `<target>/.minecraft/modpack-version.txt` exists, update its contents to the new version number (e.g., `2.9`). This file is read by the publish-modpack skill and the in-game version checker plugin.

## Step 5: Swap Mods (if requested)

If the user wants to replace specific mod jars:

1. List the old jar to remove: `ls <target>/.minecraft/mods/ | grep <mod-name>`
2. Remove it: `rm "<target>/.minecraft/mods/<old-jar>"`
3. Copy the new jar in: `cp "<source-jar>" "<target>/.minecraft/mods/"`

Common sources for new jars:
- GitHub release: `gh release download <tag> --pattern "<pattern>" --dir /tmp/`
- Local build output: `client/build/libs/client.jar`, `server/build/libs/server.jar`

## Step 6: Confirm

Report what was done:
- Source instance and target instance
- Config fields updated
- Any mods swapped (old -> new)

Remind the user to open Prism Launcher and verify the new instance appears with the correct name before launching.
