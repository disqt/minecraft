"""Tests for census_entities.py — NBT-based villager entity parser."""

import pytest

from census_entities import nbt_to_villager


# ---------------------------------------------------------------------------
# NBT fixture builder
# ---------------------------------------------------------------------------

def _make_villager_nbt(**overrides):
    """Build a complete villager NBT dict. Pass overrides to replace top-level keys."""
    nbt = {
        "id": "minecraft:villager",
        "UUID": [346464738, -1288157012, -1558611273, 949520682],
        "Pos": [3173.038130397757, 70.0, -755.0478646574805],
        "Paper.Origin": [3145.9453962812213, 63.9375, -1006.4578843209587],
        "Paper.SpawnReason": "BREEDING",
        "VillagerData": {
            "profession": "minecraft:fisherman",
            "level": 1,
            "type": "minecraft:taiga",
        },
        "Health": 16.0,
        "FoodLevel": 0,
        "Xp": 0,
        "Spigot.ticksLived": 821095,
        "Age": 0,
        "OnGround": 1,
        "RestocksToday": 0,
        "LastRestock": 1001127489,
        "LastGossipDecay": 1024984001,
        "Brain": {
            "memories": {
                "minecraft:job_site": {
                    "value": {"pos": [3172, 70, -754], "dimension": "minecraft:overworld"}
                },
                "minecraft:meeting_point": {
                    "value": {"pos": [3170, 66, -883], "dimension": "minecraft:overworld"}
                },
                "minecraft:last_slept": {"value": 1018111156},
                "minecraft:last_woken": {"value": 1018112423},
                "minecraft:last_worked_at_poi": {"value": 1001132966},
            }
        },
        "Offers": {"Recipes": []},
        "Inventory": [],
        "Gossips": [],
    }
    nbt.update(overrides)
    return nbt


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_nbt_to_villager_basic():
    nbt = _make_villager_nbt()
    v = nbt_to_villager(nbt)

    # UUID (ints_to_uuid([346464738, -1288157012, -1558611273, 949520682]))
    assert v["uuid"] == "14a6a1e2-b338-48ac-a319-7ab73898892a"

    # Position
    assert v["pos_x"] == pytest.approx(3173.04, rel=1e-3)
    assert v["pos_y"] == pytest.approx(70.0)
    assert v["pos_z"] == pytest.approx(-755.05, rel=1e-3)

    # Origin
    assert v["origin_x"] == pytest.approx(3145.95, rel=1e-3)
    assert v["origin_y"] == pytest.approx(63.9375)
    assert v["origin_z"] == pytest.approx(-1006.46, rel=1e-3)

    # Paper fields
    assert v["spawn_reason"] == "BREEDING"

    # VillagerData
    assert v["profession"] == "fisherman"
    assert v["profession_level"] == 1
    assert v["villager_type"] == "taiga"

    # Health / food
    assert v["health"] == pytest.approx(16.0)
    assert v["food_level"] == 0

    # XP / ticks / age / ground
    assert v["xp"] == 0
    assert v["ticks_lived"] == 821095
    assert v["age"] == 0
    assert v["on_ground"] == 1

    # Commerce
    assert v["restocks_today"] == 0
    assert v["last_restock"] == 1001127489
    assert v["last_gossip_decay"] == 1024984001

    # Brain memory positions
    assert v["home_x"] is None
    assert v["home_y"] is None
    assert v["home_z"] is None
    assert v["job_site_x"] == 3172
    assert v["job_site_y"] == 70
    assert v["job_site_z"] == -754
    assert v["meeting_point_x"] == 3170
    assert v["meeting_point_y"] == 66
    assert v["meeting_point_z"] == -883

    # Brain memory scalars
    assert v["last_slept"] == 1018111156
    assert v["last_woken"] == 1018112423
    assert v["last_worked"] == 1001132966

    # Collections
    assert v["trades"] == []
    assert v["inventory"] == []
    assert v["gossip"] == []


def test_nbt_to_villager_missing_fields():
    """Minimal NBT — optional fields should default to None, collections to []."""
    nbt = {
        "id": "minecraft:villager",
        "UUID": [346464738, -1288157012, -1558611273, 949520682],
        "Pos": [100.5, 64.0, -200.5],
        "VillagerData": {
            "profession": "minecraft:none",
            "level": 1,
            "type": "minecraft:plains",
        },
        "Health": 20.0,
    }
    v = nbt_to_villager(nbt)

    # Required fields still present
    assert v["uuid"] == "14a6a1e2-b338-48ac-a319-7ab73898892a"
    assert v["pos_x"] == pytest.approx(100.5)
    assert v["profession"] == "none"
    assert v["health"] == pytest.approx(20.0)

    # Optional scalars default to None
    assert v["origin_x"] is None
    assert v["origin_y"] is None
    assert v["origin_z"] is None
    assert v["spawn_reason"] is None
    assert v["food_level"] is None
    assert v["xp"] is None
    assert v["ticks_lived"] is None
    assert v["age"] is None
    assert v["on_ground"] is None
    assert v["restocks_today"] is None
    assert v["last_restock"] is None
    assert v["last_gossip_decay"] is None
    assert v["home_x"] is None
    assert v["job_site_x"] is None
    assert v["meeting_point_x"] is None
    assert v["last_slept"] is None
    assert v["last_woken"] is None
    assert v["last_worked"] is None

    # Collections default to []
    assert v["trades"] == []
    assert v["inventory"] == []
    assert v["gossip"] == []


def test_nbt_to_villager_trades():
    """Trade recipes are parsed correctly."""
    nbt = _make_villager_nbt(Offers={
        "Recipes": [
            {
                "buy": {"id": "minecraft:emerald", "count": 1},
                "buyB": {"id": "minecraft:air", "count": 0},
                "sell": {"id": "minecraft:cooked_cod", "count": 6},
                "priceMultiplier": 0.05,
                "maxUses": 16,
                "xp": 1,
            },
            {
                "buy": {"id": "minecraft:string", "count": 20},
                "buyB": {"id": "minecraft:air", "count": 0},
                "sell": {"id": "minecraft:emerald", "count": 1},
                "priceMultiplier": 0.05,
                "maxUses": 16,
                "xp": 2,
            },
        ]
    })
    v = nbt_to_villager(nbt)
    trades = v["trades"]
    assert len(trades) == 2

    t0 = trades[0]
    assert t0["slot"] == 0
    assert t0["buy_item"] == "emerald"
    assert t0["buy_count"] == 1
    assert t0["sell_item"] == "cooked_cod"
    assert t0["sell_count"] == 6
    assert t0["price_multiplier"] == pytest.approx(0.05)
    assert t0["max_uses"] == 16
    assert t0["xp"] == 1

    t1 = trades[1]
    assert t1["slot"] == 1
    assert t1["buy_item"] == "string"
    assert t1["sell_item"] == "emerald"
    assert t1["xp"] == 2


def test_nbt_to_villager_inventory():
    """Inventory items are parsed correctly."""
    nbt = _make_villager_nbt(Inventory=[
        {"id": "minecraft:beetroot", "count": 2},
        {"id": "minecraft:wheat_seeds", "count": 3},
    ])
    v = nbt_to_villager(nbt)
    inv = v["inventory"]
    assert len(inv) == 2
    assert inv[0] == {"item": "beetroot", "count": 2}
    assert inv[1] == {"item": "wheat_seeds", "count": 3}


def test_nbt_to_villager_gossip():
    """Gossip entries are parsed correctly."""
    nbt = _make_villager_nbt(Gossips=[
        {
            "Type": "minor_negative",
            "Target": [-2075606571, 174605987, -2012950428, -563128421],
            "Value": 5,
        },
    ])
    v = nbt_to_villager(nbt)
    gossip = v["gossip"]
    assert len(gossip) == 1
    g = gossip[0]
    assert g["gossip_type"] == "minor_negative"
    assert g["value"] == 5
    assert isinstance(g["target_uuid"], str)
    assert len(g["target_uuid"]) == 36


def test_nbt_to_villager_home_memory():
    """Home brain memory is extracted when present."""
    nbt = _make_villager_nbt()
    nbt["Brain"]["memories"]["minecraft:home"] = {
        "value": {"pos": [3100, 65, -780], "dimension": "minecraft:overworld"}
    }
    v = nbt_to_villager(nbt)
    assert v["home_x"] == 3100
    assert v["home_y"] == 65
    assert v["home_z"] == -780
