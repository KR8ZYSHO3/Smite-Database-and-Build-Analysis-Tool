"""Compute per-ability and per-god kit metrics."""

from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from typing import Any

from .stat_parse import clamp, normalize_winsorized, parse_ability_features


def _is_basic(slot: str | None) -> bool:
    return bool(slot and "basic" in slot.lower())


def _is_passive(slot: str | None) -> bool:
    return bool(slot and "passive" in slot.lower())


def _is_ultimate(slot: str | None) -> bool:
    return bool(slot and "ultimate" in slot.lower())


def _is_combat_ability(slot: str | None) -> bool:
    """Non-basic, non-passive (active kit + ults)."""
    if not slot:
        return False
    if _is_basic(slot) or _is_passive(slot):
        return False
    return True


def compute_ability_metrics(conn: sqlite3.Connection) -> dict[str, int]:
    conn.execute("DELETE FROM ability_metrics")
    conn.execute("DELETE FROM god_kit_metrics")

    rows = conn.execute(
        """
        SELECT a.id, a.god_id, a.slot, a.name, a.short_label, a.description,
               a.stats_text, a.notes_text, a.stats_json, g.name AS god_name,
               g.primary_damage_type
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
                "damage_type": r["primary_damage_type"],
                "slot": r["slot"],
                "name": r["name"],
            }
        )
        parsed.append(feat)

    # Normalize power across all non-basic abilities (winsorized)
    non_basic = [p for p in parsed if p["slot"] and not _is_basic(p["slot"])]
    norms = normalize_winsorized([p["power_raw"] for p in non_basic]) if non_basic else []
    norm_map = {p["ability_id"]: norms[i] for i, p in enumerate(non_basic)} if norms else {}

    for p in parsed:
        power_score = norm_map.get(p["ability_id"])
        if power_score is None:
            # basic attacks: modest score from scaling only (don't dominate kit)
            power_score = clamp(
                (p["scaling_str_pct"] + p["scaling_int_pct"]) * 0.25 + 15
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
                json.dumps(
                    {
                        "name": p["name"],
                        "power_raw": p["power_raw"],
                        "tick_mult": p.get("tick_mult"),
                        "has_hard_cc": p.get("has_hard_cc"),
                        "has_prot_buff": p.get("has_prot_buff"),
                        "damage_parts": p.get("damage_parts") or [],
                    }
                ),
            ),
        )

    # God kit aggregates
    by_god: dict[int, list[dict]] = defaultdict(list)
    for p in parsed:
        by_god[p["god_id"]].append(p)

    # damage type lookup
    dtype_by_god = {
        r["id"]: (r["primary_damage_type"] or "").strip()
        for r in conn.execute("SELECT id, primary_damage_type FROM gods")
    }

    kit_raws: list[tuple[int, dict[str, float]]] = []
    for god_id, abs_ in by_god.items():
        # Full non-basic set for counts / stance
        non_basic_abs = [a for a in abs_ if a["slot"] and not _is_basic(a["slot"])]
        combat = [a for a in non_basic_abs if _is_combat_ability(a["slot"])]
        # Damaging abilities for scaling (combat + damaging passives)
        scaling_src = [
            a
            for a in non_basic_abs
            if (a.get("damage_rank5") or 0) > 0
            or (a.get("scaling_str_pct") or 0) + (a.get("scaling_int_pct") or 0) > 0
        ]
        # Prefer combat abilities for scaling when available
        if any(_is_combat_ability(a["slot"]) and (a.get("damage_rank5") or 0) > 0 for a in scaling_src):
            scaling_src = [
                a
                for a in scaling_src
                if _is_combat_ability(a["slot"]) and (a.get("damage_rank5") or 0) > 0
            ]

        ability_count = len(abs_)
        stance_variants = max(0, ability_count - 6)

        total_dmg = sum(a["damage_rank5"] or 0 for a in combat)

        # Weight scaling by damage contribution so small side scalings don't flip Hybrid
        w_str = 0.0
        w_int = 0.0
        w_tot = 0.0
        for a in scaling_src:
            w = max(a.get("damage_rank5") or 0.0, 1.0)
            # Ult counts half for primary scaling identity
            if _is_ultimate(a.get("slot")):
                w *= 0.5
            w_str += (a.get("scaling_str_pct") or 0.0) * w
            w_int += (a.get("scaling_int_pct") or 0.0) * w
            w_tot += w
        if w_tot > 0:
            avg_str = w_str / w_tot
            avg_int = w_int / w_tot
        else:
            str_scales = [a["scaling_str_pct"] for a in combat if a["scaling_str_pct"]]
            int_scales = [a["scaling_int_pct"] for a in combat if a["scaling_int_pct"]]
            avg_str = sum(str_scales) / len(str_scales) if str_scales else 0.0
            avg_int = sum(int_scales) / len(int_scales) if int_scales else 0.0

        dtype = (dtype_by_god.get(god_id) or "").lower()
        # Damage type is itemization truth; only allow Hybrid when both scales matter
        if dtype == "magical":
            if avg_int >= 15 and avg_str >= avg_int * 0.85 and avg_str >= 40:
                primary = "Hybrid"
            elif avg_int > 5 or avg_str > 5:
                primary = "Intelligence"
            else:
                primary = "Intelligence"
        elif dtype == "physical":
            if avg_str >= 15 and avg_int >= avg_str * 0.85 and avg_int >= 40:
                primary = "Hybrid"
            elif avg_str > 5 or avg_int > 5:
                primary = "Strength"
            else:
                primary = "Strength"
        else:
            if avg_str > 15 and avg_int > 15 and min(avg_str, avg_int) / max(avg_str, avg_int, 1) > 0.55:
                primary = "Hybrid"
            elif avg_str >= avg_int and avg_str > 5:
                primary = "Strength"
            elif avg_int > avg_str and avg_int > 5:
                primary = "Intelligence"
            else:
                primary = "Mixed"

        cds = [
            a["cooldown_rank5"]
            for a in combat
            if a["cooldown_rank5"] and not _is_ultimate(a.get("slot"))
        ]
        min_cd = min(cds) if cds else None
        ults = [a for a in combat if _is_ultimate(a.get("slot"))]
        ult_cd = ults[0]["cooldown_rank5"] if ults and ults[0]["cooldown_rank5"] else None

        cc_count = sum(1 for a in non_basic_abs if a["has_cc"])
        heal_count = sum(1 for a in non_basic_abs if a["has_heal"])
        mobility_count = sum(1 for a in non_basic_abs if a["has_mobility"])

        # Soft-cap each ability before summing so one ult doesn't dominate the roster
        def softcap(x: float, cap: float = 2500.0) -> float:
            if x <= cap:
                return x
            return cap + (x - cap) * 0.25

        burst = 0.0
        dps = 0.0
        for a in non_basic_abs:
            bw = 1.0
            if _is_ultimate(a.get("slot")):
                bw = 0.55  # ult less than full kit spam for "kit power"
            if _is_passive(a.get("slot")):
                bw = 0.35
            burst += softcap(a.get("burst_proxy") or 0.0) * bw
            dps += softcap(a.get("dps_proxy") or 0.0, cap=200.0) * bw

        util = sum(a["utility_score"] for a in non_basic_abs) / max(len(non_basic_abs), 1)
        power = sum(a["power_score"] for a in combat) / max(len(combat), 1) if combat else (
            sum(a["power_score"] for a in non_basic_abs) / max(len(non_basic_abs), 1)
        )

        flex = min(stance_variants * 4.0, 12.0)

        # AA-kit bonus: abilities that buff basic attacks are undercounted on raw ability dmg
        aa_hits = 0
        for a in non_basic_abs:
            blob = " ".join(
                str(x)
                for x in (
                    a.get("name"),
                    # features don't carry description; use power from AS-style low dmg high util
                )
            )
            # Heuristic: low/no damage ability with short CD often AS steroid (Rama 2, etc.)
            dmg = a.get("damage_rank5") or 0
            cd = a.get("cooldown_rank5") or 12
            if dmg < 80 and cd and cd <= 16 and not _is_ultimate(a.get("slot")):
                # passive AS / AA packs show as utility without damage
                if (a.get("utility_score") or 0) >= 15 or dmg == 0:
                    aa_hits += 0.5
        # Stronger signal from god ability text would need join; use count of zero-damage combat abs
        zero_dmg_combat = sum(
            1
            for a in combat
            if not _is_ultimate(a.get("slot")) and (a.get("damage_rank5") or 0) < 40
        )
        aa_bonus = 0.0
        if zero_dmg_combat >= 1 and avg_str >= 40 and dtype == "physical":
            aa_bonus = 180.0 + zero_dmg_combat * 60.0  # lifts Rama/Apollo-class kits
        elif zero_dmg_combat >= 2 and dtype == "physical":
            aa_bonus = 120.0

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
                    "burst_raw": burst + aa_bonus * 0.35,
                    "dps_raw": dps + aa_bonus,
                    "util_raw": util + flex,
                    "power_raw": power + flex * 0.5 + (8 if aa_bonus else 0),
                    "damage_type": dtype_by_god.get(god_id),
                    "aa_bonus": aa_bonus,
                },
            )
        )

    burst_n = normalize_winsorized([k[1]["burst_raw"] for k in kit_raws])
    dps_n = normalize_winsorized([k[1]["dps_raw"] for k in kit_raws])
    util_n = normalize_winsorized([k[1]["util_raw"] for k in kit_raws])
    power_n = normalize_winsorized([k[1]["power_raw"] for k in kit_raws])

    for i, (god_id, k) in enumerate(kit_raws):
        kit_burst = burst_n[i]
        kit_dps = dps_n[i]
        kit_util = util_n[i]
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
                        "damage_type": k.get("damage_type"),
                        "normalize": "winsorized_5_95",
                    }
                ),
            ),
        )

    conn.commit()
    return {"abilities": len(parsed), "gods": len(kit_raws)}
