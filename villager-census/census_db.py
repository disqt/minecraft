"""
census_db.py — SQLite data access layer for the villager census system.

All insert functions use keyword-only arguments and call conn.commit() after
each write. The connection is configured with row_factory=sqlite3.Row so rows
can be accessed as dicts.
"""

import sqlite3
from pathlib import Path


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp        TEXT    NOT NULL,
    players_online   INTEGER NOT NULL DEFAULT 0,
    area_center_x    REAL    NOT NULL DEFAULT 0,
    area_center_z    REAL    NOT NULL DEFAULT 0,
    scan_radius      INTEGER NOT NULL DEFAULT 64,
    villager_count   INTEGER NOT NULL DEFAULT 0,
    bed_count        INTEGER NOT NULL DEFAULT 0,
    notes            TEXT
);

CREATE TABLE IF NOT EXISTS villagers (
    uuid                TEXT    PRIMARY KEY,
    first_seen_snapshot INTEGER NOT NULL REFERENCES snapshots(id),
    last_seen_snapshot  INTEGER NOT NULL REFERENCES snapshots(id),
    spawn_reason        TEXT,
    origin_x            REAL,
    origin_y            REAL,
    origin_z            REAL,
    presumed_dead       INTEGER NOT NULL DEFAULT 0,
    death_snapshot      INTEGER REFERENCES snapshots(id)
);

CREATE TABLE IF NOT EXISTS villager_states (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id         INTEGER NOT NULL REFERENCES snapshots(id),
    villager_uuid       TEXT    NOT NULL REFERENCES villagers(uuid),
    pos_x               REAL,
    pos_y               REAL,
    pos_z               REAL,
    health              REAL,
    food_level          INTEGER,
    profession          TEXT,
    profession_level    INTEGER,
    villager_type       TEXT,
    xp                  INTEGER,
    ticks_lived         INTEGER,
    age                 INTEGER,
    home_x              REAL,
    home_y              REAL,
    home_z              REAL,
    job_site_x          REAL,
    job_site_y          REAL,
    job_site_z          REAL,
    meeting_point_x     REAL,
    meeting_point_y     REAL,
    meeting_point_z     REAL,
    last_slept          TEXT,
    last_woken          TEXT,
    last_worked         TEXT,
    last_restock        TEXT,
    restocks_today      INTEGER,
    on_ground           INTEGER,
    last_gossip_decay   TEXT,
    UNIQUE(snapshot_id, villager_uuid)
);

CREATE TABLE IF NOT EXISTS villager_trades (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id     INTEGER NOT NULL REFERENCES snapshots(id),
    villager_uuid   TEXT    NOT NULL REFERENCES villagers(uuid),
    slot            INTEGER NOT NULL,
    buy_item        TEXT,
    buy_count       INTEGER,
    buy_b_item      TEXT,
    buy_b_count     INTEGER,
    sell_item       TEXT,
    sell_count      INTEGER,
    price_multiplier REAL,
    max_uses        INTEGER,
    xp              INTEGER
);

CREATE TABLE IF NOT EXISTS villager_inventory (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id   INTEGER NOT NULL REFERENCES snapshots(id),
    villager_uuid TEXT    NOT NULL REFERENCES villagers(uuid),
    item          TEXT    NOT NULL,
    count         INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS villager_gossip (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id   INTEGER NOT NULL REFERENCES snapshots(id),
    villager_uuid TEXT    NOT NULL REFERENCES villagers(uuid),
    gossip_type   TEXT    NOT NULL,
    target_uuid   TEXT,
    value         INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS beds (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id   INTEGER NOT NULL REFERENCES snapshots(id),
    pos_x         INTEGER NOT NULL,
    pos_y         INTEGER NOT NULL,
    pos_z         INTEGER NOT NULL,
    free_tickets  INTEGER NOT NULL DEFAULT 0,
    claimed_by    TEXT    REFERENCES villagers(uuid),
    UNIQUE(snapshot_id, pos_x, pos_y, pos_z)
);
"""


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def init_db(db_path):
    """Create all tables and return a connection with row_factory=sqlite3.Row."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Insert helpers
# ---------------------------------------------------------------------------

def _row_to_dict(row):
    if row is None:
        return None
    return dict(row)


def insert_snapshot(conn, *, timestamp, players_online, area_center_x,
                    area_center_z, scan_radius, villager_count, bed_count,
                    notes):
    """Insert a snapshot row and return its lastrowid."""
    cur = conn.execute(
        """
        INSERT INTO snapshots
            (timestamp, players_online, area_center_x, area_center_z,
             scan_radius, villager_count, bed_count, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (timestamp, players_online, area_center_x, area_center_z,
         scan_radius, villager_count, bed_count, notes),
    )
    conn.commit()
    return cur.lastrowid


def insert_villager(conn, *, uuid, first_seen_snapshot, last_seen_snapshot,
                    spawn_reason, origin_x, origin_y, origin_z):
    """Upsert a villager row; on conflict update last_seen_snapshot."""
    cur = conn.execute(
        """
        INSERT INTO villagers
            (uuid, first_seen_snapshot, last_seen_snapshot,
             spawn_reason, origin_x, origin_y, origin_z)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(uuid) DO UPDATE SET
            last_seen_snapshot = excluded.last_seen_snapshot
        """,
        (uuid, first_seen_snapshot, last_seen_snapshot,
         spawn_reason, origin_x, origin_y, origin_z),
    )
    conn.commit()
    return cur.lastrowid


def insert_villager_state(conn, *, snapshot_id, villager_uuid, pos_x, pos_y,
                          pos_z, health, food_level, profession,
                          profession_level, villager_type, xp, ticks_lived,
                          age, home_x, home_y, home_z, job_site_x, job_site_y,
                          job_site_z, meeting_point_x, meeting_point_y,
                          meeting_point_z, last_slept, last_woken,
                          last_worked, last_restock, restocks_today,
                          on_ground, last_gossip_decay):
    """Insert a villager state row. UNIQUE(snapshot_id, villager_uuid)."""
    cur = conn.execute(
        """
        INSERT INTO villager_states
            (snapshot_id, villager_uuid, pos_x, pos_y, pos_z, health,
             food_level, profession, profession_level, villager_type, xp,
             ticks_lived, age, home_x, home_y, home_z, job_site_x,
             job_site_y, job_site_z, meeting_point_x, meeting_point_y,
             meeting_point_z, last_slept, last_woken, last_worked,
             last_restock, restocks_today, on_ground, last_gossip_decay)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (snapshot_id, villager_uuid, pos_x, pos_y, pos_z, health,
         food_level, profession, profession_level, villager_type, xp,
         ticks_lived, age, home_x, home_y, home_z, job_site_x,
         job_site_y, job_site_z, meeting_point_x, meeting_point_y,
         meeting_point_z, last_slept, last_woken, last_worked,
         last_restock, restocks_today, on_ground, last_gossip_decay),
    )
    conn.commit()
    return cur.lastrowid


def insert_trade(conn, *, snapshot_id, villager_uuid, slot, buy_item,
                 buy_count, buy_b_item, buy_b_count, sell_item, sell_count,
                 price_multiplier, max_uses, xp):
    """Insert a trade row."""
    cur = conn.execute(
        """
        INSERT INTO villager_trades
            (snapshot_id, villager_uuid, slot, buy_item, buy_count,
             buy_b_item, buy_b_count, sell_item, sell_count,
             price_multiplier, max_uses, xp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (snapshot_id, villager_uuid, slot, buy_item, buy_count,
         buy_b_item, buy_b_count, sell_item, sell_count,
         price_multiplier, max_uses, xp),
    )
    conn.commit()
    return cur.lastrowid


def insert_inventory_item(conn, *, snapshot_id, villager_uuid, item, count):
    """Insert an inventory item row."""
    cur = conn.execute(
        """
        INSERT INTO villager_inventory (snapshot_id, villager_uuid, item, count)
        VALUES (?, ?, ?, ?)
        """,
        (snapshot_id, villager_uuid, item, count),
    )
    conn.commit()
    return cur.lastrowid


def insert_gossip(conn, *, snapshot_id, villager_uuid, gossip_type,
                  target_uuid, value):
    """Insert a gossip row."""
    cur = conn.execute(
        """
        INSERT INTO villager_gossip
            (snapshot_id, villager_uuid, gossip_type, target_uuid, value)
        VALUES (?, ?, ?, ?, ?)
        """,
        (snapshot_id, villager_uuid, gossip_type, target_uuid, value),
    )
    conn.commit()
    return cur.lastrowid


def insert_bed(conn, *, snapshot_id, pos_x, pos_y, pos_z, free_tickets,
               claimed_by):
    """Insert a bed row. UNIQUE(snapshot_id, pos_x, pos_y, pos_z)."""
    cur = conn.execute(
        """
        INSERT INTO beds (snapshot_id, pos_x, pos_y, pos_z, free_tickets, claimed_by)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (snapshot_id, pos_x, pos_y, pos_z, free_tickets, claimed_by),
    )
    conn.commit()
    return cur.lastrowid


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def get_villager(conn, uuid):
    """Return a villager row as dict, or None if not found."""
    cur = conn.execute("SELECT * FROM villagers WHERE uuid = ?", (uuid,))
    return _row_to_dict(cur.fetchone())


def get_latest_snapshot(conn):
    """Return the most recent snapshot as dict, or None if table is empty."""
    cur = conn.execute(
        "SELECT * FROM snapshots ORDER BY timestamp DESC, id DESC LIMIT 1"
    )
    return _row_to_dict(cur.fetchone())


def mark_dead(conn, uuid, death_snapshot):
    """Set presumed_dead=1 and record death_snapshot for a villager."""
    conn.execute(
        """
        UPDATE villagers
        SET presumed_dead = 1, death_snapshot = ?
        WHERE uuid = ?
        """,
        (death_snapshot, uuid),
    )
    conn.commit()


def get_snapshot_villager_uuids(conn, snapshot_id):
    """Return the set of villager UUIDs recorded in a snapshot."""
    cur = conn.execute(
        "SELECT villager_uuid FROM villager_states WHERE snapshot_id = ?",
        (snapshot_id,),
    )
    return {row["villager_uuid"] for row in cur.fetchall()}


def get_all_snapshots(conn):
    """Return all snapshots as a list of dicts, ordered by id ascending."""
    cur = conn.execute("SELECT * FROM snapshots ORDER BY id ASC")
    return [dict(row) for row in cur.fetchall()]


def get_villager_history(conn, uuid):
    """Return all state rows for a villager, joined with snapshot timestamp."""
    cur = conn.execute(
        """
        SELECT vs.*, s.timestamp
        FROM villager_states vs
        JOIN snapshots s ON s.id = vs.snapshot_id
        WHERE vs.villager_uuid = ?
        ORDER BY s.timestamp ASC, vs.snapshot_id ASC
        """,
        (uuid,),
    )
    return [dict(row) for row in cur.fetchall()]


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

def _get_snapshot_dict(conn, snapshot_id):
    cur = conn.execute("SELECT * FROM snapshots WHERE id = ?", (snapshot_id,))
    return _row_to_dict(cur.fetchone())


def _get_villager_states_for_snapshot(conn, snapshot_id):
    cur = conn.execute(
        "SELECT * FROM villager_states WHERE snapshot_id = ?", (snapshot_id,)
    )
    return [dict(row) for row in cur.fetchall()]


def _get_trades_for_snapshot_villager(conn, snapshot_id, villager_uuid):
    cur = conn.execute(
        "SELECT * FROM villager_trades WHERE snapshot_id = ? AND villager_uuid = ?",
        (snapshot_id, villager_uuid),
    )
    return [dict(row) for row in cur.fetchall()]


def _get_inventory_for_snapshot_villager(conn, snapshot_id, villager_uuid):
    cur = conn.execute(
        "SELECT * FROM villager_inventory WHERE snapshot_id = ? AND villager_uuid = ?",
        (snapshot_id, villager_uuid),
    )
    return [dict(row) for row in cur.fetchall()]


def _get_gossip_for_snapshot_villager(conn, snapshot_id, villager_uuid):
    cur = conn.execute(
        "SELECT * FROM villager_gossip WHERE snapshot_id = ? AND villager_uuid = ?",
        (snapshot_id, villager_uuid),
    )
    return [dict(row) for row in cur.fetchall()]


def _get_beds_for_snapshot(conn, snapshot_id):
    cur = conn.execute(
        "SELECT * FROM beds WHERE snapshot_id = ?", (snapshot_id,)
    )
    return [dict(row) for row in cur.fetchall()]


def export_snapshot_json(conn, snapshot_id):
    """Return a full snapshot as a JSON-serializable dict."""
    snapshot = _get_snapshot_dict(conn, snapshot_id)
    states = _get_villager_states_for_snapshot(conn, snapshot_id)
    villagers_out = []
    for state in states:
        uuid = state["villager_uuid"]
        villagers_out.append({
            "state": state,
            "villager": get_villager(conn, uuid),
            "trades": _get_trades_for_snapshot_villager(conn, snapshot_id, uuid),
            "inventory": _get_inventory_for_snapshot_villager(conn, snapshot_id, uuid),
            "gossip": _get_gossip_for_snapshot_villager(conn, snapshot_id, uuid),
        })
    return {
        "snapshot": snapshot,
        "villagers": villagers_out,
        "beds": _get_beds_for_snapshot(conn, snapshot_id),
    }


def export_all_json(conn):
    """Return the entire database as a JSON-serializable dict."""
    snapshots = get_all_snapshots(conn)
    cur = conn.execute("SELECT * FROM villagers ORDER BY uuid")
    villagers = [dict(row) for row in cur.fetchall()]
    return {
        "snapshots": [
            export_snapshot_json(conn, s["id"]) for s in snapshots
        ],
        "villagers": villagers,
    }
