-- SMITE 2 Database Schema
-- Source: official wiki.smite2.com only (not Smite 1)

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS gods (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT NOT NULL UNIQUE,
    slug                TEXT,
    title               TEXT,
    pantheon            TEXT,
    primary_damage_type TEXT,
    roles               TEXT,          -- JSON array
    character_tags      TEXT,          -- JSON array
    type_label          TEXT,
    release_date        TEXT,
    diamonds            INTEGER,
    voice_actor         TEXT,
    wiki_url            TEXT,
    icon_path           TEXT,
    card_path           TEXT,
    lore                TEXT,
    game_id             TEXT,
    master_id           TEXT,
    patch_version       TEXT,
    base_stats_json     TEXT,          -- full baseStats object
    raw_infobox_json    TEXT,
    scraped_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS abilities (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    god_id          INTEGER NOT NULL REFERENCES gods(id) ON DELETE CASCADE,
    slot            TEXT NOT NULL,     -- Basic Attack | Passive | 1st Ability | 2nd Ability | 3rd Ability | Ultimate
    slot_order      INTEGER NOT NULL DEFAULT 0,
    name            TEXT NOT NULL,
    short_label     TEXT,
    icon            TEXT,
    description     TEXT,
    stats_text      TEXT,              -- bullet list of stats (ranks preserved)
    notes_text      TEXT,
    stats_json      TEXT,              -- parsed key/value when possible
    UNIQUE (god_id, slot, name)
);

CREATE TABLE IF NOT EXISTS items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    tier            TEXT,              -- 1 | 2 | 3 | Starter | Upgraded Starter | Relic | Curio | Consumable | God Specific
    item_type       TEXT,              -- Offensive | Defensive | Hybrid | Relic | etc.
    cost            INTEGER,
    total_cost      INTEGER,
    stats_text      TEXT,
    stats_json      TEXT,
    passive         TEXT,
    active          TEXT,
    recipe_json     TEXT,
    categories      TEXT,              -- JSON array of wiki categories
    god_specific    TEXT,              -- god name if restricted
    wiki_url        TEXT,
    image           TEXT,
    notes           TEXT,
    raw_infobox_json TEXT,
    scraped_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS patch_notes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    phase           TEXT,              -- Open Beta | Closed Alpha | Alpha Weekend
    number_label    TEXT,              -- e.g. OB39, CA8
    release_date    TEXT,
    title           TEXT,              -- e.g. The Relentless
    wiki_url        TEXT,
    previous_patch  TEXT,
    next_patch      TEXT,
    content_wikitext TEXT,
    content_text    TEXT,
    content_json    TEXT,              -- structured entries when available
    scraped_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS patch_changes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    patch_id        INTEGER NOT NULL REFERENCES patch_notes(id) ON DELETE CASCADE,
    section         TEXT,              -- God Balance | Item Balance | Gameplay | New God | etc.
    entity_name     TEXT,              -- god or item name when known
    entity_type     TEXT,              -- god | item | system | other
    change_text     TEXT NOT NULL,
    change_order    INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_gods_pantheon ON gods(pantheon);
CREATE INDEX IF NOT EXISTS idx_gods_name ON gods(name);
CREATE INDEX IF NOT EXISTS idx_abilities_god ON abilities(god_id);
CREATE INDEX IF NOT EXISTS idx_abilities_name ON abilities(name);
CREATE INDEX IF NOT EXISTS idx_items_tier ON items(tier);
CREATE INDEX IF NOT EXISTS idx_items_type ON items(item_type);
CREATE INDEX IF NOT EXISTS idx_items_name ON items(name);
CREATE INDEX IF NOT EXISTS idx_patches_phase ON patch_notes(phase);
CREATE INDEX IF NOT EXISTS idx_patch_changes_entity ON patch_changes(entity_name);
CREATE INDEX IF NOT EXISTS idx_patch_changes_patch ON patch_changes(patch_id);
