# Migration Preview CLI

## Purpose

A Python CLI tool that analyzes Minecraft world chunks against a query, generates visual reports showing which chunks would be kept vs deleted, and optionally performs the trim. Designed for major version migrations where old terrain should regenerate.

Two output modes: a standalone HTML preview page for quick visual inspection, and a raw binary file that the existing chunk inspector at `disqt.com/minecraft/chunks/` can ingest as a new overlay layer.

## CLI Interface

```
python migrate.py <world-path> [options]

# or download first
python migrate.py --host <ssh-host> --remote-path <path> [options]
```

### Arguments

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `<world-path>` | yes* | — | Local world directory (positional) |
| `--host` | no | — | SSH host to download from (uses ~/.ssh/config) |
| `--remote-path` | no | — | Remote world directory path (see Dimension Paths) |
| `--dimensions` | no | all present | Space-separated: `overworld`, `nether`, `end` |
| `--threshold N` | no | — | InhabitedTime < N ticks (pure Python, no Java). 120 ticks = 6 seconds. |
| `--query "..."` | no | — | Full MCA Selector query string (requires `--mcaselector`) |
| `--mcaselector` | no | — | Path to MCA Selector JAR (required with `--query`) |
| `--html <file>` | no | — | Generate standalone HTML preview |
| `--raw <file>` | no | — | Generate binary data for chunk inspector |
| `--dangerously-perform-the-trim` | no | — | Actually delete matching chunks |
| `--safety-pct N` | no | `90` | Abort trim if deletion > N% per dimension |
| `--force` | no | — | Override safety abort |

**Input rules:**

- Either `<world-path>` or `--host` + `--remote-path` is required, not both. If both are given, the CLI exits with an error.
- If SSH args are given, the world downloads to `./migration-work/<world-name>/`.

**Query rules:**

- If neither `--threshold` nor `--query` is given, defaults to `--threshold 120` (6 seconds of player presence — intentionally aggressive, targets chunks a player barely passed through).
- `--threshold` and `--query` are mutually exclusive. `--query` requires `--mcaselector`.

**Output rules:**

- If no output flags are given (`--html`, `--raw`, `--dangerously-perform-the-trim`), the CLI just prints the stats table to the terminal. This is valid — useful for a quick check.
- `--html` and `--raw` are always generated regardless of safety check results. The safety check only blocks `--dangerously-perform-the-trim`.

### Examples

```bash
# Quick local preview
python migrate.py ./world_new --threshold 120 --html preview.html

# Download from server, preview all dimensions
python migrate.py --host minecraft \
  --remote-path /home/minecraft/serverfiles \
  --threshold 120 --dimensions overworld nether end \
  --html preview.html

# Power user: full MCA Selector query
python migrate.py ./world_new \
  --query "InhabitedTime < 600 AND DataVersion < 2860" \
  --mcaselector ./mcaselector.jar \
  --html preview.html --raw migration.bin

# Generate chunk inspector overlay data
python migrate.py ./world_new --threshold 120 --raw migration.bin

# Actually trim (after reviewing the preview)
python migrate.py ./world_new --threshold 120 --dangerously-perform-the-trim
```

## Dimension Paths

Minecraft servers store dimensions in different layouts depending on the server software.

**PaperMC layout** (separate world folders — used by the target server):
```
serverfiles/
  world_new/                    # Overworld
    region/
  world_new_nether/             # Nether
    DIM-1/region/
  world_new_the_end/            # End
    DIM1/region/
```

**Vanilla layout** (everything under one world folder):
```
world/
  region/                       # Overworld
  DIM-1/region/                 # Nether
  DIM1/region/                  # End
```

**When using a local `<world-path>`:** The CLI auto-detects the layout. If `<world-path>/DIM-1/region/` exists, it's Vanilla layout. If not, it looks for sibling directories matching `*_nether/DIM-1/region/` and `*_the_end/DIM1/region/` (PaperMC layout).

**When using `--remote-path`:** Point it at the `serverfiles/` root (PaperMC) or the world folder (Vanilla). The CLI probes remote paths via SSH to detect layout before downloading.

## Pipeline

### Step 1: Resolve World

If `--host` is given, detect dimension layout via SSH probe, then SCP the world down with a progress bar. Downloads `level.dat` + `region/` contents for each selected dimension.

If a positional `<world-path>` is given, auto-detect layout and use it directly.

### Step 2: Analyze

For each selected dimension, determine which chunks match the query.

**With `--threshold` (pure Python, no Java):**

Parse each .mca region file:
1. Read the 4096-byte location header to find populated chunk offsets
2. For each populated chunk, seek to its offset, read the compression type byte, decompress the NBT data (zlib for type 2, lz4 for type 4)
3. Extract `InhabitedTime` (long tag) and `DataVersion` (int tag) from the chunk root compound
4. Mark the chunk as keep (above threshold) or delete (below threshold)

**With `--query` (MCA Selector):**

Shell out to MCA Selector CLI in selection mode to get the set of matching chunks. The exact CLI incantation needs verification during implementation — MCA Selector's CLI interface may use `--mode select`, `--mode export`, or another flag to list matching chunks. The implementation should verify against the actual JAR and document the working command.

For non-overworld dimensions, use `--region` flag to point MCA Selector at the correct region directory. LZ4 handling is only relevant for `--threshold` mode; MCA Selector handles all compression types internally.

**Output of analysis:** A per-dimension data structure mapping each chunk to its keep/delete status, InhabitedTime, and DataVersion (when available from `--threshold` mode).

### Step 3: Print Stats

Always print a stats table to stderr:

```
Dimension      Total    Delete    Keep    Delete %
─────────────────────────────────────────────────
Overworld      12,847   8,203     4,644   63.9%
Nether          2,104   1,456       648   69.2%
End               891     834        57   93.6%
─────────────────────────────────────────────────
Total          15,842  10,493     5,349   66.2%
```

### Step 4: Generate Outputs

Generated regardless of safety check results — you may want the preview specifically to understand a concerning deletion percentage.

**`--html <file>`: Standalone HTML preview**

A self-contained `.html` file (no external dependencies). Contains:
- Dark theme matching the chunk inspector aesthetic
- Dimension tabs (Overworld / Nether / End) to switch views
- Canvas grid: green = keep, red = delete, dark = unexplored
- Stats bar per dimension: total, delete, keep, percentage
- Query and timestamp in the header
- All chunk data embedded as base64-encoded binary in a `<script>` tag

The grid is static (no pan/zoom). Scales to fit the window. Each chunk is rendered as a colored pixel.

**`--raw <file>`: Binary data for chunk inspector**

Outputs a migration overlay file — a simpler format than the full chunk inspector data, containing only migration-relevant fields.

**Binary layout (Uint8 per chunk):**

```
Bit 7:    exists (1 = chunk present in world)
Bit 6:    delete (1 = marked for deletion)
Bits 0-5: InhabitedTime bucket (0-5, logarithmic scale matching the chunk inspector)
```

One byte per chunk in a 2D grid (row-major, `grid[z * cols + x]`).

When multiple dimensions are selected, the `--raw` filename gets a dimension suffix: `migration-overworld.bin`, `migration-nether.bin`, `migration-end.bin`. When only one dimension is selected, the exact filename is used.

Accompanied by a JSON metadata file (`<basename>.json`) with grid bounds and totals:

```json
{
  "min_cx": -500, "max_cx": 500,
  "min_cz": -500, "max_cz": 500,
  "cols": 1001, "rows": 1001,
  "total": 12847, "delete": 8203, "keep": 4644,
  "query": "InhabitedTime < 120",
  "timestamp": "2026-03-21T14:30:00"
}
```

The chunk inspector loads this as an optional overlay layer. When the file exists in the data directory, a "Migration Preview" toggle appears in the layer panel.

### Step 5: Safety Check + Trim

**Safety check** runs only when `--dangerously-perform-the-trim` is given. If any single dimension's deletion percentage exceeds `--safety-pct` (default 90%), the trim is aborted:

```
SAFETY ABORT: Would delete 93.6% of End chunks — this looks wrong.
Use --force to override.
```

The `--html` and `--raw` outputs are already written at this point (Step 4), so the user can inspect them.

**Trim (pure Python, with `--threshold`):**

For each chunk marked for deletion, zero out its 4-byte location entry and 4-byte timestamp entry in the region file header, then write the modified header back. Region files where all 1024 entries become zero are deleted entirely.

Note: orphaned chunk data sectors remain in the .mca file. The server reclaims this space when it next saves the region. For immediate disk reclamation, use MCA Selector's `--mode delete` instead (rewrites region files without orphaned sectors).

**Trim (MCA Selector, with `--query`):**

Shell out to MCA Selector `--mode delete` with the query string. MCA Selector rewrites region files cleanly (no orphaned sectors).

After trimming, print a summary:
```
Trim complete.
  Overworld: deleted 8,203 chunks
  Nether:    deleted 1,456 chunks
  End:       deleted 834 chunks
```

The two-pass workflow (preview first, trim second) is intentional. Run once with `--html` to review, then run again with `--dangerously-perform-the-trim` when satisfied.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Safety abort (trim blocked, but outputs were still generated) |
| 2 | Dependency/environment error (missing JAR, Java, SSH failed, bad paths) |

## Region File Parsing (Pure Python)

Minecraft Anvil region file format (.mca):

```
Bytes 0-4095:     Location table (1024 entries x 4 bytes)
                  Each entry: 3 bytes offset (in 4KiB sectors) + 1 byte sector count
                  Zero entry = chunk does not exist

Bytes 4096-8191:  Timestamp table (1024 entries x 4 bytes)
                  Each entry: Unix timestamp of last save

Byte 8192+:       Chunk data sectors
                  Each chunk sector starts with:
                    4 bytes: data length
                    1 byte:  compression type (1=gzip, 2=zlib, 3=uncompressed, 4=lz4)
                    N bytes: compressed NBT data
```

Chunk coordinates within a region: `chunk_x % 32`, `chunk_z % 32`. Region file `r.X.Z.mca` contains chunks from `(X*32, Z*32)` to `(X*32+31, Z*32+31)`.

**NBT parsing for InhabitedTime:** After decompressing, the chunk NBT is a compound tag. For MC 1.18+, `InhabitedTime` is at the root level. For pre-1.18, it's under `Level.InhabitedTime`. The `DataVersion` field determines which layout applies (DataVersion >= 2860 = 1.18+).

**LZ4 compression (MC 1.20.5+):** Compression type 4 uses LZ4 block format. The `lz4` pip package handles decompression. If `lz4` is not installed, the CLI warns and skips LZ4-compressed chunks (printing a count of how many were skipped so the user knows the analysis is incomplete).

**Trimming chunks (pure Python):** Zero the 4-byte location entry and 4-byte timestamp entry in the region header. Orphaned data sectors are not reclaimed — the server handles this on next save. If all 1024 entries in a region are zero, delete the .mca file entirely.

## Dependencies

- **Python 3.10+** (stdlib: argparse, struct, zlib, pathlib, subprocess, sys, base64, json)
- **lz4** (pip, optional — needed for MC 1.20.5+ chunks, graceful degradation without it)
- **Java + MCA Selector JAR** (only needed with `--query`)
- **SSH/SCP** (only needed with `--host`)

## File Location

`scripts/migrate.py` in the minecraft repository root, with supporting modules:

```
scripts/
  migrate.py            # CLI entry point, argument parsing, pipeline orchestration
  migrate_regions.py    # Region file parsing: headers, chunk NBT, InhabitedTime extraction
  migrate_mca.py        # MCA Selector wrapper for --query mode
  migrate_remote.py     # SSH/SCP download with progress
  migrate_html.py       # Standalone HTML report generator
  migrate_raw.py        # Binary data output for chunk inspector
```

## Companion Skill (separate spec)

A Claude Code skill (`/migrate-world`) will be designed separately after this CLI is built. It serves as the knowledge layer: migration strategies, when to use which threshold, step-by-step workflow guidance, and how to use this CLI tool.
