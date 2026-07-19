"""Composite tier list from patch momentum, kit power, and build synergy."""

from __future__ import annotations

import json
import re
import sqlite3
from typing import Any

from .stat_parse import clamp, normalize_minmax


# Default weights — patch notes dominate by design
WEIGHTS = {
    "patch": 0.48,
    "kit": 0.28,
    "build": 0.14,
    "novelty": 0.05,
    "stability": 0.05,
}


def _percentile_tiers(scores: list[float]) -> list[str]:
    """
    Assign S/A/B/C/D by percentile within the scored group.
    S: top 12%, A: next 20%, B: next 28%, C: next 25%, D: bottom 15%
    """
    if not scores:
        return []
    indexed = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    n = len(scores)
    tiers = [""] * n
    for rank, (idx, _) in enumerate(indexed):
        pct = rank / max(n - 1, 1)
        if pct <= 0.12:
            tiers[idx] = "S"
        elif pct <= 0.32:
            tiers[idx] = "A"
        elif pct <= 0.60:
            tiers[idx] = "B"
        elif pct <= 0.85:
            tiers[idx] = "C"
        else:
            tiers[idx] = "D"
    return tiers


def _parse_roles(roles_json: str | None) -> list[str]:
    if not roles_json:
        return ["Unknown"]
    try:
        data = json.loads(roles_json)
    except json.JSONDecodeError:
        return [roles_json]
    out = []
    for r in data if isinstance(data, list) else [data]:
        s = str(r)
        # ItemStore.Filter.Role.Carry.STR -> Carry
        m = re.search(r"Role\.([A-Za-z]+)", s)
        if m:
            out.append(m.group(1))
        elif s and not s.startswith("ItemStore"):
            out.append(s)
    return out or ["Unknown"]


def compute_tier_lists(conn: sqlite3.Connection, weights: dict[str, float] | None = None) -> dict[str, int]:
    w = {**WEIGHTS, **(weights or {})}
    conn.execute("DELETE FROM tier_list")

    rows = conn.execute(
        """
        SELECT
            g.id AS god_id,
            g.name,
            g.pantheon,
            g.roles,
            g.primary_damage_type,
            g.release_date,
            k.kit_power_score,
            k.kit_burst_score,
            k.kit_dps_score,
            k.kit_utility_score,
            k.primary_scaling,
            k.cc_count,
            k.ability_count,
            b.build_synergy_score,
            b.meta_item_score,
            b.recommended_starter,
            b.core_items_json,
            b.build_notes,
            p.net_weighted_score,
            p.recent_5_score,
            p.recent_10_score,
            p.buff_events,
            p.nerf_events,
            p.patches_touched,
            p.trajectory,
            p.last_direction,
            p.last_patch,
            p.new_events
        FROM gods g
        LEFT JOIN god_kit_metrics k ON k.god_id = g.id
        LEFT JOIN god_build_metrics b ON b.god_id = g.id
        LEFT JOIN entity_patch_summary p
            ON p.entity_type = 'god' AND p.entity_name = g.name
        """
    ).fetchall()

    # Component vectors for normalization
    patch_vals = []
    for r in rows:
        # Emphasize recent patches inside patch component.
        # Gods never mentioned in patches get a neutral 0 (not a penalty pile-on);
        # only real buff/nerf momentum moves them.
        if not r["patches_touched"]:
            base = 0.0  # neutral before normalization anchors
        else:
            base = (
                (r["net_weighted_score"] or 0.0) * 0.35
                + (r["recent_10_score"] or 0.0) * 0.25
                + (r["recent_5_score"] or 0.0) * 0.40
            )
        patch_vals.append(base)

    kit_vals = [r["kit_power_score"] or 40.0 for r in rows]
    build_vals = [
        0.55 * (r["build_synergy_score"] or 40.0) + 0.45 * (r["meta_item_score"] or 40.0)
        for r in rows
    ]
    # novelty: newly released / new_events
    novelty_raw = []
    for r in rows:
        n = 0.0
        if r["new_events"]:
            n += min(r["new_events"], 3) * 15
        if r["trajectory"] == "new":
            n += 25
        # recently added gods often missing old balance history — slight bump for visibility
        if (r["patches_touched"] or 0) <= 2:
            n += 10
        novelty_raw.append(n)

    # stability: not thrashing; mild bonus for stable strong kits after buffs
    stability_raw = []
    for r in rows:
        buffs = r["buff_events"] or 0
        nerfs = r["nerf_events"] or 0
        traj = r["trajectory"] or "stable"
        if traj == "stable":
            s = 70.0
        elif traj == "rising":
            s = 85.0
        elif traj == "falling":
            s = 35.0
        elif traj == "volatile":
            s = 40.0
        elif traj == "new":
            s = 55.0
        else:
            s = 50.0
        if buffs + nerfs == 0:
            s = 60.0  # unmentioned — average trust
        stability_raw.append(s)

    patch_n = normalize_minmax(patch_vals)
    # kit already 0-100-ish; re-normalize for fairness
    kit_n = normalize_minmax(kit_vals)
    build_n = normalize_minmax(build_vals)
    novelty_n = normalize_minmax(novelty_raw)
    stability_n = normalize_minmax(stability_raw)

    scored: list[dict[str, Any]] = []
    for i, r in enumerate(rows):
        score = (
            w["patch"] * patch_n[i]
            + w["kit"] * kit_n[i]
            + w["build"] * build_n[i]
            + w["novelty"] * novelty_n[i]
            + w["stability"] * stability_n[i]
        )
        # Confidence: more patch + ability data → higher
        conf = 0.35
        conf += min((r["patches_touched"] or 0) / 10.0, 0.35)
        conf += 0.15 if (r["ability_count"] or 0) >= 5 else 0.05
        conf += 0.15 if r["kit_power_score"] is not None else 0.0
        conf = clamp(conf, 0, 1)

        rationale_parts = []
        traj = r["trajectory"] or "unknown"
        rationale_parts.append(f"Patch trajectory: {traj}")
        if r["last_patch"]:
            rationale_parts.append(f"Last touch: {r['last_direction']} in {r['last_patch']}")
        rationale_parts.append(
            f"Kit {kit_n[i]:.0f}/100 (burst/dps/utility blend), build fit {build_n[i]:.0f}/100"
        )
        if r["recent_5_score"]:
            sign = "buffed" if r["recent_5_score"] > 0 else "nerfed" if r["recent_5_score"] < 0 else "touched"
            rationale_parts.append(f"Last 5 patches net {sign} (score {r['recent_5_score']:+.2f})")
        if r["core_items_json"]:
            try:
                cores = json.loads(r["core_items_json"])[:3]
                if cores:
                    rationale_parts.append("Suggested cores: " + ", ".join(cores))
            except json.JSONDecodeError:
                pass

        roles = _parse_roles(r["roles"])
        scored.append(
            {
                "god_id": r["god_id"],
                "name": r["name"],
                "pantheon": r["pantheon"],
                "roles": roles,
                "damage_type": r["primary_damage_type"],
                "score": score,
                "patch_score": patch_n[i],
                "kit_score": kit_n[i],
                "build_score": build_n[i],
                "novelty_score": novelty_n[i],
                "stability_score": stability_n[i],
                "confidence": conf,
                "rationale": "; ".join(rationale_parts),
                "components": {
                    "weights": w,
                    "raw_patch": patch_vals[i],
                    "trajectory": traj,
                    "buff_events": r["buff_events"] or 0,
                    "nerf_events": r["nerf_events"] or 0,
                    "primary_scaling": r["primary_scaling"],
                    "starter": r["recommended_starter"],
                },
            }
        )

    # Overall tier list
    _write_scope(conn, "overall", scored)

    # Per-role tier lists
    role_map: dict[str, list[dict]] = {}
    for s in scored:
        for role in s["roles"]:
            role_map.setdefault(role, []).append(s)
    for role, group in role_map.items():
        if len(group) < 3:
            continue
        _write_scope(conn, f"role:{role}", group)

    # Per damage type
    for dtype in sorted({s["damage_type"] for s in scored if s["damage_type"]}):
        group = [s for s in scored if s["damage_type"] == dtype]
        if len(group) >= 5:
            _write_scope(conn, f"damage:{dtype}", group)

    # Per pantheon (optional, if enough gods)
    for pan in sorted({s["pantheon"] for s in scored if s["pantheon"]}):
        group = [s for s in scored if s["pantheon"] == pan]
        if len(group) >= 4:
            _write_scope(conn, f"pantheon:{pan}", group)

    # Item tier list from patch momentum + cost efficiency
    _item_tier_list(conn)

    conn.commit()
    n = conn.execute("SELECT COUNT(*) AS c FROM tier_list").fetchone()["c"]
    return {"tier_rows": n, "gods_scored": len(scored)}


def _write_scope(conn: sqlite3.Connection, scope: str, group: list[dict[str, Any]]) -> None:
    scores = [g["score"] for g in group]
    tiers = _percentile_tiers(scores)
    order = sorted(range(len(group)), key=lambda i: group[i]["score"], reverse=True)
    rank_of = {idx: rank + 1 for rank, idx in enumerate(order)}
    for i, g in enumerate(group):
        conn.execute(
            """
            INSERT INTO tier_list (
                scope, entity_type, entity_name, god_id, tier, rank_in_scope,
                score, patch_score, kit_score, build_score, novelty_score,
                confidence, rationale, components_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(scope, entity_type, entity_name) DO UPDATE SET
                tier=excluded.tier,
                rank_in_scope=excluded.rank_in_scope,
                score=excluded.score,
                patch_score=excluded.patch_score,
                kit_score=excluded.kit_score,
                build_score=excluded.build_score,
                novelty_score=excluded.novelty_score,
                confidence=excluded.confidence,
                rationale=excluded.rationale,
                components_json=excluded.components_json,
                generated_at=datetime('now')
            """,
            (
                scope,
                "god",
                g["name"],
                g["god_id"],
                tiers[i],
                rank_of[i],
                g["score"],
                g["patch_score"],
                g["kit_score"],
                g["build_score"],
                g["novelty_score"],
                g["confidence"],
                g["rationale"],
                json.dumps(g["components"]),
            ),
        )


def _item_tier_list(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """
        SELECT i.name, i.tier, i.item_type, i.total_cost,
               COALESCE(p.net_weighted_score, 0) AS net_w,
               COALESCE(p.recent_5_score, 0) AS r5,
               COALESCE(p.buff_events, 0) AS buffs,
               COALESCE(p.nerf_events, 0) AS nerfs,
               COALESCE(p.trajectory, 'stable') AS trajectory
        FROM items i
        LEFT JOIN entity_patch_summary p
            ON p.entity_type = 'item' AND p.entity_name = i.name
        WHERE i.tier = '3' OR i.item_type IN ('Offensive','Defensive','Hybrid')
        """
    ).fetchall()
    if not rows:
        return

    raw = []
    for r in rows:
        # item score: patch momentum primary
        s = (r["net_w"] or 0) * 0.5 + (r["r5"] or 0) * 0.5
        # small efficiency nudge
        cost = r["total_cost"] or 2500
        if 2200 <= cost <= 2700:
            s += 0.15
        raw.append(s)
    norms = normalize_minmax(raw)
    group = []
    for i, r in enumerate(rows):
        group.append(
            {
                "name": r["name"],
                "score": norms[i],
                "patch_score": norms[i],
                "kit_score": None,
                "build_score": None,
                "novelty_score": None,
                "confidence": 0.55 if (r["buffs"] + r["nerfs"]) > 0 else 0.35,
                "rationale": f"Item patch trajectory: {r['trajectory']}; net weighted {r['net_w']:+.2f}",
                "god_id": None,
                "components": {
                    "total_cost": r["total_cost"],
                    "item_type": r["item_type"],
                    "tier": r["tier"],
                },
            }
        )
    scores = [g["score"] for g in group]
    tiers = _percentile_tiers(scores)
    order = sorted(range(len(group)), key=lambda i: group[i]["score"], reverse=True)
    rank_of = {idx: rank + 1 for rank, idx in enumerate(order)}
    for i, g in enumerate(group):
        conn.execute(
            """
            INSERT INTO tier_list (
                scope, entity_type, entity_name, god_id, tier, rank_in_scope,
                score, patch_score, kit_score, build_score, novelty_score,
                confidence, rationale, components_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(scope, entity_type, entity_name) DO UPDATE SET
                tier=excluded.tier,
                rank_in_scope=excluded.rank_in_scope,
                score=excluded.score,
                patch_score=excluded.patch_score,
                rationale=excluded.rationale,
                components_json=excluded.components_json,
                generated_at=datetime('now')
            """,
            (
                "items:overall",
                "item",
                g["name"],
                None,
                tiers[i],
                rank_of[i],
                g["score"],
                g["patch_score"],
                None,
                None,
                None,
                g["confidence"],
                g["rationale"],
                json.dumps(g["components"]),
            ),
        )
