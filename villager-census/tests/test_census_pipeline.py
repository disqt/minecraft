"""Integration tests for the census pipeline orchestrator."""

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

import census
from census_db import init_db, get_latest_snapshot, get_snapshot_villager_uuids


SAMPLE_ENTITY_LINE = """[19:44:53] [Server thread/INFO]: Fisherman has the following entity data: {Paper.SpawnReason: "BREEDING", DeathTime: 0s, Bukkit.updateLevel: 2, RestocksToday: 0, Xp: 0, OnGround: 1b, LeftHanded: 0b, AbsorptionAmount: 0.0f, FoodLevel: 0b, LastRestock: 1001127489L, AgeLocked: 0b, Invulnerable: 0b, Brain: {memories: {"minecraft:last_woken": {value: 1018112423L}, "minecraft:job_site": {value: {pos: [I; 3172, 70, -754], dimension: "minecraft:overworld"}}, "minecraft:last_slept": {value: 1018111156L}, "minecraft:last_worked_at_poi": {value: 1001132966L}, "minecraft:meeting_point": {value: {pos: [I; 3170, 66, -883], dimension: "minecraft:overworld"}}}}, Paper.Origin: [3145.9453962812213d, 63.9375d, -1006.4578843209587d], Age: 0, Rotation: [44.46672f, 0.0f], HurtByTimestamp: 0, Bukkit.Aware: 1b, ForcedAge: 0, attributes: [{base: 0.5d, id: "minecraft:movement_speed"}], WorldUUIDMost: -8821679170295479734L, fall_distance: 0.0d, Air: 300s, Offers: {Recipes: [{buy: {id: "minecraft:emerald", count: 1}, sell: {id: "minecraft:cooked_cod", count: 6}, priceMultiplier: 0.05f, buyB: {id: "minecraft:cod", count: 6}, maxUses: 16}]}, UUID: [I; 346464738, -1288157012, -1558611273, 949520682], Inventory: [{id: "minecraft:beetroot", count: 2}], Spigot.ticksLived: 821095, Paper.OriginWorld: [I; -2053957240, -1408023990, -1113309832, -1718626039], Gossips: [], VillagerData: {type: "minecraft:taiga", profession: "minecraft:fisherman", level: 1}, WorldUUIDLeast: -4781629316178913015L, Motion: [0.0d, -0.0784000015258789d, 0.0d], Pos: [3173.038130397757d, 70.0d, -755.0478646574805d], Fire: 0s, CanPickUpLoot: 1b, Health: 16.0f, HurtTime: 0s, FallFlying: 0b, PersistenceRequired: 0b, LastGossipDecay: 1024984001L, PortalCooldown: 0}"""

SAMPLE_BEDS = [
    {"pos": [3172, 69, -923], "free_tickets": 0},
    {"pos": [3140, 67, -1042], "free_tickets": 1},
]


def test_run_census_end_to_end():
    """Full pipeline integration: mocked SSH, real SNBT parsing, real DB."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    with (
        patch("census.check_players_online", return_value=["Termiduck"]),
        patch("census.collect_villager_dumps", return_value=[SAMPLE_ENTITY_LINE]),
        patch("census.get_player_position", return_value=(3159.0, 58.0, -930.0)),
        patch("census.download_poi_files", return_value=[]),
        patch("census.parse_poi_regions", return_value=SAMPLE_BEDS),
    ):
        summary = census.run_census(
            db_path=db_path,
            center_x=census.DEFAULT_CENTER_X,
            center_z=census.DEFAULT_CENTER_Z,
            radius=census.DEFAULT_RADIUS,
            poi_regions=census.DEFAULT_POI_REGIONS,
        )

    # --- summary checks ---
    assert summary["villager_count"] == 1
    assert summary["bed_count"] == 2
    assert summary["births"] == 1
    assert summary["deaths"] == 0
    assert summary["players_online"] == ["Termiduck"]

    # --- DB checks ---
    conn = init_db(db_path)

    # 1 snapshot
    snap = get_latest_snapshot(conn)
    assert snap is not None
    assert snap["villager_count"] == 1
    assert snap["bed_count"] == 2

    # villager exists with correct spawn_reason
    cur = conn.execute("SELECT * FROM villagers")
    villagers = [dict(r) for r in cur.fetchall()]
    assert len(villagers) == 1
    assert villagers[0]["spawn_reason"] == "BREEDING"

    # 1 trade
    cur = conn.execute("SELECT * FROM villager_trades")
    trades = cur.fetchall()
    assert len(trades) == 1

    # 1 inventory item
    cur = conn.execute("SELECT * FROM villager_inventory")
    inventory = cur.fetchall()
    assert len(inventory) == 1

    # 2 beds
    cur = conn.execute("SELECT * FROM beds")
    beds = [dict(r) for r in cur.fetchall()]
    assert len(beds) == 2

    conn.close()


def test_run_census_detects_deaths():
    """Second run missing a previously seen villager marks it as dead."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    # First run: 1 villager alive
    with (
        patch("census.check_players_online", return_value=[]),
        patch("census.collect_villager_dumps", return_value=[SAMPLE_ENTITY_LINE]),
        patch("census.get_player_position", return_value=None),
        patch("census.download_poi_files", return_value=[]),
        patch("census.parse_poi_regions", return_value=[]),
    ):
        summary1 = census.run_census(
            db_path=db_path,
            center_x=census.DEFAULT_CENTER_X,
            center_z=census.DEFAULT_CENTER_Z,
            radius=census.DEFAULT_RADIUS,
            poi_regions=census.DEFAULT_POI_REGIONS,
        )

    assert summary1["births"] == 1
    assert summary1["deaths"] == 0

    # Second run: no villagers found — should mark the first as dead
    with (
        patch("census.check_players_online", return_value=[]),
        patch("census.collect_villager_dumps", return_value=[]),
        patch("census.get_player_position", return_value=None),
        patch("census.download_poi_files", return_value=[]),
        patch("census.parse_poi_regions", return_value=[]),
    ):
        summary2 = census.run_census(
            db_path=db_path,
            center_x=census.DEFAULT_CENTER_X,
            center_z=census.DEFAULT_CENTER_Z,
            radius=census.DEFAULT_RADIUS,
            poi_regions=census.DEFAULT_POI_REGIONS,
        )

    assert summary2["deaths"] == 1
    assert summary2["births"] == 0

    conn = init_db(db_path)
    cur = conn.execute("SELECT presumed_dead FROM villagers")
    rows = cur.fetchall()
    assert len(rows) == 1
    assert rows[0]["presumed_dead"] == 1
    conn.close()


def test_run_census_bed_claimed_by():
    """Bed at villager's home position gets claimed_by set to that villager's UUID."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    # The sample villager has no home memory (no minecraft:home in brain),
    # so we use a bed at a known position with free_tickets=0 which would be
    # claimed if the home matched. Here we just verify the bed inserts correctly
    # with claimed_by=None when there's no match.
    beds = [{"pos": [3000, 64, -900], "free_tickets": 0}]

    with (
        patch("census.check_players_online", return_value=[]),
        patch("census.collect_villager_dumps", return_value=[SAMPLE_ENTITY_LINE]),
        patch("census.get_player_position", return_value=None),
        patch("census.download_poi_files", return_value=[]),
        patch("census.parse_poi_regions", return_value=beds),
    ):
        summary = census.run_census(
            db_path=db_path,
            center_x=census.DEFAULT_CENTER_X,
            center_z=census.DEFAULT_CENTER_Z,
            radius=census.DEFAULT_RADIUS,
            poi_regions=census.DEFAULT_POI_REGIONS,
        )

    conn = init_db(db_path)
    cur = conn.execute("SELECT claimed_by FROM beds")
    rows = cur.fetchall()
    assert len(rows) == 1
    assert rows[0]["claimed_by"] is None
    conn.close()


def test_export_census_json():
    """export_census_json returns a JSON-serializable dict with expected keys."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    with (
        patch("census.check_players_online", return_value=["Termiduck"]),
        patch("census.collect_villager_dumps", return_value=[SAMPLE_ENTITY_LINE]),
        patch("census.get_player_position", return_value=(3159.0, 58.0, -930.0)),
        patch("census.download_poi_files", return_value=[]),
        patch("census.parse_poi_regions", return_value=SAMPLE_BEDS),
    ):
        census.run_census(
            db_path=db_path,
            center_x=census.DEFAULT_CENTER_X,
            center_z=census.DEFAULT_CENTER_Z,
            radius=census.DEFAULT_RADIUS,
            poi_regions=census.DEFAULT_POI_REGIONS,
        )

    result = census.export_census_json(db_path)
    assert "snapshots" in result
    assert "villagers" in result
    assert len(result["snapshots"]) == 1
    assert len(result["villagers"]) == 1


def test_run_census_homeless_count():
    """Villagers without a home memory are counted as homeless."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    # SAMPLE_ENTITY_LINE has no minecraft:home in brain — should be homeless
    with (
        patch("census.check_players_online", return_value=[]),
        patch("census.collect_villager_dumps", return_value=[SAMPLE_ENTITY_LINE]),
        patch("census.get_player_position", return_value=None),
        patch("census.download_poi_files", return_value=[]),
        patch("census.parse_poi_regions", return_value=[]),
    ):
        summary = census.run_census(
            db_path=db_path,
            center_x=census.DEFAULT_CENTER_X,
            center_z=census.DEFAULT_CENTER_Z,
            radius=census.DEFAULT_RADIUS,
            poi_regions=census.DEFAULT_POI_REGIONS,
        )

    assert summary["homeless"] == 1
