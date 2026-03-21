# World Migration CLI

Analyze Minecraft world chunks, preview which would be kept vs deleted, and optionally trim them. For major version migrations where old terrain should regenerate with new world generation.

## Quick Start

```bash
cd world-migration-cli

# Preview: which chunks would be deleted at threshold 120 ticks (6 seconds)?
python migrate.py ./world_new --threshold 120 --html preview.html

# Download from server first
python migrate.py --host minecraft \
  --remote-path /home/minecraft/serverfiles/world_new \
  --threshold 120 --dimensions overworld nether end \
  --html preview.html

# Just print stats, no output files
python migrate.py ./world_new --threshold 120

# Actually trim (after reviewing the preview)
python migrate.py ./world_new --threshold 120 --dangerously-perform-the-trim
```

Open `preview.html` in a browser to see a green/red chunk grid with dimension tabs.

## How It Works

1. **Resolve world** -- point at a local folder, or provide `--host`/`--remote-path` to download via SCP. Auto-detects PaperMC (separate world folders) and Vanilla (single folder) layouts.
2. **Analyze** -- reads every chunk's `InhabitedTime` from .mca region files via pure Python NBT parsing. No Java needed for `--threshold` mode.
3. **Output** -- prints a stats table, and optionally generates:
   - `--html` -- standalone HTML file with a canvas grid (green = keep, red = delete, dark = unexplored)
   - `--raw` -- binary overlay file the [chunk inspector](https://disqt.com/minecraft/chunks/) can ingest
4. **Trim** (only with `--dangerously-perform-the-trim`) -- zeros matching chunk entries in the region file headers. Safety check aborts if deletion exceeds `--safety-pct` (default 90%) per dimension.

## Arguments

| Arg | Default | Description |
|-----|---------|-------------|
| `<world-path>` | -- | Local world directory (or use `--host` + `--remote-path`) |
| `--host` | -- | SSH host to download from |
| `--remote-path` | -- | Remote world directory path |
| `--dimensions` | auto-detect | `overworld`, `nether`, `end` (space-separated) |
| `--threshold N` | `120` | InhabitedTime < N ticks. 120 = 6 seconds. Pure Python, no Java. |
| `--query "..."` | -- | Full MCA Selector query (requires `--mcaselector`) |
| `--mcaselector` | -- | Path to MCA Selector JAR (only with `--query`) |
| `--html <file>` | -- | Generate standalone HTML preview |
| `--raw <file>` | -- | Generate binary data for chunk inspector |
| `--dangerously-perform-the-trim` | -- | Actually delete matching chunks |
| `--safety-pct N` | `90` | Abort trim if deletion > N% per dimension |
| `--force` | -- | Override safety abort |

## Two Analysis Modes

**`--threshold` (default, pure Python):** Reads .mca files directly. Extracts `InhabitedTime` from each chunk's NBT data. No external tools needed. Handles zlib and LZ4 compression (LZ4 requires `pip install lz4`).

**`--query` (MCA Selector):** Delegates to MCA Selector CLI for complex queries like `"InhabitedTime < 600 AND DataVersion < 2860"`. Requires Java and the MCA Selector JAR.

## InhabitedTime Reference

`InhabitedTime` counts game ticks (20/second) a player has spent in a chunk.

| Threshold | Real time | What it catches |
|-----------|-----------|-----------------|
| 60 | 3 seconds | Chunks barely loaded at render distance edge |
| 120 | 6 seconds | Chunks a player passed through (default) |
| 600 | 30 seconds | Chunks a player lingered in briefly |
| 2400 | 2 minutes | Chunks with some activity |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Safety abort (outputs still generated, trim blocked) |
| 2 | Dependency/environment error |

## After Trimming

The CLI trims a local copy. To apply it to the server:

1. Stop the Minecraft server
2. Back up the current world
3. Upload the trimmed region files
4. Start the server
5. Run Chunky pre-generation for the trimmed areas
6. Purge and re-render BlueMap

## Dependencies

- Python 3.10+
- No pip dependencies (stdlib only)
- Optional: `lz4` pip package for MC 1.20.5+ chunks
- Optional: Java + MCA Selector JAR for `--query` mode

## Tests

```bash
cd world-migration-cli
python -m pytest tests/ -v
```

62 tests covering NBT parsing, region analysis, layout detection, HTML/raw output, CLI args, and end-to-end pipeline.

## Module Layout

| File | Purpose |
|------|---------|
| `migrate.py` | CLI entry point + pipeline orchestration |
| `migrate_nbt.py` | Minimal NBT reader (InhabitedTime, DataVersion) |
| `migrate_regions.py` | .mca region file parsing + chunk analysis |
| `migrate_remote.py` | PaperMC/Vanilla layout detection + SSH download |
| `migrate_html.py` | Standalone HTML preview generator |
| `migrate_raw.py` | Binary overlay output for chunk inspector |
| `migrate_mca.py` | MCA Selector CLI wrapper |
| `migrate_display.py` | Terminal stats table + safety abort formatting |
