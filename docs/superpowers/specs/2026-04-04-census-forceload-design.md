# Census Forceload Mode Design

## Problem

The census cron job depends on a player being online to keep chunks loaded. Without loaded chunks, `--auto` skips the run entirely. This makes unattended census unreliable.

## Solution

Replace `--auto` with two chunk-loading strategies:

- **`--force` (default)**: Forceload all zone chunks before the census, run the full pipeline, then unforceload. Works autonomously on cron with no player required.
- **`--lazy`**: Probe each zone for loaded chunks, run only loaded zones, skip the rest. Lightweight fallback for when forceloading is undesirable.

Remove `--auto` and the `check_players_online` gate entirely. The chunk probe (`execute if loaded`) is ground truth — checking player presence was always a proxy.

## Architecture

### Chunk strategy selection

```
census.py CLI
  --lazy flag → ChunkStrategy.LAZY
  (default)  → ChunkStrategy.FORCE
```

The strategy is passed into `run_census()` as a parameter. The pipeline calls the appropriate functions from `census_collect.py` based on the strategy.

### Forceload lifecycle

Forceload is a bracket operation: acquire before census, release after (including on error).

```
forceload_zones(zones)       # /forceload add for each zone
try:
    run census pipeline
finally:
    unforceload_zones(zones)  # /forceload remove for each zone
```

### Forceload commands

Minecraft's `/forceload` operates on chunk coordinates (block coord >> 4). Each zone gets one `forceload add` command covering its bounding box:

```
/forceload add <chunk_x_min> <chunk_z_min> <chunk_x_max> <chunk_z_max>
```

Where `chunk_x_min = floor(block_x_min / 16)`, etc.

For circle zones, use the bounding box (already computed by `bounding_box()` in `census_zones.py`).

Wait ~2 seconds after forceloading for chunks to finish loading before starting the census.

### Lazy mode

Same as current `--auto` chunk behavior, minus the players-online check:

1. Probe each zone with `execute if loaded <center_x> 64 <center_z>`
2. Run census on responding zones
3. Log skipped zones
4. If no zones loaded, log `skipped_no_chunks` to `census_runs` and exit

## Files Changed

### `census_collect.py`

Add two functions:

```python
def forceload_zones(zones):
    """Send /forceload add for each zone's bounding box (chunk coords)."""

def unforceload_zones(zones):
    """Send /forceload remove for each zone's bounding box (chunk coords)."""
```

Both use `_send_tmux()` to send commands. Each zone gets one command. Sleep 0.3s between commands (same pattern as `check_chunks_loaded`). `forceload_zones` sleeps 2s after all commands to let chunks load.

Keep `check_players_online()` — it's still called inside `run_census()` to record who was online in the snapshot. Just remove it as a gating check in the CLI.

### `census.py`

- Remove `--auto` flag
- Add `--lazy` flag: `parser.add_argument("--lazy", action="store_true", help="Skip zones with unloaded chunks instead of forceloading")`
- Default behavior (no `--lazy`): call `forceload_zones(zones)` before the pipeline, `unforceload_zones(zones)` after (in a finally block)
- `--lazy` behavior: call `check_chunks_loaded(zones)`, filter to loaded zones, skip if none
- Update `--install` cron builder to use `--lazy` instead of `--auto`
- Keep `census_runs` logging: `completed`, `skipped_no_chunks` (lazy only)
- Remove `check_players_online` from CLI gating logic (keep the import — `run_census` still uses it for snapshot metadata)

### `tests/test_census_collect.py`

- Add tests for `forceload_zones` and `unforceload_zones` (mock `_send_tmux`)
- Verify chunk coordinate conversion (block >> 4)
- Verify sleep timing
- Keep `check_players_online` tests (function still used by pipeline)

### `tests/test_census_cli.py`

- Replace `--auto` tests with `--lazy` tests
- Add test for default (force) mode calling `forceload_zones`/`unforceload_zones`
- Update cron install tests to use `--lazy`

## Chunk coordinate conversion

Block-to-chunk: `chunk = block_coord >> 4` (equivalent to `floor(block_coord / 16)`)

For a zone with `x_min=3090, z_min=-1040, x_max=3220, z_max=-980`:
- `chunk_x_min = 3090 >> 4 = 193`
- `chunk_z_min = -1040 >> 4 = -65`
- `chunk_x_max = 3220 >> 4 = 201`
- `chunk_z_max = -980 >> 4 = -62` (note: -980 / 16 = -61.25, >> 4 gives -62 for negative)

Actually, Python's `>>` on negative numbers does arithmetic shift (floor division by power of 2), which is correct for Minecraft chunk coords.

## Backward compatibility

- Existing cron jobs using `--auto` will fail with an unrecognized argument error. The `--install` command must be re-run to update to `--lazy`.
- The `census_runs` table schema is unchanged. Old `skipped_no_players` entries remain valid historical data.
- Forceload state is transient — `/forceload remove` cleans up. If the process crashes mid-census, forceloaded chunks persist until server restart or manual cleanup. This is acceptable; the server already handles orphaned forceloads.

## Non-goals

- Mineflayer bot integration (unnecessary for chunk loading)
- Persistent forceload management (one-shot bracket is sufficient)
- Changes to the census data model or dashboard
