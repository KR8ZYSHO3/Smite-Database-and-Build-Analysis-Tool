"""Recommend builds from item stats + patch item momentum + god scaling."""

from __future__ import annotations

import json
import re
import sqlite3
from typing import Any

from .stat_parse import clamp, normalize_minmax


def _item_stat_map(stats_json: str | None) -> dict[str, float]:
    if not stats_json:
        return {}
    try:
        arr = json.loads(stats_json)
    except json.JSONDecodeError:
        return {}
    out: dict[str, float] = {}
    if not isinstance(arr, list):
        return out
    for entry in arr:
        if not isinstance(entry, dict):
            continue
        name = (entry.get("stat") or "").strip()
        raw = str(entry.get("value") or "")
        m = re.search(r"-?\d+(?:\.\d+)?", raw.replace(",", ""))
        if name and m:
            out[name.lower()] = float(m.group())
    return out


def _item_tags(row) -> set[str]:
    tags = set()
    for field in (row["categories"], row["item_type"], row["passive"], row["active"], row["stats_text"]):
        if not field:
            continue
        tags.add(str(field).lower())
    blob = " ".join(tags)
    flags = set()
    if "strength" in blob or re.search(r"\bstr\b", blob):
        flags.add("str")
    if "intelligence" in blob or re.search(r"\bint\b", blob):
        flags.add("int")
    if "lifesteal" in blob or "ls" in blob:
        flags.add("ls")
    if "crit" in blob:
        flags.add("crit")
    if "pen" in blob or "penetration" in blob:
        flags.add("pen")
    if "cooldown" in blob or "cdr" in blob or "haste" in blob:
        flags.add("cdr")
    if "attack speed" in blob or "as" in blob:
        flags.add("as")
    if "physical protection" in blob or "magical protection" in blob or "prot" in blob:
        flags.add("prot")
    if "health" in blob or "hp" in blob:
        flags.add("hp")
    if "offensive" in blob:
        flags.add("offensive")
    if "defensive" in blob:
        flags.add("defensive")
    if "hybrid" in blob:
        flags.add("hybrid")
    if "starter" in blob:
        flags.add("starter")
    if row["active"]:
        flags.add("active")
    if row["passive"]:
        flags.add("passive")
    return flags


def compute_build_metrics(conn: sqlite3.Connection) -> dict[str, int]:
    conn.execute("DELETE FROM god_build_metrics")

    items = conn.execute(
        """
        SELECT id, name, tier, item_type, cost, total_cost, stats_json, stats_text,
               passive, active, categories
        FROM items
        WHERE tier IN ('1','2','3','Starter','Upgraded Starter')
           OR item_type IN ('Offensive','Defensive','Hybrid','Starter','Relic')
           OR categories LIKE '%Starter%'
           OR categories LIKE '%Offensive%'
           OR categories LIKE '%Defensive%'
           OR categories LIKE '%Hybrid%'
           OR categories LIKE '%Relic%'
        """
    ).fetchall()

    # Item patch momentum
    item_momentum = {
        r["entity_name"]: r["net_weighted_score"]
        for r in conn.execute(
            "SELECT entity_name, net_weighted_score FROM entity_patch_summary WHERE entity_type='item'"
        )
    }

    catalog: list[dict[str, Any]] = []
    for it in items:
        stats = _item_stat_map(it["stats_json"])
        tags = _item_tags(it)
        # infer str/int from parsed stats
        if "str" in stats or any(k.startswith("str") for k in stats):
            tags.add("str")
        if "int" in stats or "intelligence" in " ".join(stats.keys()):
            tags.add("int")
        for k, v in stats.items():
            kl = k.lower()
            if kl in ("str", "strength"):
                tags.add("str")
            if kl in ("int", "intelligence"):
                tags.add("int")
            if "lifesteal" in kl or kl == "ls":
                tags.add("ls")
            if "crit" in kl:
                tags.add("crit")
            if "pen" in kl:
                tags.add("pen")
            if "cooldown" in kl or kl in ("cdr", "haste"):
                tags.add("cdr")
            if "attack speed" in kl or kl == "as":
                tags.add("as")
            if "prot" in kl:
                tags.add("prot")
            if "health" in kl or kl in ("hp", "max health"):
                tags.add("hp")

        tier = str(it["tier"] or "")
        is_starter = "starter" in (it["categories"] or "").lower() or tier in (
            "Starter",
            "Upgraded Starter",
        )
        is_t3 = tier == "3" or (it["item_type"] in ("Offensive", "Defensive", "Hybrid") and (it["total_cost"] or 0) >= 2200)
        is_relic = "relic" in (it["categories"] or "").lower() or it["item_type"] == "Relic" or tier == "Relic"

        catalog.append(
            {
                "name": it["name"],
                "tier": tier,
                "item_type": it["item_type"],
                "total_cost": it["total_cost"] or it["cost"] or 0,
                "tags": tags,
                "stats": stats,
                "is_starter": is_starter,
                "is_t3": is_t3 and not is_starter,
                "is_relic": is_relic,
                "momentum": item_momentum.get(it["name"], 0.0),
                "offensive_power": _offensive_power(stats, tags),
                "defensive_power": _defensive_power(stats, tags),
            }
        )

    gods = conn.execute(
        """
        SELECT g.id, g.name, g.primary_damage_type, g.roles, k.primary_scaling,
               k.avg_scaling_str, k.avg_scaling_int, k.kit_power_score,
               k.cc_count, k.heal_count, k.mobility_count
        FROM gods g
        LEFT JOIN god_kit_metrics k ON k.god_id = g.id
        """
    ).fetchall()

    synergy_raws: list[float] = []
    meta_raws: list[float] = []
    records: list[dict[str, Any]] = []

    for g in gods:
        scaling = g["primary_scaling"] or "Mixed"
        dtype = (g["primary_damage_type"] or "").strip()
        # Damage type is the itemization truth. Basics can inflate STR% on magical
        # guardians (e.g. Ymir Hybrid numbers) without meaning physical cores.
        if dtype.lower() == "magical":
            prefer_int, prefer_str = True, False
        elif dtype.lower() == "physical":
            prefer_str, prefer_int = True, False
        else:
            prefer_str = scaling == "Strength" or (
                scaling in ("Hybrid", "Mixed")
                and (g["avg_scaling_str"] or 0) > (g["avg_scaling_int"] or 0)
            )
            prefer_int = scaling == "Intelligence" or (
                scaling in ("Hybrid", "Mixed")
                and (g["avg_scaling_int"] or 0) >= (g["avg_scaling_str"] or 0)
            )
            if prefer_str and prefer_int:
                prefer_int = (g["avg_scaling_int"] or 0) >= (g["avg_scaling_str"] or 0)
                prefer_str = not prefer_int

        def score_item(it: dict, role: str) -> float:
            s = 0.0
            tags = it["tags"]
            if role == "offense":
                s += it["offensive_power"]
                if prefer_str and "str" in tags:
                    s += 25
                if prefer_int and "int" in tags:
                    s += 25
                if prefer_str and "int" in tags and "str" not in tags:
                    s -= 25
                if prefer_int and "str" in tags and "int" not in tags:
                    s -= 25
                # Magical gods should never rank Avatar's Parashu / pure STR actives as cores
                if prefer_int and "str" in tags and "int" not in tags:
                    s -= 30
                if prefer_str and "int" in tags and "str" not in tags:
                    s -= 30
                if "pen" in tags:
                    s += 12
                if "cdr" in tags:
                    s += 8
                if "ls" in tags:
                    s += 6
                if "crit" in tags and prefer_str:
                    s += 8
                if "as" in tags and prefer_str:
                    s += 5
            elif role == "defense":
                s += it["defensive_power"]
                if "prot" in tags:
                    s += 20
                if "hp" in tags:
                    s += 15
                if "cdr" in tags:
                    s += 5
            else:  # hybrid/support
                s += 0.5 * it["offensive_power"] + 0.5 * it["defensive_power"]
                if "hybrid" in tags:
                    s += 15
                if g["heal_count"] and ("heal" in " ".join(tags) or "hp" in tags):
                    s += 10
            s += it["momentum"] * 8  # patch-favored items
            # cost efficiency mild preference for 2400-2800 cores
            cost = it["total_cost"]
            if 2300 <= cost <= 2800:
                s += 5
            return s

        starters = [it for it in catalog if it["is_starter"] and it["tier"] in ("1", "Starter", "")]
        # also categories starter with tier 1
        starters = [it for it in catalog if it["is_starter"] and (it["total_cost"] or 0) < 1200]
        if not starters:
            starters = [it for it in catalog if it["is_starter"]]

        t3_off = [
            it
            for it in catalog
            if it["is_t3"]
            and (
                "offensive" in it["tags"]
                or it["item_type"] == "Offensive"
                or (it["offensive_power"] > it["defensive_power"] and it["offensive_power"] > 5)
            )
        ]
        t3_def = [
            it
            for it in catalog
            if it["is_t3"]
            and (
                "defensive" in it["tags"]
                or it["item_type"] == "Defensive"
                or (it["defensive_power"] > it["offensive_power"] and it["defensive_power"] > 5)
            )
        ]
        t3_hyb = [it for it in catalog if it["is_t3"] and ("hybrid" in it["tags"] or it["item_type"] == "Hybrid")]
        relics = [it for it in catalog if it["is_relic"] and (it["total_cost"] or 0) <= 0]

        # Prefer scaling-aligned items strongly when ranking cores
        def core_key(it: dict) -> float:
            s = score_item(it, "offense")
            # Penalize ultra-expensive outliers slightly so every INT god isn't Idol-only
            if (it["total_cost"] or 0) >= 3400:
                s -= 12
            return s

        starters_s = sorted(starters, key=lambda x: score_item(x, "offense"), reverse=True)
        cores = sorted(t3_off, key=core_key, reverse=True)[:6]
        defs = sorted(t3_def, key=lambda x: score_item(x, "defense"), reverse=True)[:4]
        hybs = sorted(t3_hyb, key=lambda x: score_item(x, "hybrid"), reverse=True)[:3]
        relic_s = sorted(relics, key=lambda x: x["momentum"], reverse=True)[:3]

        # Synergy: how well top cores match preferred scaling + non-empty kit data
        match = 0.0
        for c in cores[:5]:
            if prefer_str and "str" in c["tags"]:
                match += 1.0
            elif prefer_int and "int" in c["tags"]:
                match += 1.0
            elif scaling == "Hybrid" and ("str" in c["tags"] or "int" in c["tags"]):
                match += 0.75
            elif "pen" in c["tags"] or "cdr" in c["tags"]:
                match += 0.35
        synergy = (match / max(len(cores[:5]), 1)) * 100
        # Blend in kit identity: healers value hybrid/support slightly
        if (g["heal_count"] or 0) >= 1:
            synergy = min(100.0, synergy + 8)
        if (g["cc_count"] or 0) >= 2:
            synergy = min(100.0, synergy + 5)

        meta = sum(max(c["momentum"], -1.5) for c in cores[:4])
        meta_score_raw = meta + synergy * 0.02

        notes = []
        if dtype.lower() == "magical":
            notes.append(
                f"Magical damage god — itemize Intelligence / magical cores "
                f"(kit label {scaling}; basic-attack STR% does not mean physical items)."
            )
        elif dtype.lower() == "physical":
            notes.append(
                f"Physical damage god — itemize Strength / physical cores "
                f"(kit label {scaling})."
            )
        else:
            notes.append(f"Scaling label: {scaling}. Flexible itemization.")
        if prefer_int and not prefer_str:
            notes.append("Prefer INT power, magical pen (Obsidian / Spears), CDR.")
        elif prefer_str and not prefer_int:
            notes.append("Prefer STR power, physical pen (Titan's), AS/crit as role fits.")
        if g["cc_count"] and g["cc_count"] >= 2:
            notes.append("High CC kit — CDR and survival items valuable.")
        if g["mobility_count"] == 0:
            notes.append("Low innate mobility — consider blink/agility relics.")

        records.append(
            {
                "god_id": g["id"],
                "damage_type": dtype,
                "primary_scaling": scaling,
                "recommended_starter": starters_s[0]["name"] if starters_s else None,
                "core_items": [c["name"] for c in cores[:5]],
                "defense_items": [c["name"] for c in defs[:4]],
                "hybrid_items": [c["name"] for c in hybs[:3]],
                "relics": [c["name"] for c in relic_s],
                "synergy_raw": synergy,
                "meta_raw": meta_score_raw,
                "notes": " ".join(notes),
            }
        )
        synergy_raws.append(synergy)
        meta_raws.append(meta_score_raw)

    syn_n = normalize_minmax(synergy_raws)
    meta_n = normalize_minmax(meta_raws)

    for i, rec in enumerate(records):
        conn.execute(
            """
            INSERT INTO god_build_metrics (
                god_id, damage_type, primary_scaling, recommended_starter,
                core_items_json, defense_items_json, hybrid_items_json,
                relic_suggestions, build_synergy_score, meta_item_score,
                build_notes, metrics_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                rec["god_id"],
                rec["damage_type"],
                rec["primary_scaling"],
                rec["recommended_starter"],
                json.dumps(rec["core_items"]),
                json.dumps(rec["defense_items"]),
                json.dumps(rec["hybrid_items"]),
                json.dumps(rec["relics"]),
                syn_n[i],
                meta_n[i],
                rec["notes"],
                json.dumps(
                    {
                        "synergy_raw": rec["synergy_raw"],
                        "meta_raw": rec["meta_raw"],
                        "cores": rec["core_items"],
                    }
                ),
            ),
        )

    conn.commit()
    return {"gods": len(records), "items_cataloged": len(catalog)}


def _offensive_power(stats: dict[str, float], tags: set[str]) -> float:
    score = 0.0
    for k, v in stats.items():
        kl = k.lower()
        if kl in ("str", "strength"):
            score += v * 1.2
        elif kl in ("int", "intelligence"):
            score += v * 1.2
        elif "lifesteal" in kl or kl == "ls":
            score += v * 2.0
        elif "crit" in kl:
            score += v * 1.5
        elif "pen" in kl:
            score += v * 1.8
        elif "attack speed" in kl or kl == "as":
            score += v * 0.8
        elif "cooldown" in kl or kl in ("cdr", "haste"):
            score += v * 1.0
    if "offensive" in tags:
        score += 10
    return score


def _defensive_power(stats: dict[str, float], tags: set[str]) -> float:
    score = 0.0
    for k, v in stats.items():
        kl = k.lower()
        if "prot" in kl:
            score += v * 1.5
        elif "health" in kl or kl in ("hp", "max health"):
            score += v * 0.05
        elif "regen" in kl or "hp5" in kl:
            score += v * 2
        elif "cooldown" in kl:
            score += v * 0.8
    if "defensive" in tags:
        score += 10
    return score
