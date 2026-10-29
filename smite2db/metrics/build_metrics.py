"""God build metrics — same engine as Conquest paths (unified scorer)."""

from __future__ import annotations

import json
import re
import sqlite3
from typing import Any

from .stat_parse import normalize_minmax

# Prefer primary Conquest role for tier "build fit"
_ROLE_PRIORITY = ("Carry", "Mid", "Jungle", "Solo", "Support")

# Bounded identity vote — rewards locked kits whose path lands hook cores.
_IDENTITY_SYNERGY_CAP = 12.0
_IDENTITY_BAN_PENALTY = 4.0


def _parse_roles(roles_json: str | None) -> list[str]:
    if not roles_json:
        return []
    try:
        data = json.loads(roles_json)
    except json.JSONDecodeError:
        return [roles_json]
    out: list[str] = []
    for r in data if isinstance(data, list) else [data]:
        s = str(r)
        m = re.search(r"Role\.([A-Za-z]+)", s)
        if m:
            out.append(m.group(1))
        elif s and not s.startswith("ItemStore"):
            out.append(s)
    return out


def _primary_role(roles: list[str], damage_type: str | None) -> str:
    dtype = (damage_type or "").lower()
    for r in _ROLE_PRIORITY:
        if r in roles:
            return r
    if dtype == "magical":
        return "Mid"
    if dtype == "physical":
        return "Carry"
    return "Mid"


def _identity_synergy_delta(path_names: list[str], bias: dict[str, Any]) -> dict[str, Any]:
    """
    Bounded bonus/penalty when identity_lock is on.

    Hits against hook force-cores and prefer_items raise synergy; ban_items
    on the path lower it. Caps keep the 18% build vote from flipping S/A alone.
    """
    if not bias.get("identity_lock"):
        return {"delta": 0.0, "hits": 0, "want": 0, "ban_hits": 0}

    hooks = set(bias.get("identity_hooks") or [])
    if not hooks:
        return {"delta": 0.0, "hits": 0, "want": 0, "ban_hits": 0}

    from ..conquest_builds import _IDENTITY_FORCE_CORES

    blob = " | ".join((n or "").lower() for n in path_names)
    want_keys: list[str] = []
    for h in (
        "item_hp_scale",
        "permanent_max_hp",
        "spirit_lifesteal",
        "max_mana_scale",
        "damage_reflect",
        "max_hp_scale",
        "item_prot_cc",
        "plat_damp_stack",
        "haunt_shred",
        "base_damage_only",
        "ally_heal",
        "ally_shield",
    ):
        if h not in hooks:
            continue
        for k in _IDENTITY_FORCE_CORES.get(h, ()):
            if k not in want_keys:
                want_keys.append(k)
    for p in bias.get("prefer_items") or []:
        pl = str(p).lower().strip()
        if pl and pl not in want_keys:
            want_keys.append(pl)

    # Expect up to 3 distinct hook cores on a healthy locked path
    expect = want_keys[:5]
    hits = sum(1 for k in expect if k and k in blob)
    want_n = max(len(expect), 1)
    hit_ratio = hits / want_n
    # 0 hits → 0; full expect → +cap
    bonus = _IDENTITY_SYNERGY_CAP * hit_ratio

    ban_hits = 0
    for b in bias.get("ban_items") or []:
        bl = str(b).lower().strip()
        if bl and bl in blob:
            ban_hits += 1
    penalty = min(_IDENTITY_BAN_PENALTY * ban_hits, _IDENTITY_SYNERGY_CAP)

    delta = max(-_IDENTITY_SYNERGY_CAP, min(_IDENTITY_SYNERGY_CAP, bonus - penalty))
    return {
        "delta": round(delta, 2),
        "hits": hits,
        "want": len(expect),
        "ban_hits": ban_hits,
        "hooks": sorted(hooks),
    }


def compute_build_metrics(conn: sqlite3.Connection) -> dict[str, int]:
    """
    Populate god_build_metrics from the Conquest builder so tiers and
    site paths share one itemization brain.
    """
    # Late import avoids circular import at package load
    from ..conquest_builds import (
        ROLE_PROFILES,
        build_god_build,
        detect_archetype,
        god_scaling_bias,
        load_items,
    )

    conn.execute("DELETE FROM god_build_metrics")
    items = load_items(conn)

    gods = conn.execute(
        """
        SELECT g.id, g.name, g.primary_damage_type, g.roles,
               k.primary_scaling, k.avg_scaling_str, k.avg_scaling_int,
               k.kit_power_score, k.cc_count, k.heal_count, k.mobility_count
        FROM gods g
        LEFT JOIN god_kit_metrics k ON k.god_id = g.id
        """
    ).fetchall()

    records: list[dict[str, Any]] = []
    synergy_raws: list[float] = []
    meta_raws: list[float] = []

    for g in gods:
        roles = _parse_roles(g["roles"])
        dtype = (g["primary_damage_type"] or "").strip()
        role = _primary_role(roles, dtype)
        if role not in ROLE_PROFILES:
            role = "Mid"

        god_row = {
            "god_id": g["id"],
            "entity_name": g["name"],
            "primary_damage_type": dtype,
            "pantheon": None,
            "tier": None,
            "rank_in_scope": None,
            "score": g["kit_power_score"],
        }
        try:
            build = build_god_build(conn, items, role, god_row)
        except Exception as exc:  # noqa: BLE001
            # Fallback empty so analysis never dies on one god
            records.append(
                {
                    "god_id": g["id"],
                    "damage_type": dtype,
                    "primary_scaling": g["primary_scaling"] or "Mixed",
                    "recommended_starter": None,
                    "core_items": [],
                    "defense_items": [],
                    "hybrid_items": [],
                    "relics": [],
                    "synergy_raw": 40.0,
                    "meta_raw": 0.0,
                    "notes": f"Build engine error: {exc}",
                    "extra": {"role": role, "error": str(exc)},
                }
            )
            synergy_raws.append(40.0)
            meta_raws.append(0.0)
            continue

        if build is None:
            records.append(
                {
                    "god_id": g["id"],
                    "damage_type": dtype,
                    "primary_scaling": g["primary_scaling"] or "Mixed",
                    "recommended_starter": None,
                    "core_items": [],
                    "defense_items": [],
                    "hybrid_items": [],
                    "relics": [],
                    "synergy_raw": 40.0,
                    "meta_raw": 0.0,
                    "notes": f"{role} illegal for kit (e.g. melee Carry)",
                    "extra": {"role": role, "skipped": True},
                }
            )
            synergy_raws.append(40.0)
            meta_raws.append(0.0)
            continue

        path = build.get("items") or []
        cores = [
            it["name"]
            for it in path
            if it.get("type") in ("Offensive", "Hybrid") or (it.get("pen") or 0) >= 8
        ][:5]
        if not cores:
            cores = [it["name"] for it in path[:4]]
        defs = [it["name"] for it in path if it.get("type") == "Defensive"][:4]
        hybs = [it["name"] for it in path if it.get("type") == "Hybrid"][:3]
        starter = (build.get("starter") or {}).get("name")
        relics = [r["name"] for r in (build.get("relics") or [])]

        bias = god_scaling_bias(conn, g["id"])
        mage = dtype.lower() == "magical" or bias.get("primary") == "Intelligence"
        physical = (not mage) and (
            dtype.lower() == "physical" or bias.get("primary") == "Strength"
        )
        arch = build.get("archetype") or detect_archetype(bias, role, mage, physical)

        # Synergy: path matches damage type + pen present for damage roles
        match = 0.0
        n = max(len(path), 1)
        for it in path:
            stats = it.get("stats") or {}
            int_v = float(stats.get("int") or 0)
            str_v = float(stats.get("str") or 0)
            if mage and int_v >= str_v:
                match += 1.0
            elif physical and str_v >= int_v:
                match += 1.0
            elif not mage and not physical:
                match += 0.6
            if (it.get("pen") or 0) >= 8 and role in ("Carry", "Mid", "Jungle"):
                match += 0.35
        synergy = min(100.0, (match / n) * 85 + 15)
        if (g["cc_count"] or 0) >= 2:
            synergy = min(100.0, synergy + 4)
        if arch:
            synergy = min(100.0, synergy + 3)

        path_names = [it["name"] for it in path]
        id_vote = _identity_synergy_delta(path_names, bias)
        synergy = max(0.0, min(100.0, synergy + float(id_vote["delta"])))

        # Meta: mean recent-ish scores on path items (stored on item cards as momentum)
        moms = [float(it.get("momentum") or 0) for it in path]
        meta_score_raw = (sum(moms) / max(len(moms), 1)) * 4 + synergy * 0.02

        axes = bias.get("patch_axes_r5") or bias.get("patch_axes") or {}
        top_ax = sorted(axes.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        ax_txt = ", ".join(f"{k} {v:+.1f}" for k, v in top_ax) if top_ax else "—"

        algo_ver = None
        try:
            algo_ver = (build.get("algorithm") or {}).get("version")
        except AttributeError:
            algo_ver = None

        notes = [
            f"Primary role {role} · archetype «{arch}».",
            f"Same path engine as Conquest Builds (actives ≤{build.get('max_shop_actives', 2)}).",
        ]
        if bias.get("identity_lock"):
            notes.append(
                f"Identity lock (+{id_vote['delta']} synergy; "
                f"hook hits {id_vote['hits']}/{id_vote['want']})."
            )
        if dtype.lower() == "magical":
            notes.append("Magical damage → INT / magical cores.")
        elif dtype.lower() == "physical":
            notes.append("Physical damage → STR / physical cores.")
        notes.append(f"Patch axes (r5): {ax_txt}.")
        if build.get("why"):
            notes.append(build["why"][:280])

        records.append(
            {
                "god_id": g["id"],
                "damage_type": dtype,
                "primary_scaling": build.get("scaling") or g["primary_scaling"] or "Mixed",
                "recommended_starter": starter,
                "core_items": cores,
                "defense_items": defs,
                "hybrid_items": hybs,
                "relics": relics,
                "synergy_raw": synergy,
                "meta_raw": meta_score_raw,
                "notes": " ".join(notes),
                "extra": {
                    "role": role,
                    "archetype": arch,
                    "full_path": path_names,
                    "pen_total": build.get("pen_total"),
                    "kit_tags": build.get("kit_tags"),
                    "patch_axes_r5": axes,
                    "source": "conquest_builds.build_god_build",
                    "algorithm_version": algo_ver,
                    "identity_lock": bool(bias.get("identity_lock")),
                    "identity_strength": float(bias.get("identity_strength") or 0),
                    "identity_hooks": list(bias.get("identity_hooks") or []),
                    "identity_synergy": id_vote,
                },
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
                        **(rec.get("extra") or {}),
                    }
                ),
            ),
        )

    conn.commit()
    return {"gods": len(records), "items_cataloged": len(items), "engine": "conquest_builds"}
