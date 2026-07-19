"""Compute per-ability and per-god kit metrics."""

from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from typing import Any

from .stat_parse import clamp, normalize_minmax, parse_ability_features, safe_div


def compute_ability_metrics(conn: sqlite3.Connection) -> dict[str, int]:
    conn.execute("DELETE FROM ability_metrics")
    conn.execute("DELETE FROM god_kit_metrics")

    rows = conn.execute(
        """
        SELECT a.id, a.god_id, a.slot, a.name, a.short_label, a.description,
               a.stats_text, a.notes_text, a.stats_json, g.name AS god_name
        FROM abilities a
        JOIN gods g ON g.id = a.god_id
        ORDER BY a.god_id, a.slot_order
        """
    ).fetchall()

    parsed: list[dict[str, Any]] = []
    for r in rows:
        try:
            stats_json = json.loads(r["stats_json"]) if r["stats_json"] else {}
        except json.JSONDecodeError:
            stats_json = {}
        feat = parse_ability_features(
            stats_json,
            r["stats_text"] or "",
            r["description"] or "",
            r["notes_text"] or "",
            r["short_label"] or "",
        )
        feat.update(
            {
                "ability_id": r["id"],
                "god_id": r["god_id"],
                "god_name": r["god_name"],
                "slot": r["slot"],
                "name": r["name"],
            }
        )
        parsed.append(feat)

    # Normalize power across all non-basic abilities
    power_raws = [p["power_raw"] for p in parsed if p["slot"] and "basic" not in p["slot"].lower()]
    # map ability_id -> normalized
    non_basic = [p for p in parsed if p["slot"] and "basic" not in p["slot"].lower()]
    norms = normalize_minmax([p["power_raw"] for p in non_basic]) if non_basic else []
    norm_map = {p["ability_id"]: norms[i] for i, p in enumerate(non_basic)} if norms else {}

    for p in parsed:
        power_score = norm_map.get(p["ability_id"])
        if power_score is None:
            # basic attacks: modest score from scaling
            power_score = clamp(
                (p["scaling_str_pct"] + p["scaling_int_pct"]) * 0.4 + 20
            )
        p["power_score"] = power_score
        conn.execute(
            """
            INSERT INTO ability_metrics (
                ability_id, god_id, slot, damage_rank5, damage_rank1,
                scaling_str_pct, scaling_int_pct, scaling_other_pct,
                cooldown_rank1, cooldown_rank5, mana_cost_rank5,
                range_m, radius_m, has_cc, has_heal, has_shield,
                has_mobility, has_dot, dps_proxy, burst_proxy,
                utility_score, power_score, metrics_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                p["ability_id"],
                p["god_id"],
                p["slot"],
                p["damage_rank5"],
                p["damage_rank1"],
                p["scaling_str_pct"],
                p["scaling_int_pct"],
                p["scaling_other_pct"],
                p["cooldown_rank1"],
                p["cooldown_rank5"],
                p["mana_cost_rank5"],
                p["range_m"],
                p["radius_m"],
                p["has_cc"],
                p["has_heal"],
                p["has_shield"],
                p["has_mobility"],
                p["has_dot"],
                p["dps_proxy"],
                p["burst_proxy"],
                p["utility_score"],
                p["power_score"],
                json.dumps({"name": p["name"], "power_raw": p["power_raw"]}),
            ),
        )

    # God kit aggregates
    by_god: dict[int, list[dict]] = defaultdict(list)
    for p in parsed:
        by_god[p["god_id"]].append(p)

    kit_raws: list[tuple[int, dict[str, float]]] = []
    for god_id, abs_ in by_god.items():
        combat = [a for a in abs_ if a["slot"] and "basic" not in a["slot"].lower()]
        ability_count = len(abs_)
        # stance variants: more than 6 total abilities often means stances
        stance_variants = max(0, ability_count - 6)

        total_dmg = sum(a["damage_rank5"] or 0 for a in combat)
        str_scales = [a["scaling_str_pct"] for a in combat if a["scaling_str_pct"]]
        int_scales = [a["scaling_int_pct"] for a in combat if a["scaling_int_pct"]]
        avg_str = sum(str_scales) / len(str_scales) if str_scales else 0.0
        avg_int = sum(int_scales) / len(int_scales) if int_scales else 0.0

        if avg_str > 15 and avg_int > 15:
            primary = "Hybrid"
        elif avg_str >= avg_int and avg_str > 5:
            primary = "Strength"
        elif avg_int > avg_str and avg_int > 5:
            primary = "Intelligence"
        else:
            primary = "Mixed"

        cds = [a["cooldown_rank5"] for a in combat if a["cooldown_rank5"]]
        min_cd = min(cds) if cds else None
        ults = [
            a
            for a in combat
            if a["slot"] and "ultimate" in a["slot"].lower()
        ]
        ult_cd = ults[0]["cooldown_rank5"] if ults and ults[0]["cooldown_rank5"] else None

        cc_count = sum(1 for a in combat if a["has_cc"])
        heal_count = sum(1 for a in combat if a["has_heal"])
        mobility_count = sum(1 for a in combat if a["has_mobility"])

        burst = sum(a["burst_proxy"] for a in combat)
        dps = sum(a["dps_proxy"] for a in combat)
        util = sum(a["utility_score"] for a in combat) / max(len(combat), 1)
        power = sum(a["power_score"] for a in combat) / max(len(combat), 1)

        # stance bonus: flexibility
        flex = min(stance_variants * 4.0, 12.0)

        kit_raws.append(
            (
                god_id,
                {
                    "ability_count": ability_count,
                    "stance_variants": stance_variants,
                    "total_damage_r5": total_dmg,
                    "avg_scaling_str": avg_str,
                    "avg_scaling_int": avg_int,
                    "primary_scaling": primary,
                    "min_ability_cd": min_cd or 0,
                    "ult_cooldown": ult_cd or 0,
                    "cc_count": cc_count,
                    "heal_count": heal_count,
                    "mobility_count": mobility_count,
                    "burst_raw": burst,
                    "dps_raw": dps,
                    "util_raw": util + flex,
                    "power_raw": power + flex * 0.5,
                },
            )
        )

    burst_n = normalize_minmax([k[1]["burst_raw"] for k in kit_raws])
    dps_n = normalize_minmax([k[1]["dps_raw"] for k in kit_raws])
    util_n = normalize_minmax([k[1]["util_raw"] for k in kit_raws])
    power_n = normalize_minmax([k[1]["power_raw"] for k in kit_raws])

    for i, (god_id, k) in enumerate(kit_raws):
        kit_burst = burst_n[i]
        kit_dps = dps_n[i]
        kit_util = util_n[i]
        # Kit power: blend of burst, sustained, utility, average ability power
        kit_power = clamp(
            0.35 * kit_burst
            + 0.30 * kit_dps
            + 0.20 * kit_util
            + 0.15 * power_n[i]
        )
        conn.execute(
            """
            INSERT INTO god_kit_metrics (
                god_id, ability_count, stance_variants, total_damage_r5,
                avg_scaling_str, avg_scaling_int, primary_scaling,
                min_ability_cd, ult_cooldown, cc_count, heal_count, mobility_count,
                kit_burst_score, kit_dps_score, kit_utility_score, kit_power_score,
                metrics_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                god_id,
                int(k["ability_count"]),
                int(k["stance_variants"]),
                k["total_damage_r5"],
                k["avg_scaling_str"],
                k["avg_scaling_int"],
                k["primary_scaling"],
                k["min_ability_cd"] or None,
                k["ult_cooldown"] or None,
                int(k["cc_count"]),
                int(k["heal_count"]),
                int(k["mobility_count"]),
                kit_burst,
                kit_dps,
                kit_util,
                kit_power,
                json.dumps(
                    {
                        "burst_raw": k["burst_raw"],
                        "dps_raw": k["dps_raw"],
                        "primary_scaling": k["primary_scaling"],
                    }
                ),
            ),
        )

    conn.commit()
    return {"abilities": len(parsed), "gods": len(kit_raws)}
