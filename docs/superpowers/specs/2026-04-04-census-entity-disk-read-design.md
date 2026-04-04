# Census Entity Disk-Read Design

> Replace tmux log-scraping villager collection with direct reads of `world/entities/*.mca` files, plus an mtime-based noop gate.

## Problem

The census collects villager data by sending `execute as @e[type=villager] run data get entity @s` via tmux and parsing SNBT from server logs. This requires entities to be loaded and active in memory. Paper's Entity Activation Range (EAR) suppresses entities when no player is within 32 blocks, so forceloaded chunks have loaded terrain but sleeping entities. The command returns 0 villagers when nobody is online.

## Solution

Read villager entity data directly from `world/entities/*.mca` region files on disk. This mirrors the existing POI pipeline (beds/bells from `world/poi/*.mca`) and is immune to EAR, chunk loading state, and player presence.

Add an mtime-based noop gate: if entity region files haven't been modified since the last census, skip the run entirely.

## Architecture

### New module: `census_entities.py`

Parses entity region `.mca` files using the existing NBT reader from `census_poi.py`.

**`parse_entity_region(region_path)`** — mirrors `parse_poi_region()`. Iterates chunk slots in the `.mca` file, decompresses each, reads NBT. Each chunk's root compound contains an `Entities` list. Filters for entries where `id == "minecraft:villager"`, converts each to a villager dict via `nbt_to_villager()`.

**`nbt_to_villager(nbt)`** — maps an NBT compound dict to the same dict shape that `parse_entity_line()` currently returns. All fields are direct dict lookups (no regex parsing). Field mapping:

| Field | NBT path | Type |
|-------|----------|------|
| uuid | `UUID` (list of 4 ints) -> `ints_to_uuid()` | str |
| pos_x/y/z | `Pos` (list of 3 doubles) | float |
| origin_x/y/z | `Paper.Origin` (list of 3 doubles) | float |
| spawn_reason | `Paper.SpawnReason` | str |
| profession | `VillagerData.profession` (strip `minecraft:` prefix) | str |
| profession_level | `VillagerData.level` | int |
| villager_type | `VillagerData.type` (strip `minecraft:` prefix) | str |
| health | `Health` | float |
| food_level | `FoodLevel` | int |
| xp | `Xp` | int |
| ticks_lived | `Spigot.ticksLived` | int |
| age | `Age` | int |
| on_ground | `OnGround` | int (0/1) |
| restocks_today | `RestocksToday` | int |
| last_restock | `LastRestock` | int |
| last_gossip_decay | `LastGossipDecay` | int |
| home_x/y/z | `Brain.memories.minecraft:home.value.pos` (list of 3 ints) | int |
| job_site_x/y/z | `Brain.memories.minecraft:job_site.value.pos` (list of 3 ints) | int |
| meeting_point_x/y/z | `Brain.memories.minecraft:meeting_point.value.pos` (list of 3 ints) | int |
| last_slept | `Brain.memories.minecraft:last_slept.value` | int |
| last_woken | `Brain.memories.minecraft:last_woken.value` | int |
| last_worked | `Brain.memories.minecraft:last_worked_at_poi.value` | int |
| trades | `Offers.Recipes` (list of compound dicts) | list |
| inventory | `Inventory` (list of compound dicts) | list |
| gossip | `Gossips` (list of compound dicts) | list |

Trade recipe dict mapping (each entry in `Offers.Recipes`):

| Field | NBT path |
|-------|----------|
| buy_item | `buy.id` (strip `minecraft:`) |
| buy_count | `buy.count` |
| buy_b_item | `buyB.id` (strip `minecraft:`) |
| buy_b_count | `buyB.count` |
| sell_item | `sell.id` (strip `minecraft:`) |
| sell_count | `sell.count` |
| price_multiplier | `priceMultiplier` |
| max_uses | `maxUses` |
| xp | `xp` |

Gossip entry mapping (each entry in `Gossips`):

| Field | NBT path |
|-------|----------|
| gossip_type | `Type` |
| target_uuid | `Target` (list of 4 ints) -> `ints_to_uuid()` |
| value | `Value` |

Inventory item mapping (each entry in `Inventory`):

| Field | NBT path |
|-------|----------|
| item | `id` (strip `minecraft:`) |
| count | `count` |

### New functions in `census_collect.py`

**`save_all()`** — sends `save-all` via tmux, then tails the log waiting for "Saved the game" (with a timeout of 30 seconds). This flushes any hot entity data in loaded chunks to disk.

**`get_entity_files(region_coords, local_dir)`** — mirrors `get_poi_files()`. SCPs `world/entities/r.X.Z.mca` files to a local temp directory. Uses the same SSH/local transport pattern.

**`get_entity_mtimes(region_coords)`** — stats the entity `.mca` files on the server (via SSH or locally), returns `{filename: mtime_epoch}` dict.

### Entity directory path

Add a new constant alongside the existing `POI_DIR`:

```
ENTITY_DIR = "/home/minecraft/serverfiles/world_new/entities"
```

### Mtime noop gate

Added to `census.py main()`, runs before the census pipeline:

1. `save_all()` — flush dirty data
2. `get_entity_mtimes(entity_regions)` — stat entity `.mca` files
3. Load previous mtimes from the last successful `census_runs` row
4. If all mtimes match -> insert `census_runs` row with `status="skipped_no_changes"`, print skip message, return
5. If any changed -> proceed with full census

Entity region coords are derived from the zone bounding box using floor division: `region_x = block_x // 512`, `region_z = block_z // 512`. For Piwigord (x=3090..3220, z=-1040..-826), this gives entity regions `(6, -3)` and `(6, -2)` — matching the POI regions that cover those zones. Entity regions are computed at runtime from zone bounds, not copied from the POI config in `zones.toml`.

### Mtime storage

Add an `entity_mtimes` column to the `census_runs` table (TEXT, JSON-encoded dict of `{filename: mtime_epoch}`). The migration adds this column with a default of NULL. First run after migration always proceeds (no previous mtimes to compare).

### Changes to `census.py`

**`run_census()`**:
- Replace `collect_villager_dumps_box()` + `parse_entity_line()` loop with `get_entity_files()` + `parse_entity_region()` calls
- Entity region coords computed from zone bounding box
- Everything else unchanged (zone classification, bed/bell pipeline, death detection, summary)

**`main()`**:
- Remove `--lazy` flag and forceload lifecycle
- Add mtime noop gate before `run_census()`
- Store entity mtimes in `census_runs` row after successful run
- The `_build_cron_command()` no longer needs `--lazy`

### What gets removed

- `forceload_zones()`, `unforceload_zones()`, `_forceload_cmd()` from `census_collect.py`
- `_forceload_cmd()` helper from `census_collect.py`
- `--lazy` flag from CLI
- `collect_villager_dumps()`, `collect_villager_dumps_box()`, `_collect_with_selector()` from `census_collect.py` — no longer called
- `check_chunks_loaded()` from `census_collect.py` — no longer needed (mtime gate replaces chunk probing)

Keep `census_parse.py` in the codebase (it's tested and may be useful for ad-hoc SNBT parsing), but it's no longer imported by the main pipeline.

### What stays

- `census_poi.py` — untouched (bed/bell pipeline)
- `census_db.py` — one new column added to `census_runs`
- Zone classification, death detection, summary output — unchanged
- `check_players_online()` — still called inside `run_census()` for snapshot metadata
- `get_player_position()` — still available for ad-hoc use

### Entity regions: runtime computation

Entity region coords are computed from zone bounds, not hardcoded:

```python
def entity_region_coords(zones):
    """Compute the set of entity region (rx, rz) coords covering all zones."""
    from census_zones import bounding_box
    x_min, z_min, x_max, z_max = bounding_box(zones)
    regions = set()
    # Iterate block-space corners at region granularity (512 blocks = 32 chunks)
    for x in range(x_min // 512, (x_max // 512) + 1):
        for z in range(z_min // 512, (z_max // 512) + 1):
            regions.add((x, z))
    return sorted(regions)
```

This replaces the hardcoded `poi_regions` list for entity data. POI regions remain configured in `zones.toml` since POI files can cover a wider area (villagers can claim beds outside their zone).

## Testing

### `tests/test_census_entities.py` (new)

- `test_nbt_to_villager_basic` — verify all field mappings from a hand-crafted NBT dict
- `test_nbt_to_villager_missing_fields` — verify `.get()` defaults when optional fields are absent
- `test_nbt_to_villager_trades` — verify trade recipe mapping
- `test_nbt_to_villager_gossip` — verify gossip entry mapping with UUID conversion
- `test_nbt_to_villager_brain_memories` — verify home/job_site/meeting_point extraction
- `test_parse_entity_region` — build a minimal valid `.mca` with one villager entity, verify round-trip
- `test_parse_entity_region_filters_non_villagers` — include a zombie entity, verify it's excluded
- `test_parse_entity_region_empty` — empty region file returns empty list

### `tests/test_census_collect.py` (additions)

- `test_save_all_waits_for_confirmation` — verify save_all sends command and waits for log marker
- `test_save_all_timeout` — verify timeout behavior
- `test_get_entity_mtimes` — mock stat calls, verify dict output
- `test_get_entity_files` — mirror existing `get_poi_files` test pattern

### `tests/test_census_cli.py` (updates)

- Remove `--lazy` tests and forceload mock patches
- Add mtime noop gate tests:
  - `test_cli_skips_when_mtimes_unchanged` — verify skip with matching mtimes
  - `test_cli_runs_when_mtimes_changed` — verify full run with different mtimes
  - `test_cli_runs_on_first_run` — verify no previous mtimes triggers full run

### Existing tests

- `test_census_pipeline.py` — update mocks to use `get_entity_files` + `parse_entity_region` instead of `collect_villager_dumps_box` + `parse_entity_line`
- `test_census_zones.py` — `zone_bounds` tests remain (function kept if `bounding_box` still uses it)
- `test_census_parse.py` — kept as-is (module still exists, just not in the main pipeline)

## Migration path

1. Add `entity_mtimes` column to `census_runs` table (nullable TEXT)
2. Deploy new code to VPS
3. Update cron command (remove `--lazy` if present)
4. First cron run: no previous mtimes, runs full census from disk
5. Subsequent runs: mtime gate kicks in, skips if nothing changed
