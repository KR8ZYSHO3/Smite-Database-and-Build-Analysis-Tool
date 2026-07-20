"""Export SQLite analysis to JSON for the static web GUI / GitHub Pages."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .db import DEFAULT_DB, connect
from .aspect_kit import list_god_aspects
from .conquest_builds import (
    ROLE_PROFILES,
    build_god_build,
    generate_all,
    god_scaling_bias,
    load_items,
    render_markdown,
)

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
        "live_url": (
            "https://cdn.jsdelivr.net/gh/KR8ZYSHO3/"
            "Smite-Database-and-Build-Analysis-Tool@main/docs/index.html"
        ),
        "live_url_alt": (
            "https://raw.githack.com/KR8ZYSHO3/"
            "Smite-Database-and-Build-Analysis-Tool/main/docs/index.html"
        ),
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
               p.axes_json, p.recent_axes_json,
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
        for key in ("core_items_json", "defense_items_json", "relic_suggestions", "roles",
                    "axes_json", "recent_axes_json"):
            if d.get(key):
                try:
                    parsed = json.loads(d[key])
                    if key.endswith("_json"):
                        d[key.replace("_json", "")] = parsed
                    else:
                        d[key] = parsed
                except json.JSONDecodeError:
                    pass
        # Friendly aliases for UI
        if d.get("recent_axes"):
            d["patch_axes"] = d["recent_axes"]
        elif d.get("axes"):
            d["patch_axes"] = d["axes"]
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
        # Normalize roles list for UI
        roles_raw = d.get("roles")
        if isinstance(roles_raw, str):
            try:
                roles_raw = json.loads(roles_raw)
            except json.JSONDecodeError:
                roles_raw = []
        role_names: list[str] = []
        for rr in roles_raw or []:
            s = str(rr)
            m = re.search(r"Role\.([A-Za-z]+)", s)
            role_names.append(m.group(1) if m else s)
        d["role_list"] = role_names

        # Recent balance bullets (so UI can show "what patched" without full wikitext)
        try:
            from .metrics.patch_impact import classify_stat_axes

            ab_names = [
                (a.get("name") or "").strip()
                for a in abs_
                if a.get("name") and "basic" not in (a.get("slot") or "").lower()
            ]
            ab_names = sorted({n for n in ab_names if n}, key=len, reverse=True)
            samples = []
            for x in conn.execute(
                """
                SELECT i.direction, i.magnitude, i.sample_text, i.change_count,
                       pn.name AS patch_name, pn.release_date
                FROM patch_impacts i
                JOIN patch_notes pn ON pn.id = i.patch_id
                WHERE i.entity_type = 'god' AND i.entity_name = ?
                  AND i.direction IN ('buff', 'nerf', 'shift')
                ORDER BY pn.id ASC, i.magnitude DESC
                LIMIT 14
                """,
                (d["name"],),
            ):
                row = dict(x)
                text = row.get("sample_text") or ""
                hit = None
                tl = text.lower()
                for an in ab_names:
                    if an.lower() in tl:
                        hit = an
                        break
                row["ability_hint"] = hit
                row["axes"] = classify_stat_axes(text)
                samples.append(row)
            d["patch_samples"] = samples
        except sqlite3.OperationalError:
            d["patch_samples"] = []

        # Compact kit profile for counter-build UI (tags + effects)
        try:
            bias = god_scaling_bias(conn, d["id"])
            d["kit_tags"] = sorted(bias.get("tags") or [])
            d["kit_effects"] = bias.get("effect_labels") or []
            d["kit_effect_scores"] = bias.get("effects") or {}
            d["aa_score"] = bias.get("aa_score")
            d["primary_scaling"] = bias.get("primary") or d.get("primary_scaling")
        except Exception:  # noqa: BLE001
            d.setdefault("kit_tags", [])
            d.setdefault("kit_effects", [])

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

    # Items summary + patch intel + item tier ladder
    item_patch: dict[str, dict] = {}
    try:
        for r in conn.execute(
            """
            SELECT entity_name, net_weighted_score, recent_5_score, trajectory,
                   buff_events, nerf_events, axes_json, recent_axes_json
            FROM entity_patch_summary WHERE entity_type='item'
            """
        ):
            d = dict(r)
            for jk in ("axes_json", "recent_axes_json"):
                if d.get(jk):
                    try:
                        d[jk.replace("_json", "")] = json.loads(d[jk])
                    except json.JSONDecodeError:
                        pass
            if d.get("recent_axes"):
                d["patch_axes"] = d["recent_axes"]
            elif d.get("axes"):
                d["patch_axes"] = d["axes"]
            item_patch[r["entity_name"]] = d
    except sqlite3.OperationalError:
        pass

    item_tier: dict[str, dict] = {}
    try:
        for r in conn.execute(
            """
            SELECT entity_name, tier, rank_in_scope, score, patch_score, rationale
            FROM tier_list WHERE scope='items:overall' AND entity_type='item'
            """
        ):
            item_tier[r["entity_name"]] = dict(r)
    except sqlite3.OperationalError:
        pass

    items = []
    for r in conn.execute(
        """
        SELECT name, tier, item_type, total_cost, cost, stats_text, passive, active, categories
        FROM items ORDER BY name
        """
    ):
        it = dict(r)
        p = item_patch.get(it["name"]) or {}
        t = item_tier.get(it["name"]) or {}
        it["net_weighted_score"] = p.get("net_weighted_score")
        it["recent_5_score"] = p.get("recent_5_score")
        it["trajectory"] = p.get("trajectory")
        it["buff_events"] = p.get("buff_events")
        it["nerf_events"] = p.get("nerf_events")
        it["patch_axes"] = p.get("patch_axes") or {}
        it["ladder_tier"] = t.get("tier")
        it["ladder_rank"] = t.get("rank_in_scope")
        it["ladder_score"] = t.get("score")
        it["ladder_rationale"] = t.get("rationale")
        items.append(it)

    builds = None
    builds_path = ROOT / "data" / "conquest_builds.json"
    if rebuild_builds:
        try:
            builds = generate_all(conn, gods_per_role=12)
            builds_path.write_text(json.dumps(builds, indent=2), encoding="utf-8")
            (ROOT / "data" / "conquest_builds.md").write_text(
                render_markdown(builds), encoding="utf-8"
            )
            qg = builds.get("quality_gate") or {}
            if qg:
                status = "OK" if qg.get("ok") else "WARN"
                print(f"Build quality gate: {status}")
                for role, info in (qg.get("roles") or {}).items():
                    print(
                        f"  {role}: unique {info.get('unique')}/{info.get('total')}"
                        f"  shared_groups={info.get('shared_groups', 0)}"
                    )
                for w in qg.get("warnings") or []:
                    print(f"  ! {w}")
        except Exception as exc:  # noqa: BLE001
            print(f"WARN: could not rebuild builds: {exc}")
    if builds is None and builds_path.exists():
        builds = json.loads(builds_path.read_text(encoding="utf-8"))

    # Attach per-god Conquest paths for every role they play (not only top-5 lists).
    # Magical supports also get a Mid full-damage path.
    try:
        shop_items = load_items(conn)
        by_name = {g["name"]: g for g in gods}
        for g in gods:
            roles = list(g.get("role_list") or [])
            dtype = (g.get("primary_damage_type") or "").lower()
            if "Support" in roles and dtype == "magical" and "Mid" not in roles:
                roles = roles + ["Mid"]  # full-damage option for mage guardians
            paths: dict = {}
            aspect_paths: dict = {}
            god_row = {
                "god_id": g["id"],
                "entity_name": g["name"],
                "primary_damage_type": g.get("primary_damage_type"),
                "pantheon": g.get("pantheon"),
                "tier": g.get("tier"),
                "rank_in_scope": g.get("rank_in_scope"),
                "score": g.get("score"),
            }
            aspects = list_god_aspects(conn, g["id"])
            g["aspects"] = [
                {
                    "id": a["id"],
                    "name": a["name"],
                    "description": a.get("description") or "",
                }
                for a in aspects
            ]
            for role in roles:
                if role not in ROLE_PROFILES:
                    continue
                paths[role] = build_god_build(conn, shop_items, role, god_row)
                if aspects:
                    aspect_paths[role] = build_god_build(
                        conn, shop_items, role, god_row, use_aspect=True
                    )
            g["conquest_by_role"] = paths
            if aspect_paths:
                g["conquest_by_role_aspect"] = aspect_paths
            # Drop bulky legacy lists from the main god payload confusion in UI
            # (still keep short notes + starter for tier rationale)
            if paths:
                g["build_display"] = "conquest"
    except Exception as exc:  # noqa: BLE001
        print(f"WARN: per-god conquest attach failed: {exc}")

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

    write_standalone(payload)

    conn.close()
    print(f"Exported web data → {WEB_DATA}")
    print(f"  gods: {len(gods)}  tier scopes: {len(tiers)}  items: {len(items)}")
    print(f"  standalone: {ROOT / 'docs' / 'standalone.html'}")
    return WEB_DATA


def write_standalone(payload: dict | None = None) -> Path:
    """Build a single HTML file with CSS/JS/data inlined (works on CDNs that mangle multi-file apps)."""
    docs = ROOT / "docs"
    out = docs / "standalone.html"
    html = (docs / "index.html").read_text(encoding="utf-8")
    css = (docs / "style.css").read_text(encoding="utf-8")
    js = (docs / "app.js").read_text(encoding="utf-8")
    if payload is None:
        payload = json.loads((WEB_DATA / "bundle.json").read_text(encoding="utf-8"))
    # Compact JSON for size; keep it valid for embedding in <script>
    data_js = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    # Break </script> sequences that could appear inside strings
    data_js = data_js.replace("</", "<\\/")

    html = html.replace(
        '  <!-- Static site: works on jsDelivr / Netlify / any host. Relative asset paths. -->\n'
        '  <link rel="stylesheet" href="./style.css" />',
        "  <style>\n" + css + "\n  </style>",
    )
    # Prefer the comment-less form too
    html = html.replace(
        '  <link rel="stylesheet" href="./style.css" />',
        "  <style>\n" + css + "\n  </style>",
    )
    embed = (
        "  <script>window.__SMITE2_DATA__ = "
        + data_js
        + ";</script>\n"
        "  <script>\n"
        + js
        + "\n  </script>"
    )
    html = html.replace('  <script src="./app.js"></script>', embed)
    html = html.replace(
        "Local / GitHub Pages viewer",
        "Self-contained viewer (data embedded)",
    )
    out.write_text(html, encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Export data for GitHub Pages web GUI")
    p.add_argument("--db", type=Path, default=DEFAULT_DB)
    p.add_argument("--no-rebuild-builds", action="store_true")
    args = p.parse_args(argv)
    export_web(args.db, rebuild_builds=not args.no_rebuild_builds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
