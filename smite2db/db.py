"""SQLite helpers for the SMITE 2 database."""

from __future__ import annotations

import sqlite3
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "smite2.db"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.sql"


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else DEFAULT_DB
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema)
    # Forward-compatible migrations for existing DBs
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS god_aspects (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            god_id          INTEGER NOT NULL REFERENCES gods(id) ON DELETE CASCADE,
            name            TEXT NOT NULL,
            description     TEXT,
            image           TEXT,
            raw_json        TEXT,
            scraped_at      TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE (god_id, name)
        );
        CREATE TABLE IF NOT EXISTS god_aspect_abilities (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            aspect_id       INTEGER NOT NULL REFERENCES god_aspects(id) ON DELETE CASCADE,
            slot            TEXT NOT NULL,
            slot_order      INTEGER NOT NULL DEFAULT 0,
            name            TEXT NOT NULL,
            short_label     TEXT,
            icon            TEXT,
            description     TEXT,
            stats_text      TEXT,
            notes_text      TEXT,
            stats_json      TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_god_aspects_god ON god_aspects(god_id);
        CREATE INDEX IF NOT EXISTS idx_god_aspect_abilities_aspect ON god_aspect_abilities(aspect_id);
        """
    )
    conn.commit()


def reset_content_tables(conn: sqlite3.Connection) -> None:
    """Clear scraped content (keeps schema)."""
    for table in (
        "patch_changes",
        "god_aspect_abilities",
        "god_aspects",
        "abilities",
        "items",
        "patch_notes",
        "gods",
        "meta",
    ):
        try:
            conn.execute(f"DELETE FROM {table}")
        except sqlite3.OperationalError:
            pass
    conn.commit()


def set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO meta(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
