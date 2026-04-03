"""census.py — CLI entry point and pipeline orchestrator for the villager census."""

import json
from datetime import datetime, timezone
from pathlib import Path

from census_collect import (
    check_players_online,
    collect_villager_dumps,
    download_poi_files,
    get_player_position,
)
from census_db import (
    export_all_json,
    get_latest_snapshot,
    get_snapshot_villager_uuids,
    init_db,
    insert_bed,
    insert_gossip,
    insert_inventory_item,
    insert_snapshot,
    insert_trade,
    insert_villager,
    insert_villager_state,
    mark_dead,
)
from census_parse import parse_entity_line
from census_poi import parse_poi_regions


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_CENTER_X = 3150
DEFAULT_CENTER_Z = -950
DEFAULT_RADIUS = 300
DEFAULT_POI_REGIONS = [(5, -3), (5, -2), (6, -3), (6, -2)]


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run_census(*, db_path, center_x, center_z, radius, poi_regions, notes=None):
    """Run the full census pipeline and return a summary dict.

    Steps:
    1. Init DB, get previous snapshot UUIDs.
    2. Check players online.
    3. Collect villager entity dumps.
    4. Parse entity lines into villager dicts.
    5. Download and parse POI files for bed data.
    6. Filter beds to area bounds (center ± radius + 50 margin).
    7. Insert snapshot row.
    8. Insert villagers, states, trades, inventory, gossip.
    9. Insert beds (with home→uuid cross-reference for claimed_by).
    10. Detect deaths and births vs previous snapshot.
    11. Return summary.
    """
    conn = init_db(db_path)

    # Step 1: previous snapshot
    prev_snapshot = get_latest_snapshot(conn)
    prev_uuids = set()
    if prev_snapshot is not None:
        prev_uuids = get_snapshot_villager_uuids(conn, prev_snapshot["id"])

    # Step 2: players online
    players = check_players_online()

    # Step 3: collect entity lines
    entity_lines = collect_villager_dumps(center_x, center_z, radius)

    # Step 4: parse each line
    villagers = []
    for line in entity_lines:
        try:
            v = parse_entity_line(line)
            if v.get("uuid"):
                villagers.append(v)
        except (ValueError, KeyError):
            pass

    # Step 5: download and parse POI files
    poi_local_dir = Path("/tmp/census_poi")
    poi_paths = download_poi_files(poi_regions, poi_local_dir)
    all_beds = parse_poi_regions(poi_paths)

    # Step 6: filter beds to area bounds
    margin = 50
    x_min = center_x - radius - margin
    x_max = center_x + radius + margin
    z_min = center_z - radius - margin
    z_max = center_z + radius + margin

    beds = [
        b for b in all_beds
        if x_min <= b["pos"][0] <= x_max and z_min <= b["pos"][2] <= z_max
    ]

    # Step 7: insert snapshot
    timestamp = datetime.now(timezone.utc).isoformat()
    snapshot_id = insert_snapshot(
        conn,
        timestamp=timestamp,
        players_online=json.dumps(players),
        area_center_x=center_x,
        area_center_z=center_z,
        scan_radius=radius,
        villager_count=len(villagers),
        bed_count=len(beds),
        notes=notes,
    )

    # Step 8: insert villagers — build home→uuid lookup for bed cross-ref
    home_to_uuid = {}  # (x, y, z) -> uuid
    current_uuids = set()

    for v in villagers:
        uuid = v["uuid"]
        current_uuids.add(uuid)

        insert_villager(
            conn,
            uuid=uuid,
            first_seen_snapshot=snapshot_id,
            last_seen_snapshot=snapshot_id,
            spawn_reason=v.get("spawn_reason"),
            origin_x=v.get("origin_x"),
            origin_y=v.get("origin_y"),
            origin_z=v.get("origin_z"),
        )

        insert_villager_state(
            conn,
            snapshot_id=snapshot_id,
            villager_uuid=uuid,
            pos_x=v.get("pos_x"),
            pos_y=v.get("pos_y"),
            pos_z=v.get("pos_z"),
            health=v.get("health"),
            food_level=v.get("food_level"),
            profession=v.get("profession"),
            profession_level=v.get("profession_level"),
            villager_type=v.get("villager_type"),
            xp=v.get("xp"),
            ticks_lived=v.get("ticks_lived"),
            age=v.get("age"),
            home_x=v.get("home_x"),
            home_y=v.get("home_y"),
            home_z=v.get("home_z"),
            job_site_x=v.get("job_site_x"),
            job_site_y=v.get("job_site_y"),
            job_site_z=v.get("job_site_z"),
            meeting_point_x=v.get("meeting_point_x"),
            meeting_point_y=v.get("meeting_point_y"),
            meeting_point_z=v.get("meeting_point_z"),
            last_slept=v.get("last_slept"),
            last_woken=v.get("last_woken"),
            last_worked=v.get("last_worked"),
            last_restock=v.get("last_restock"),
            restocks_today=v.get("restocks_today"),
            on_ground=v.get("on_ground"),
            last_gossip_decay=v.get("last_gossip_decay"),
        )

        for trade in v.get("trades", []):
            insert_trade(
                conn,
                snapshot_id=snapshot_id,
                villager_uuid=uuid,
                slot=trade["slot"],
                buy_item=trade.get("buy_item"),
                buy_count=trade.get("buy_count"),
                buy_b_item=trade.get("buy_b_item"),
                buy_b_count=trade.get("buy_b_count"),
                sell_item=trade.get("sell_item"),
                sell_count=trade.get("sell_count"),
                price_multiplier=trade.get("price_multiplier"),
                max_uses=trade.get("max_uses"),
                xp=trade.get("xp"),
            )

        for item in v.get("inventory", []):
            insert_inventory_item(
                conn,
                snapshot_id=snapshot_id,
                villager_uuid=uuid,
                item=item["item"],
                count=item["count"],
            )

        for g in v.get("gossip", []):
            insert_gossip(
                conn,
                snapshot_id=snapshot_id,
                villager_uuid=uuid,
                gossip_type=g["gossip_type"],
                target_uuid=g.get("target_uuid"),
                value=g["value"],
            )

        # Build home lookup: integer coords from brain memory
        hx, hy, hz = v.get("home_x"), v.get("home_y"), v.get("home_z")
        if hx is not None and hy is not None and hz is not None:
            home_to_uuid[(int(hx), int(hy), int(hz))] = uuid

    # Step 9: insert beds
    for bed in beds:
        bx, by, bz = bed["pos"][0], bed["pos"][1], bed["pos"][2]
        claimed_by = home_to_uuid.get((int(bx), int(by), int(bz)))
        insert_bed(
            conn,
            snapshot_id=snapshot_id,
            pos_x=bx,
            pos_y=by,
            pos_z=bz,
            free_tickets=bed.get("free_tickets", 0),
            claimed_by=claimed_by,
        )

    # Step 10: deaths and births
    deaths_uuids = prev_uuids - current_uuids
    births_uuids = current_uuids - prev_uuids

    for uuid in deaths_uuids:
        mark_dead(conn, uuid, snapshot_id)

    # Step 11: compute homeless count (no home memory)
    homeless = sum(
        1 for v in villagers
        if v.get("home_x") is None
    )

    conn.close()

    return {
        "snapshot_id": snapshot_id,
        "timestamp": timestamp,
        "villager_count": len(villagers),
        "bed_count": len(beds),
        "births": len(births_uuids),
        "deaths": len(deaths_uuids),
        "homeless": homeless,
        "players_online": players,
    }


def export_census_json(db_path):
    """Export the entire census DB as a JSON-serializable dict."""
    conn = init_db(db_path)
    data = export_all_json(conn)
    conn.close()
    return data
