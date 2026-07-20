-- Analytics tables for ability / build / patch metrics and tier lists
-- Populated by: python -m smite2db.analyze

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS ability_metrics (
    ability_id          INTEGER PRIMARY KEY REFERENCES abilities(id) ON DELETE CASCADE,
    god_id              INTEGER NOT NULL,
    slot                TEXT,
    damage_rank5        REAL,          -- highest rank base damage if present
    damage_rank1        REAL,
    scaling_str_pct     REAL,          -- Strength scaling %
    scaling_int_pct     REAL,          -- Intelligence scaling %
    scaling_other_pct   REAL,
    cooldown_rank1      REAL,
    cooldown_rank5      REAL,
    mana_cost_rank5     REAL,
    range_m             REAL,
    radius_m            REAL,
    has_cc              INTEGER NOT NULL DEFAULT 0,
    has_heal            INTEGER NOT NULL DEFAULT 0,
    has_shield          INTEGER NOT NULL DEFAULT 0,
    has_mobility        INTEGER NOT NULL DEFAULT 0,
    has_dot             INTEGER NOT NULL DEFAULT 0,
    dps_proxy           REAL,          -- damage/cooldown heuristic at rank 5
    burst_proxy         REAL,          -- raw rank-5 damage * (1 + scaling/100)
    utility_score       REAL,          -- 0-100 composite of CC/heal/mobility
    power_score         REAL,          -- 0-100 offensive power of this ability
    metrics_json        TEXT,
    computed_at         TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS god_kit_metrics (
    god_id              INTEGER PRIMARY KEY REFERENCES gods(id) ON DELETE CASCADE,
    ability_count       INTEGER,
    stance_variants     INTEGER,
    total_damage_r5     REAL,
    avg_scaling_str     REAL,
    avg_scaling_int     REAL,
    primary_scaling     TEXT,          -- Strength | Intelligence | Hybrid | Mixed
    min_ability_cd      REAL,
    ult_cooldown        REAL,
    cc_count            INTEGER,
    heal_count          INTEGER,
    mobility_count      INTEGER,
    kit_burst_score     REAL,          -- 0-100
    kit_dps_score       REAL,          -- 0-100
    kit_utility_score   REAL,          -- 0-100
    kit_power_score     REAL,          -- 0-100 weighted kit strength
    metrics_json        TEXT,
    computed_at         TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS patch_impacts (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    patch_id            INTEGER NOT NULL REFERENCES patch_notes(id) ON DELETE CASCADE,
    entity_type         TEXT NOT NULL,  -- god | item
    entity_name         TEXT NOT NULL,
    direction           TEXT NOT NULL,  -- buff | nerf | shift | new | fix | neutral
    magnitude           REAL NOT NULL DEFAULT 1.0,
    weighted_score      REAL NOT NULL,  -- direction * magnitude * recency_weight
    recency_weight      REAL NOT NULL,
    change_count        INTEGER NOT NULL DEFAULT 1,
    sample_text         TEXT,
    UNIQUE (patch_id, entity_type, entity_name, direction)
);

CREATE TABLE IF NOT EXISTS entity_patch_summary (
    entity_type         TEXT NOT NULL,
    entity_name         TEXT NOT NULL,
    patches_touched     INTEGER NOT NULL DEFAULT 0,
    buff_events         INTEGER NOT NULL DEFAULT 0,
    nerf_events         INTEGER NOT NULL DEFAULT 0,
    shift_events        INTEGER NOT NULL DEFAULT 0,
    new_events          INTEGER NOT NULL DEFAULT 0,
    net_raw_score       REAL NOT NULL DEFAULT 0,
    net_weighted_score  REAL NOT NULL DEFAULT 0,  -- recency-weighted momentum
    recent_5_score      REAL NOT NULL DEFAULT 0,  -- last 5 patches only
    recent_10_score     REAL NOT NULL DEFAULT 0,
    last_direction      TEXT,
    last_patch          TEXT,
    last_patch_date     TEXT,
    trajectory          TEXT,          -- rising | falling | stable | volatile | new
    axes_json           TEXT,          -- {"damage":1.2,"cooldown":-0.4,...} recency-weighted
    recent_axes_json    TEXT,          -- same axes, last 5 patches only
    PRIMARY KEY (entity_type, entity_name)
);

CREATE TABLE IF NOT EXISTS god_build_metrics (
    god_id              INTEGER PRIMARY KEY REFERENCES gods(id) ON DELETE CASCADE,
    damage_type         TEXT,
    primary_scaling     TEXT,
    recommended_starter TEXT,
    core_items_json     TEXT,          -- top offensive cores
    defense_items_json  TEXT,
    hybrid_items_json   TEXT,
    relic_suggestions   TEXT,
    build_synergy_score REAL,          -- 0-100 how well shop matches kit
    meta_item_score     REAL,          -- cores recently buffed / not nerfed
    build_notes         TEXT,
    metrics_json        TEXT,
    computed_at         TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tier_list (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    scope               TEXT NOT NULL,  -- overall | role:Mid | pantheon:Greek | ...
    entity_type         TEXT NOT NULL DEFAULT 'god',
    entity_name         TEXT NOT NULL,
    god_id              INTEGER,
    tier                TEXT NOT NULL,  -- S | A | B | C | D
    rank_in_scope       INTEGER,
    score               REAL NOT NULL,
    patch_score         REAL,
    kit_score           REAL,
    build_score         REAL,
    novelty_score       REAL,
    confidence          REAL,          -- 0-1 data confidence
    rationale           TEXT,
    components_json     TEXT,
    generated_at        TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (scope, entity_type, entity_name)
);

CREATE TABLE IF NOT EXISTS analysis_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_patch_impacts_entity ON patch_impacts(entity_type, entity_name);
CREATE INDEX IF NOT EXISTS idx_tier_list_scope ON tier_list(scope, tier, rank_in_scope);
CREATE INDEX IF NOT EXISTS idx_ability_metrics_god ON ability_metrics(god_id);
