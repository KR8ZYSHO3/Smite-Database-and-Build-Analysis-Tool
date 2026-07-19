"""Export SQLite analysis to JSON for the static web GUI / GitHub Pages."""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .db import DEFAULT_DB, connect
from .conquest_builds import generate_all, render_markdown

ROOT = Path(__file__).resolve().parent.parent
WEB_DATA = ROOT / "docs" / "data"


def export_web(db_path: Path | str | None = None, rebuild_builds: bool = True) -> Path:
    conn = connect(db_path or DEFAULT_DB)
    WEB_DATA.mkdir(parents=True, exist_ok=True)

    meta = {
        "game": "SMITE 2",
        "source": "https://wiki.smite2.com",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "repo": "https://github.com/KR8ZYSHO3/Smite-Database-and-Build-Analysis-Tool",
    }
    try:
        for r in conn.execute("SELECT key, value FROM meta"):
            meta[r["key"]] = r["value"]
        for r in conn.execute("SELECT key, value FROM analysis_meta"):
            meta[f"analysis_{r['key']}"] = r["value"]
    except sqlite3.OperationalError:
        pass

    # Gods summary
    gods = []
    for r in conn.execute(
        """
        SELECT g.id, g.name, g.title, g.pantheon, g.primary_damage_type, g.roles, g.wiki_url,
               k.primary_scaling, k.avg_scaling_str, k.avg_scaling_int, k.kit_power_score,
               k.cc_count, k.heal_count, k.mobility_count,
               t.tier, t.rank_in_scope, t.score, t.patch_score, t.kit_score, t.build_score,
               t.confidence, t.rationale,
               p.trajectory, p.net_weighted_score, p.recent_5_score, p.buff_events, p.nerf_events,
               b.recommended_starter, b.core_items_json, b.defense_items_json, b.relic_suggestions,
               b.build_notes
        FROM gods g
        LEFT JOIN god_kit_metrics k ON k.god_id = g.id
        LEFT JOIN tier_list t ON t.entity_name = g.name AND t.scope = 'overall' AND t.entity_type = 'god'
        LEFT JOIN entity_patch_summary p ON p.entity_type = 'god' AND p.entity_name = g.name
        LEFT JOIN god_build_metrics b ON b.god_id = g.id
        ORDER BY g.name
        """
    ):
        d = dict(r)
        for key in ("core_items_json", "defense_items_json", "relic_suggestions", "roles"):
            if d.get(key):
                try:
                    d[key.replace("_json", "")] = json.loads(d[key])
                except json.JSONDecodeError:
                    pass
        # abilities
        abs_ = [
            dict(a)
            for a in conn.execute(
                """
                SELECT a.slot, a.name, a.description, a.stats_text,
                       m.damage_rank5, m.scaling_str_pct, m.scaling_int_pct,
                       m.cooldown_rank5, m.power_score, m.has_cc, m.has_mobility
                FROM abilities a
                LEFT JOIN ability_metrics m ON m.ability_id = a.id
                WHERE a.god_id = ?
                ORDER BY a.slot_order
                """,
                (d["id"],),
            )
        ]
        d["abilities"] = abs_
        gods.append(d)

    # Tier lists by scope
    tiers: dict[str, list] = {}
    try:
        for r in conn.execute(
            """
            SELECT scope, entity_type, entity_name, tier, rank_in_scope, score,
                   patch_score, kit_score, build_score, confidence, rationale
            FROM tier_list
            ORDER BY scope, rank_in_scope
            """
        ):
            tiers.setdefault(r["scope"], []).append(dict(r))
    except sqlite3.OperationalError:
        pass

    # Items summary
    items = [
        dict(r)
        for r in conn.execute(
            """
            SELECT name, tier, item_type, total_cost, cost, stats_text, passive, active, categories
            FROM items ORDER BY name
            """
        )
    ]

    builds = None
    builds_path = ROOT / "data" / "conquest_builds.json"
    if rebuild_builds:
        try:
            builds = generate_all(conn, gods_per_role=5)
            builds_path.write_text(json.dumps(builds, indent=2), encoding="utf-8")
            (ROOT / "data" / "conquest_builds.md").write_text(
                render_markdown(builds), encoding="utf-8"
            )
        except Exception as exc:  # noqa: BLE001
            print(f"WARN: could not rebuild builds: {exc}")
    if builds is None and builds_path.exists():
        builds = json.loads(builds_path.read_text(encoding="utf-8"))

    payload = {
        "meta": meta,
        "gods": gods,
        "tiers": tiers,
        "items": items,
        "builds": builds,
    }

    # Split for lighter loads
    (WEB_DATA / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (WEB_DATA / "tiers.json").write_text(json.dumps(tiers), encoding="utf-8")
    (WEB_DATA / "builds.json").write_text(json.dumps(builds or {}), encoding="utf-8")
    (WEB_DATA / "gods.json").write_text(json.dumps(gods), encoding="utf-8")
    (WEB_DATA / "items.json").write_text(json.dumps(items), encoding="utf-8")
    (WEB_DATA / "bundle.json").write_text(json.dumps(payload), encoding="utf-8")

    conn.close()
    print(f"Exported web data → {WEB_DATA}")
    print(f"  gods: {len(gods)}  tier scopes: {len(tiers)}  items: {len(items)}")
    return WEB_DATA


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Export data for GitHub Pages web GUI")
    p.add_argument("--db", type=Path, default=DEFAULT_DB)
    p.add_argument("--no-rebuild-builds", action="store_true")
    args = p.parse_args(argv)
    export_web(args.db, rebuild_builds=not args.no_rebuild_builds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
