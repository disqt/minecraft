---
name: migrate-world
description: Use when the user asks about Minecraft world migration, chunk trimming, preserving builds during version updates, InhabitedTime thresholds, MCA Selector usage, or preparing a world for a major Minecraft version upgrade. Also use when they mention "migrate", "trim chunks", "reset terrain", "new world generation", or want to know which chunks to keep vs delete.
---

# World Migration Guide

Help the user preserve their builds while regenerating terrain for a major Minecraft version update. The core problem: new versions change world generation, but old chunks keep stale terrain forever. The solution is trimming low-activity chunks so the server regenerates them with new terrain.

## When to Migrate

Migrations are worthwhile when Mojang changes world generation in a way that affects unexplored terrain. Not every version needs one.

**Major generation changes (worth migrating for):**

| Version | Change | DataVersion |
|---------|--------|-------------|
| 1.13 | Ocean overhaul, chunk format rewrite | 1519 |
| 1.16 | Nether overhaul (4 new biomes, bastions) | 2566 |
| 1.18 | Height extension Y=-64..319, cave overhaul | 2860 |
| 1.19 | Deep dark, mangrove swamp | 3105 |
| 1.20 | Cherry grove, trail ruins | 3463 |
| 1.21 | Trial chambers | 3953 |

**Minor updates (no migration needed):** Bug fixes, balance changes, new items that don't affect terrain generation.

## Strategy: Chunk Trimming

The community consensus for small servers. Delete chunks players barely touched — the server regenerates them with new terrain on next visit. Builds survive because they have high `InhabitedTime`.

**InhabitedTime** counts game ticks (20/second) a player has spent in a chunk. It's the best proxy for "does someone care about this chunk."

| Threshold | Real time | What it catches | Risk |
|-----------|-----------|-----------------|------|
| 60 ticks | 3 seconds | Render-distance edge loads | Very safe |
| **120 ticks** | **6 seconds** | **Chunks a player walked through** | **Recommended default** |
| 600 ticks | 30 seconds | Brief lingering | May catch small builds |
| 2400 ticks | 2 minutes | Moderate activity | Review preview carefully |

**120 ticks (6 seconds) is the sweet spot.** It catches flyover chunks but keeps anything a player spent meaningful time in. Start here and adjust after reviewing the preview.

## The CLI Tool

The `world-migration-cli/migrate.py` tool analyzes chunks and generates a visual preview.

### Quick Reference

```bash
# Preview which chunks would be deleted (generates HTML report)
python world-migration-cli/migrate.py ./world_copy --threshold 120 --html preview.html

# Download from server, preview all dimensions
python world-migration-cli/migrate.py \
  --host minecraft \
  --remote-path /home/minecraft/serverfiles/world_new \
  --dimensions overworld nether end \
  --threshold 120 \
  --html preview.html

# Just print stats (no output files)
python world-migration-cli/migrate.py ./world_copy --threshold 120

# Generate data for the chunk inspector overlay
python world-migration-cli/migrate.py ./world_copy --threshold 120 --raw migration.bin

# Power user: MCA Selector query (requires Java + JAR)
python world-migration-cli/migrate.py ./world_copy \
  --query "InhabitedTime < 600 AND DataVersion < 2860" \
  --mcaselector ./mcaselector.jar \
  --html preview.html

# Actually trim (only after reviewing the preview!)
python world-migration-cli/migrate.py ./world_copy \
  --threshold 120 \
  --dangerously-perform-the-trim
```

### Key Arguments

| Arg | Description |
|-----|-------------|
| `<world-path>` | Local world directory |
| `--host` / `--remote-path` | Download world from SSH host instead |
| `--dimensions` | Which dimensions (`overworld nether end`), default: auto-detect all |
| `--threshold N` | InhabitedTime < N ticks (pure Python, no Java needed) |
| `--query "..."` | Full MCA Selector query (needs `--mcaselector` JAR path) |
| `--html <file>` | Generate standalone HTML preview (green=keep, red=delete) |
| `--raw <file>` | Generate binary overlay for chunk inspector |
| `--dangerously-perform-the-trim` | Actually delete matching chunks |
| `--safety-pct N` | Abort if >N% would be deleted per dimension (default: 90) |
| `--force` | Override safety abort |

### Two Analysis Modes

**`--threshold` (recommended):** Pure Python. Reads .mca files directly, no external tools. Handles zlib and LZ4 compression.

**`--query`:** Delegates to MCA Selector CLI for complex queries combining InhabitedTime, DataVersion, biome, block palette, etc. Requires Java + MCA Selector JAR.

## Migration Workflow

### 1. Back Up

Take a manual backup before anything else. The daily automated backup is good, but label this one clearly.

```bash
ssh minecraft "/home/minecraft/pmcserver backup"
```

### 2. Copy the World Locally

Work on a copy, never the live world.

```bash
# SCP the world down (or use the CLI's --host flag)
scp -r minecraft:/home/minecraft/serverfiles/world_new ./world_copy
```

### 3. Preview

Generate an HTML preview and open it. Look at the green/red grid — green chunks survive, red chunks get deleted.

```bash
python world-migration-cli/migrate.py ./world_copy \
  --threshold 120 \
  --dimensions overworld nether end \
  --html preview.html
```

Open `preview.html` in a browser. Check:
- Are your bases green? (They should be — high InhabitedTime)
- Are the edges of explored areas red? (Expected — flyover chunks)
- Is the deletion percentage reasonable? (50-70% is normal for a well-explored world)

If too many chunks are being kept, lower the threshold. If builds are being caught, raise it.

### 4. Trim

Once satisfied with the preview:

```bash
python world-migration-cli/migrate.py ./world_copy \
  --threshold 120 \
  --dimensions overworld nether end \
  --dangerously-perform-the-trim
```

### 5. Test the Trimmed World

Before touching the live server, verify the trimmed world works. Copy it to a staging location or test server and boot it. Walk around your builds, check chunk borders look reasonable.

### 6. Deploy

```bash
# Stop the server (check if players are online first!)
ssh minecraft "/home/minecraft/pmcserver stop"

# Upload trimmed world (replace region dirs)
ssh minecraft "rm -rf /home/minecraft/serverfiles/world_new/region"
scp -r ./world_copy/region minecraft:/home/minecraft/serverfiles/world_new/

# Repeat for nether and end if trimmed
ssh minecraft "rm -rf /home/minecraft/serverfiles/world_new_nether/DIM-1/region"
scp -r ./world_copy_nether/DIM-1/region minecraft:/home/minecraft/serverfiles/world_new_nether/DIM-1/

# Start the server
ssh minecraft "/home/minecraft/pmcserver start"
```

### 7. Post-Deploy

```bash
# Pre-generate trimmed areas to avoid lag spikes
# (via server console or tmux)
chunky radius 3000
chunky start

# Purge and re-render BlueMap
bluemap purge world_new
bluemap render world_new
```

## Nether and End

Apply the same InhabitedTime trimming to Nether and End — don't just delete them. Players may have:
- Nether highways and rails
- XP farms in the End
- Nether hub builds
- End island bases

The `--dimensions overworld nether end` flag trims all three with the same threshold. Each dimension's deletion % is checked independently by the safety check.

## Troubleshooting

**"Would delete 95% of chunks"** — Safety check fired. Either the threshold is too aggressive for this world, or the world is mostly unexplored. Review with `--html` first. Use `--force` only if you're sure.

**LZ4 warning** — Some chunks use LZ4 compression (MC 1.20.5+). Install `pip install lz4` to handle them. Without it, those chunks are skipped (counted but not analyzed).

**MCA Selector not found** — Only needed for `--query` mode. For `--threshold` mode, no external tools are required.

**HTML preview shows nothing** — The world path might be wrong, or no .mca files were found. Check the terminal stats output — if total chunks is 0, the path or dimension detection failed.
