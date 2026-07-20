"""
Statistically weighted Conquest builds per role.

Uses only local DB data:
  - item stats / categories / cost
  - item patch momentum
  - god kit scaling + role tags + tier scores
No external build guides.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sqlite3
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .db import DEFAULT_DB, connect

# SMITE 2 active-item rules (shop T3 On-Use items in the 6-item grid):
# - Hard game limit is 3 (item text + curios share this budget; curios auto-drop at 3).
# - Practical default is 2 shop actives so you can keep your free Curio + 1 relic.
# - Melee physical kits (Solo/Jungle warriors, etc.) may fill the 3rd active slot.
HARD_MAX_ACTIVE_ITEMS = 3
DEFAULT_MAX_SHOP_ACTIVES = 2
# Back-compat alias used in reports / older call sites
MAX_ACTIVE_ITEMS = DEFAULT_MAX_SHOP_ACTIVES

# Roles that must ship real penetration in the final 6 (not just raw power).
DAMAGE_ROLES_NEED_PEN = frozenset({"Carry", "Mid", "Jungle"})
# Minimum pen stat total (flat or %) across the 6 items for those roles.
MIN_BUILD_PEN = 10.0


# ---------------------------------------------------------------------------
# Role frameworks — weights sum to ~1.0 for primary stat axes
# ---------------------------------------------------------------------------

ROLE_PROFILES: dict[str, dict[str, Any]] = {
    "Carry": {
        "description": (
            "Conquest duo ADC: sustained basic-attack DPS, crit windows, "
            "penetration, and self-heal to stay in lane/fights."
        ),
        "prefer_damage": "Physical",  # soft preference; Magical carries still allowed
        "stat_weights": {
            "str": 0.20,
            "int": 0.04,
            "as": 0.16,
            "crit": 0.14,
            "pen": 0.18,
            "ls": 0.10,
            "bap": 0.08,
            "hp": 0.05,
            "cdr": 0.03,
            "pprot": 0.01,
            "mprot": 0.01,
        },
        "tag_bonus": {
            "offensive": 12,
            "passive": 8,
            "active": 1,
            "starter": 0,
        },
        "starter_prefs": {
            # name substring / category cues → weight
            "gilded": 30,
            "arrow": 25,
            "death": 22,
            "toll": 20,
            "cowl": 18,
            "leather": 16,
            "shroud": 10,
            "vampiric": 8,
            "bluestone": 5,
        },
        "relic_prefs": {
            "beads": 25,
            "purification": 25,
            "aegis": 20,
            "blink": 12,
            "sundering": 15,
            "agility": 10,
            "phantom": 8,
        },
        # Conquest inventory: 1 starter slot + 6 item slots (starter is NOT one of the 6)
        "build_slots": {
            "starter": 1,
            "cores": 4,  # offense-first
            "defense": 1,
            "flex": 1,  # pen / AS / hybrid → total 6 full items
        },
        "tier_scope": "role:Carry",
    },
    "Mid": {
        "description": (
            "Conquest mid: ability burst and wave clear, intelligence or hybrid "
            "power, penetration, cooldown, and mana sustain."
        ),
        "prefer_damage": "Magical",
        "stat_weights": {
            "int": 0.24,
            "str": 0.06,
            "pen": 0.22,  # mages need Obsidian/Spear pen — not pure INT stacks
            "cdr": 0.14,
            "mp": 0.08,
            "mpr": 0.05,
            "hp": 0.07,
            "ls": 0.05,
            "as": 0.03,
            "pprot": 0.02,
            "mprot": 0.02,
        },
        "tag_bonus": {"offensive": 12, "passive": 8, "active": 1},
        "starter_prefs": {
            "conduit": 28,
            "sands": 26,
            "pendulum": 24,
            "vampiric": 18,
            "shroud": 16,
            "bluestone": 14,
            "archmage": 20,
            "death": 8,
        },
        "relic_prefs": {
            "beads": 22,
            "aegis": 22,
            "blink": 16,
            "sundering": 14,
            "phantom": 10,
            "agility": 8,
        },
        "build_slots": {"starter": 1, "cores": 4, "defense": 1, "flex": 1},
        "tier_scope": "role:Mid",
    },
    "Jungle": {
        "description": (
            "Conquest jungle: early clear, gank threat, mobility/CDR, "
            "burst penetration, and enough HP to invade."
        ),
        "prefer_damage": None,
        "stat_weights": {
            "str": 0.16,
            "int": 0.12,
            "pen": 0.20,
            "cdr": 0.12,
            "as": 0.10,
            "hp": 0.12,
            "ls": 0.06,
            "crit": 0.04,
            "pprot": 0.04,
            "mprot": 0.04,
        },
        "tag_bonus": {"offensive": 10, "passive": 7, "active": 2},
        "starter_prefs": {
            "bumba": 35,
            "dagger": 28,
            "cudgel": 26,
            "spear": 24,
            "hammer": 22,
            "death": 12,
            "bluestone": 10,
            "conduit": 8,
        },
        "relic_prefs": {
            "beads": 20,
            "blink": 22,
            "aegis": 14,
            "sundering": 18,
            "agility": 16,
            "phantom": 8,
        },
        "build_slots": {"starter": 1, "cores": 4, "defense": 1, "flex": 1},
        "tier_scope": "role:Jungle",
    },
    "Solo": {
        "description": (
            "Conquest solo: lane sustain, hybrid damage, protections, "
            "HP, and items that win extended trades / rotate first."
        ),
        "prefer_damage": None,
        "stat_weights": {
            "hp": 0.16,
            "pprot": 0.14,
            "mprot": 0.14,
            "str": 0.12,
            "int": 0.10,
            "cdr": 0.10,
            "ls": 0.08,
            "pen": 0.08,
            "hpr": 0.04,
            "as": 0.02,
            "mp": 0.02,
        },
        "tag_bonus": {"defensive": 10, "hybrid": 12, "offensive": 6, "passive": 5},
        "starter_prefs": {
            "warrior": 38,
            "axe": 36,
            "bluestone": 32,
            "sundering": 28,
            "selfless": 10,
            "shroud": 14,
            "vampiric": 14,
            "conduit": 10,
            "flag": 6,
        },
        "relic_prefs": {
            "beads": 24,
            "aegis": 18,
            "blink": 12,
            "sundering": 14,
            "phantom": 12,
            "shell": 10,
            "agility": 8,
        },
        "build_slots": {"starter": 1, "cores": 2, "defense": 3, "flex": 1},
        "tier_scope": "role:Solo",
    },
    "Support": {
        "description": (
            "Conquest support: peel, aura/team utility, dual prots, HP, "
            "CDR, and active/defensive cores over pure personal DPS."
        ),
        "prefer_damage": None,
        "stat_weights": {
            "hp": 0.18,
            "pprot": 0.16,
            "mprot": 0.16,
            "cdr": 0.12,
            "int": 0.08,
            "str": 0.04,
            "mp": 0.06,
            "hpr": 0.06,
            "pen": 0.04,
            "as": 0.02,
            "ls": 0.02,
            "mpr": 0.06,
        },
        "tag_bonus": {"defensive": 14, "hybrid": 10, "passive": 6, "active": 8, "offensive": 2},
        "starter_prefs": {
            "war": 28,
            "flag": 28,
            "banner": 26,
            "selfless": 26,
            "heroism": 24,
            "sundering": 10,
            "warrior": 8,
        },
        "relic_prefs": {
            "beads": 28,
            "purification": 26,
            "aegis": 22,
            "shell": 16,
            "phantom": 14,
            "talisman": 18,
            "blink": 10,
            "sundering": 8,
        },
        "build_slots": {"starter": 1, "cores": 1, "defense": 4, "flex": 1},
        "tier_scope": "role:Support",
    },
}

STAT_ALIASES = {
    "str": ("str", "strength"),
    "int": ("int", "intelligence"),
    "hp": ("hp", "max health", "health"),
    "mp": ("mp", "max mana", "mana"),
    "hpr": ("hpr", "hp5", "health regen"),
    "mpr": ("mpr", "mp5", "mana regen"),
    "as": ("as", "attack speed"),
    "crit": ("crit", "critical", "critical chance", "critical strike chance"),
    "pen": ("pen", "penetration", "% pen", "percent pen"),
    "ls": ("ls", "lifesteal", "life steal"),
    "cdr": ("cdr", "cooldown", "cooldown rate", "haste"),
    "pprot": ("pprot", "physical protection", "physical prot"),
    "mprot": ("mprot", "magical protection", "magical prot"),
    "bap": ("bap", "basic attack", "attack damage", "inhand"),
    "damp": ("damp", "dampening"),
}


def _parse_stats(stats_json: str | None, stats_text: str | None) -> dict[str, float]:
    out: dict[str, float] = {}
    if stats_json:
        try:
            arr = json.loads(stats_json)
            if isinstance(arr, list):
                for e in arr:
                    if not isinstance(e, dict):
                        continue
                    name = (e.get("stat") or "").strip().lower()
                    raw = str(e.get("value") or "")
                    m = re.search(r"-?\d+(?:\.\d+)?", raw.replace(",", ""))
                    if name and m:
                        out[name] = float(m.group())
        except json.JSONDecodeError:
            pass
    if stats_text:
        for line in stats_text.splitlines():
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            m = re.search(r"-?\d+(?:\.\d+)?", v.replace(",", ""))
            if m:
                out.setdefault(k.strip().lower(), float(m.group()))
    return out


def _canon_stat_value(raw_stats: dict[str, float], canon: str) -> float:
    aliases = STAT_ALIASES.get(canon, (canon,))
    best = 0.0
    for k, v in raw_stats.items():
        kl = k.lower()
        for a in aliases:
            if a == kl or a in kl:
                best = max(best, abs(v))
    return best


def _item_flags(row) -> set[str]:
    blob = " ".join(
        filter(
            None,
            [
                row["item_type"] or "",
                row["categories"] or "",
                row["passive"] or "",
                row["active"] or "",
                row["stats_text"] or "",
                row["name"] or "",
            ],
        )
    ).lower()
    flags = set()
    for t in (
        "offensive",
        "defensive",
        "hybrid",
        "starter",
        "relic",
        "passive",
        "active",
        "consumable",
    ):
        if t in blob:
            flags.add(t)
    # utility keywords for support/solo
    for kw, tag in (
        ("aura", "aura"),
        ("allies", "team"),
        ("ally", "team"),
        ("shield", "shield"),
        ("cleanse", "cleanse"),
        ("anti-heal", "antiheal"),
        ("anti heal", "antiheal"),
        ("heal", "heal"),
        ("movement speed", "ms"),
        ("crowd control", "cc"),
        ("slow", "cc"),
        ("stun", "cc"),
    ):
        if kw in blob:
            flags.add(tag)
    return flags


@dataclass
class ScoredItem:
    name: str
    tier: str
    item_type: str
    total_cost: int
    stats: dict[str, float]
    flags: set[str]
    momentum: float
    role_score: float
    score_breakdown: dict[str, float] = field(default_factory=dict)
    passive: str = ""
    active: str = ""
    is_active_item: bool = False  # counts toward the 3-active shop cap


def is_shop_active_item(
    *,
    name: str = "",
    tier: str = "",
    item_type: str = "",
    categories: str = "",
    active_text: str = "",
    total_cost: int = 0,
) -> bool:
    """
    True if this item consumes one of the 3 'Active item' inventory slots.

    Relics / curios / consumables / god-specific are excluded from the 6-item
    path (handled separately). Shop T3 actives are detected via category
    'Active items' or On Use + the standard 3-active disclaimer.
    """
    cats = (categories or "").lower()
    itype = (item_type or "").lower()
    tier_s = str(tier or "")
    active = active_text or ""

    # Not part of the 6-item active budget
    if tier_s == "Relic" or itype == "relic" or "relics" in cats:
        return False
    if tier_s in ("Curio", "Consumable") or itype in ("curio", "consumable"):
        return False
    if "god specific" in cats or itype == "god specific":
        return False
    if "starter" in cats and (total_cost or 0) < 1500:
        return False

    if "active items" in cats:
        return True
    if re.search(r"on use", active, re.I) and re.search(
        r"up to 3 active|own up to 3", active, re.I
    ):
        return True
    # Shop-tier On Use without the disclaimer still counts (wiki sometimes omits it)
    if re.search(r"^\s*on use", active, re.I) and tier_s in ("2", "3") and (
        itype in ("offensive", "defensive", "hybrid", "") or not itype
    ):
        return True
    return False


def load_items(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        """
        SELECT name, tier, item_type, cost, total_cost, stats_json, stats_text,
               passive, active, categories
        FROM items
        """
    ).fetchall()
    momentum = {
        r["entity_name"]: r["net_weighted_score"] or 0.0
        for r in conn.execute(
            "SELECT entity_name, net_weighted_score FROM entity_patch_summary WHERE entity_type='item'"
        )
    }
    items = []
    for r in rows:
        stats = _parse_stats(r["stats_json"], r["stats_text"])
        cost = r["total_cost"] if r["total_cost"] is not None else (r["cost"] or 0)
        cats = r["categories"] or ""
        active = r["active"] or ""
        flags = _item_flags(r)
        is_active = is_shop_active_item(
            name=r["name"],
            tier=str(r["tier"] or ""),
            item_type=r["item_type"] or "",
            categories=cats,
            active_text=active,
            total_cost=int(cost or 0),
        )
        if is_active:
            flags.add("active_item")
        else:
            flags.add("passive_item")
        items.append(
            {
                "name": r["name"],
                "tier": str(r["tier"] or ""),
                "item_type": r["item_type"] or "",
                "total_cost": int(cost or 0),
                "stats": stats,
                "flags": flags,
                "momentum": momentum.get(r["name"], 0.0),
                "passive": r["passive"] or "",
                "active": active,
                "categories": cats,
                "is_active_item": is_active,
            }
        )
    return items


def score_item_for_role(item: dict, role: str, profile: dict) -> ScoredItem:
    weights: dict[str, float] = profile["stat_weights"]
    prefer = profile.get("prefer_damage")
    # normalize raw stats to 0-100ish per axis using soft caps
    caps = {
        "str": 90,
        "int": 90,
        "hp": 500,
        "mp": 300,
        "hpr": 10,
        "mpr": 10,
        "as": 40,
        "crit": 40,
        "pen": 25,  # 20% shard already near full value; reward pen items hard
        "ls": 25,
        "cdr": 30,
        "pprot": 70,
        "mprot": 70,
        "bap": 80,
        "damp": 30,
    }
    breakdown: dict[str, float] = {}
    stat_score = 0.0
    for axis, w in weights.items():
        val = _canon_stat_value(item["stats"], axis)
        cap = caps.get(axis, 50)
        norm = min(val / cap, 1.25) * 100  # allow slight overcap
        part = w * norm
        breakdown[f"stat:{axis}"] = round(part, 2)
        stat_score += part

    str_v = _canon_stat_value(item["stats"], "str")
    int_v = _canon_stat_value(item["stats"], "int")
    # Role damage preference (Carry≈physical, Mid≈magical templates)
    align = 0.0
    if prefer == "Physical":
        align += str_v * 0.4 + _canon_stat_value(item["stats"], "as") * 0.35
        align += _canon_stat_value(item["stats"], "crit") * 0.4
        align += _canon_stat_value(item["stats"], "bap") * 0.35
        if int_v >= 45 and str_v < 20:
            align -= 35
    elif prefer == "Magical":
        align += int_v * 0.45
        if str_v >= 45 and int_v < 20:
            align -= 35
    breakdown["dmg_align"] = round(align, 2)

    tag_score = 0.0
    for flag, bonus in profile.get("tag_bonus", {}).items():
        if flag in item["flags"]:
            tag_score += bonus
            breakdown[f"tag:{flag}"] = bonus

    # role-specific utility from passives
    util = 0.0
    blob = (item["passive"] + " " + item["active"]).lower()
    if role == "Support":
        if any(k in blob for k in ("ally", "allies", "aura", "team")):
            util += 18
        if "cleanse" in blob or "cc immune" in blob:
            util += 10
        if "shield" in blob:
            util += 8
    if role == "Solo":
        if any(k in blob for k in ("shield", "protections", "heal", "mitigation")):
            util += 12
        if "anti" in blob and "heal" in blob:
            util += 8
        # Solo prefers warrior starters via starter_prefs; boost hybrid offline damage
        if str_v > 0 and (_canon_stat_value(item["stats"], "pprot") > 0 or _canon_stat_value(item["stats"], "hp") > 0):
            util += 6
    if role in ("Carry", "Mid", "Jungle"):
        pen_v = _canon_stat_value(item["stats"], "pen")
        if pen_v >= 15:
            util += 22  # dedicated shred (Obsidian / Titan's)
        elif pen_v >= 8:
            util += 14
        elif "penetrat" in blob or "penetration" in (item.get("categories") or "").lower():
            util += 10
        if "prot" in blob and "reduc" in blob:
            util += 8
        if "crit" in blob or "basic attack" in blob:
            util += 10 if role == "Carry" else 2
        # Prefer passive pen cores over luxury On-Use power+pen (Dreamer's Idol)
        cats = (item.get("categories") or "").lower()
        if "penetration" in cats and not item.get("is_active_item"):
            util += 12
    if role == "Jungle" and any(k in blob for k in ("jungle", "monster", "minion")):
        util += 8
    breakdown["utility_text"] = util

    # patch momentum (recent meta signal) — moderated so raw stats lead
    mom = item["momentum"] * 8
    breakdown["momentum"] = round(mom, 2)

    # cost efficiency: prefer 2300-2800 cores; starters handled separately
    cost = item["total_cost"] or 0
    cost_part = 0.0
    if 0 < cost < 800:
        cost_part = 4
    elif 2200 <= cost <= 2800:
        cost_part = 10
    elif 2800 < cost <= 3200:
        cost_part = 4
    elif cost > 3400:
        cost_part = -12  # luxury actives like Dreamer's/Parashu — late only
    breakdown["cost"] = cost_part

    # Actives are expensive budget: default path only wants ~2 shop actives.
    active_tax = 0.0
    if item.get("is_active_item"):
        active_tax = -16.0
        breakdown["active_tax"] = active_tax
    else:
        breakdown["active_tax"] = 0.0

    total = stat_score + tag_score + util + mom + cost_part + align + active_tax
    return ScoredItem(
        name=item["name"],
        tier=item["tier"],
        item_type=item["item_type"],
        total_cost=cost,
        stats=item["stats"],
        flags=item["flags"],
        momentum=item["momentum"],
        role_score=total,
        score_breakdown=breakdown,
        passive=item["passive"],
        active=item["active"],
        is_active_item=bool(item.get("is_active_item")),
    )


def score_starter(item: dict, profile: dict) -> float:
    name = item["name"].lower()
    base = 0.0
    for key, w in profile.get("starter_prefs", {}).items():
        if key in name:
            base = max(base, w)
    # stats still matter
    scored = score_item_for_role(item, "Support", {**profile, "stat_weights": profile["stat_weights"]})
    return base + scored.role_score * 0.25 + item["momentum"] * 5


def score_relic(item: dict, profile: dict) -> float:
    name = item["name"].lower()
    base = 0.0
    for key, w in profile.get("relic_prefs", {}).items():
        if key in name:
            base = max(base, w)
    # free relics preferred as first pick
    if (item["total_cost"] or 0) == 0:
        base += 8
    else:
        base -= 5  # upgraded relics later
    base += item["momentum"] * 6
    return base


def is_t1_starter(it: dict) -> bool:
    if "starter" not in it["flags"] and "starter" not in (it.get("categories") or "").lower():
        # also allow known starter tiers
        if it["tier"] not in ("1", "Starter"):
            return False
    # upgraded starters are tier 2 with cost ~1800+
    if it["tier"] in ("2", "Upgraded Starter") or (it["total_cost"] or 0) >= 1500:
        return False
    if it["tier"] == "1" or it["tier"] == "Starter" or (it["total_cost"] or 0) == 0:
        # filter non-starters that are just tier 1 components
        cats = (it.get("categories") or "").lower()
        name = it["name"].lower()
        if "starter" in cats or any(
            k in name
            for k in (
                "bumba",
                "bluestone",
                "conduit",
                "death",
                "gilded",
                "leather",
                "vampiric",
                "war flag",
                "warrior",
                "selfless",
                "sands",
            )
        ):
            return True
        if "starter" in cats:
            return True
    return "starter" in (it.get("categories") or "").lower() and (it["total_cost"] or 0) < 1200


def is_upgraded_starter(it: dict) -> bool:
    cats = (it.get("categories") or "").lower()
    if "starter" not in cats and "starter" not in it["flags"]:
        return False
    return (it["total_cost"] or 0) >= 1500 or it["tier"] in ("2", "Upgraded Starter")


def is_t3_core(it: dict) -> bool:
    if it["tier"] == "3":
        return True
    if it["item_type"] in ("Offensive", "Defensive", "Hybrid") and (it["total_cost"] or 0) >= 2200:
        return True
    return False


def is_base_relic(it: dict) -> bool:
    if it["tier"] == "Relic" or it["item_type"] == "Relic" or "relic" in it["flags"]:
        return (it["total_cost"] or 0) <= 0
    return False


def pick_diverse(scored: list[ScoredItem], n: int, kind: str) -> list[ScoredItem]:
    """Pick top items while avoiding near-duplicate stat profiles."""
    picked: list[ScoredItem] = []
    for it in scored:
        if kind == "offense" and it.item_type == "Defensive" and "offensive" not in it.flags:
            # allow if hybrid high score
            if "hybrid" not in it.flags and _canon_stat_value(it.stats, "str") + _canon_stat_value(it.stats, "int") < 40:
                continue
        if kind == "defense":
            if it.item_type == "Offensive" and "defensive" not in it.flags:
                if _canon_stat_value(it.stats, "pprot") + _canon_stat_value(it.stats, "mprot") + _canon_stat_value(it.stats, "hp") / 10 < 40:
                    continue
        # diversity: skip if same primary power stat within 5 of existing
        too_close = False
        for p in picked:
            if _stat_similarity(it, p) > 0.82:
                too_close = True
                break
        if too_close:
            continue
        picked.append(it)
        if len(picked) >= n:
            break
    # fill if diversity too strict
    if len(picked) < n:
        for it in scored:
            if it not in picked:
                picked.append(it)
            if len(picked) >= n:
                break
    return picked


def _stat_similarity(a: ScoredItem, b: ScoredItem) -> float:
    keys = ("str", "int", "pen", "as", "crit", "hp", "pprot", "mprot", "cdr", "ls")
    va = [_canon_stat_value(a.stats, k) for k in keys]
    vb = [_canon_stat_value(b.stats, k) for k in keys]
    # cosine similarity
    dot = sum(x * y for x, y in zip(va, vb))
    na = math.sqrt(sum(x * x for x in va)) or 1.0
    nb = math.sqrt(sum(x * x for x in vb)) or 1.0
    return dot / (na * nb)


def god_scaling_bias(conn: sqlite3.Connection, god_id: int) -> dict[str, float]:
    row = conn.execute(
        "SELECT primary_scaling, avg_scaling_str, avg_scaling_int, kit_power_score, cc_count, heal_count, mobility_count FROM god_kit_metrics WHERE god_id=?",
        (god_id,),
    ).fetchone()
    if not row:
        return {"str": 0.5, "int": 0.5, "cc": 0, "heal": 0, "mobility": 0, "kit": 40}
    return {
        "str": (row["avg_scaling_str"] or 0) / 100.0,
        "int": (row["avg_scaling_int"] or 0) / 100.0,
        "primary": row["primary_scaling"] or "Mixed",
        "cc": row["cc_count"] or 0,
        "heal": row["heal_count"] or 0,
        "mobility": row["mobility_count"] or 0,
        "kit": row["kit_power_score"] or 40,
    }


def rescore_for_god(
    item: ScoredItem,
    bias: dict,
    role: str,
    damage_type: str | None = None,
) -> float:
    s = item.role_score
    str_v = _canon_stat_value(item.stats, "str")
    int_v = _canon_stat_value(item.stats, "int")
    as_v = _canon_stat_value(item.stats, "as")
    crit_v = _canon_stat_value(item.stats, "crit")
    primary = bias.get("primary", "Mixed")
    dtype = (damage_type or "").lower()

    # Hard scaling alignment (dominant signal for per-god paths)
    mage = primary == "Intelligence" or (primary == "Mixed" and dtype == "magical") or dtype == "magical"
    physical = primary == "Strength" or (primary == "Mixed" and dtype == "physical") or dtype == "physical"

    if physical and not mage:
        s += str_v * 0.85
        s -= int_v * 0.55
        if int_v >= 40 and str_v < 15:
            s -= 55  # pure mage item on STR kit
        if as_v or crit_v:
            s += as_v * 0.25 + crit_v * 0.3
    elif mage:
        s += int_v * 0.95
        s -= str_v * 0.75
        s -= as_v * 0.45  # basic-attack toys (Riptalon etc.) are not mage cores
        s -= crit_v * 0.5
        s -= _canon_stat_value(item.stats, "bap") * 0.4
        if str_v >= 25 and int_v < 30:
            s -= 50
        if str_v >= 40 and int_v < 20:
            s -= 70
    elif primary == "Hybrid":
        s += (str_v + int_v) * 0.4
        s += min(str_v, int_v) * 0.25  # reward true hybrid stats
    else:
        s += max(str_v, int_v) * 0.45

    # Damage-type hard filter
    if dtype == "physical" and int_v > str_v + 20:
        s -= 35
    if dtype == "magical" and str_v > int_v + 15:
        s -= 40

    if bias.get("cc", 0) >= 2 and _canon_stat_value(item.stats, "cdr") > 0:
        s += 10
    if bias.get("heal", 0) >= 1 and (
        _canon_stat_value(item.stats, "ls") > 0 or "heal" in (item.passive + item.active).lower()
    ):
        s += 12
    if bias.get("mobility", 0) == 0 and role in ("Jungle", "Carry") and not mage:
        if as_v > 0:
            s += 5

    # Damage roles: pen is not optional — but only *matching* pen for the kit.
    if role in DAMAGE_ROLES_NEED_PEN:
        pen_v = _canon_stat_value(item.stats, "pen")
        # Mage: Obsidian / Magus / Deso / Soul Gem style
        if mage:
            if int_v >= 30 and pen_v >= 8:
                s += pen_v * 1.6 + 12
            elif pen_v >= 8 and int_v < 25:
                s -= 25  # physical pen item on mage
            if pen_v >= 15 and int_v >= 50 and not item.is_active_item:
                s += 22  # Obsidian Shard
        elif physical:
            if str_v >= 25 and pen_v >= 8:
                s += pen_v * 1.5 + 10
            elif pen_v >= 15 and str_v >= 40 and not item.is_active_item:
                s += 20  # Titan's Bane
            elif pen_v >= 8 and str_v < 20 and int_v >= 40:
                s -= 25  # mage pen on physical
        else:
            s += pen_v * 1.2
        if pen_v >= 8 and item.is_active_item and (item.total_cost or 0) >= 3200:
            s -= 8  # Dreamer's/Parashu = luxury, not the pen plan
    return s


def max_shop_actives_for_god(role: str, damage_type: str | None, bias: dict | None = None) -> int:
    """
    Practical active budget for the 6-item grid.

    Most builds: 2 (leave room for free Curio which also eats the active budget).
    Melee-leaning physical Solo/Jungle: up to hard cap 3.
    """
    dtype = (damage_type or "").lower()
    primary = (bias or {}).get("primary") or ""
    melee_role = role in ("Solo", "Jungle", "Support")
    physical = dtype == "physical" or primary == "Strength"
    if melee_role and physical:
        return HARD_MAX_ACTIVE_ITEMS
    return DEFAULT_MAX_SHOP_ACTIVES


def item_pen_value(it: ScoredItem) -> float:
    return _canon_stat_value(it.stats, "pen")


def is_pen_item(it: ScoredItem) -> bool:
    if item_pen_value(it) >= 5:
        return True
    blob = f"{it.name} {it.passive} {it.active}".lower()
    return "penetrat" in blob or "shattering" in blob


def _slot_label(it: ScoredItem) -> str:
    if is_pen_item(it) and item_pen_value(it) >= 8:
        return "pen"
    if it.item_type == "Defensive" or "defensive" in it.flags:
        return "defense"
    if _canon_stat_value(it.stats, "pprot") + _canon_stat_value(it.stats, "mprot") >= 45:
        return "defense"
    if _canon_stat_value(it.stats, "hp") >= 300 and (
        _canon_stat_value(it.stats, "str") + _canon_stat_value(it.stats, "int")
    ) < 40:
        return "defense"
    return "power"


def _trim_excess_defense(
    path: list[ScoredItem],
    pool: list[ScoredItem],
    max_defense: int = 1,
    max_actives: int = 2,
) -> list[ScoredItem]:
    """Damage builds keep at most one pure defense item."""
    defs = [i for i, it in enumerate(path) if _slot_label(it) == "defense"]
    if len(defs) <= max_defense:
        return path
    # Drop lowest-scored extra defense, replace with best offense from pool
    extras = sorted(defs, key=lambda i: path[i].role_score)
    new_path = list(path)
    seen = {x.name for x in new_path}
    for idx in extras[:-max_defense] if max_defense else extras:
        replacement = None
        for cand in sorted(pool, key=lambda x: x.role_score, reverse=True):
            if cand.name in seen:
                continue
            if _slot_label(cand) == "defense":
                continue
            if cand.is_active_item and sum(1 for x in new_path if x.is_active_item) >= max_actives:
                continue
            replacement = cand
            break
        if replacement:
            seen.discard(new_path[idx].name)
            new_path[idx] = replacement
            seen.add(replacement.name)
    return new_path


def _order_buy_path(path: list[ScoredItem], role: str) -> list[ScoredItem]:
    """
    Present items in an intuitive buy order, not pure score rank:
      1) early affordable power  2) pen  3) more power/CDR  4) defense  5) luxury
    """
    if not path:
        return path

    def sort_key(it: ScoredItem) -> tuple:
        pen = item_pen_value(it)
        cost = it.total_cost or 2500
        slot = _slot_label(it)
        luxury = 1 if cost >= 3200 or (it.is_active_item and pen >= 8 and cost >= 3000) else 0
        # phase: early power (0), pen (1), mid power (2), defense (3), luxury (4)
        if luxury:
            phase = 4
        elif slot == "pen":
            phase = 1
        elif slot == "defense":
            phase = 3
        elif cost <= 2500:
            phase = 0
        else:
            phase = 2
        # within phase: cheaper first, then higher score
        return (phase, cost, -it.role_score)

    return sorted(path, key=sort_key)


def _pen_matches_kit(it: ScoredItem, *, mage: bool, physical: bool) -> bool:
    """True if this pen item is for the right damage type."""
    pen = item_pen_value(it)
    if pen < 5:
        return False
    str_v = _canon_stat_value(it.stats, "str")
    int_v = _canon_stat_value(it.stats, "int")
    if mage:
        return int_v >= 30 or (int_v >= str_v and int_v >= 20)
    if physical:
        return str_v >= 25 or (str_v >= int_v and str_v >= 20)
    return True


def _ensure_pen_in_path(
    path: list[ScoredItem],
    pool: list[ScoredItem],
    role: str,
    max_actives: int,
    *,
    mage: bool = False,
    physical: bool = False,
) -> list[ScoredItem]:
    """Guarantee damage roles get real *matching* pen (prefer passive shred)."""
    if role not in DAMAGE_ROLES_NEED_PEN:
        return path

    matching = [x for x in path if _pen_matches_kit(x, mage=mage, physical=physical)]
    total_pen = sum(item_pen_value(x) for x in matching)
    if total_pen >= MIN_BUILD_PEN and matching:
        # Also strip wrong-type pen if we already have enough matching pen
        return path

    seen = {x.name for x in path}
    candidates = [
        x
        for x in pool
        if x.name not in seen
        and _pen_matches_kit(x, mage=mage, physical=physical)
        and item_pen_value(x) >= 8
    ]
    candidates.sort(
        key=lambda x: (
            0 if not x.is_active_item else 1,
            -item_pen_value(x),
            -x.role_score,
        )
    )
    if not candidates:
        return path

    pick = candidates[0]
    # Prefer replacing wrong-type pen or a low-value non-pen / active
    drop_idx = None
    for i, it in enumerate(path):
        if is_pen_item(it) and not _pen_matches_kit(it, mage=mage, physical=physical):
            drop_idx = i
            break
    if drop_idx is None:
        for i, it in enumerate(path):
            if it.is_active_item and not _pen_matches_kit(it, mage=mage, physical=physical):
                drop_idx = i
                break
    if drop_idx is None:
        scored = [
            (i, it)
            for i, it in enumerate(path)
            if not _pen_matches_kit(it, mage=mage, physical=physical)
        ]
        if scored:
            drop_idx = min(scored, key=lambda t: t[1].role_score)[0]
    if drop_idx is None:
        return path

    new_path = list(path)
    new_path[drop_idx] = pick
    while sum(1 for x in new_path if x.is_active_item) > max_actives:
        for i, it in enumerate(new_path):
            if it.is_active_item and not _pen_matches_kit(it, mage=mage, physical=physical):
                for alt in pool:
                    if alt.name not in {x.name for x in new_path} and not alt.is_active_item:
                        new_path[i] = alt
                        break
                break
        else:
            break
    return new_path


def top_gods_for_role(conn: sqlite3.Connection, role: str, limit: int = 5) -> list[dict]:
    scope = f"role:{role}"
    rows = conn.execute(
        """
        SELECT t.entity_name, t.tier, t.rank_in_scope, t.score,
               t.patch_score, t.kit_score, t.build_score, t.rationale,
               g.id AS god_id, g.primary_damage_type, g.pantheon
        FROM tier_list t
        JOIN gods g ON g.name = t.entity_name
        WHERE t.scope = ? AND t.entity_type = 'god'
        ORDER BY t.rank_in_scope
        LIMIT ?
        """,
        (scope, limit),
    ).fetchall()
    if rows:
        return [dict(r) for r in rows]
    # fallback: filter gods by roles JSON
    out = []
    for g in conn.execute(
        """
        SELECT g.id AS god_id, g.name AS entity_name, g.primary_damage_type, g.pantheon,
               g.roles, t.tier, t.rank_in_scope, t.score, t.patch_score, t.kit_score, t.build_score
        FROM gods g
        LEFT JOIN tier_list t ON t.entity_name = g.name AND t.scope = 'overall' AND t.entity_type = 'god'
        """
    ):
        roles_raw = g["roles"] or "[]"
        try:
            roles = json.loads(roles_raw)
        except json.JSONDecodeError:
            roles = []
        role_names = []
        for r in roles:
            s = str(r)
            m = re.search(r"Role\.([A-Za-z]+)", s)
            role_names.append(m.group(1) if m else s)
        if role in role_names or any(role.lower() == x.lower() for x in role_names):
            out.append(dict(g))
    out.sort(key=lambda x: x.get("score") or 0, reverse=True)
    return out[:limit]


def build_role_template(items: list[dict], role: str) -> dict[str, Any]:
    profile = ROLE_PROFILES[role]
    scored_all = [score_item_for_role(it, role, profile) for it in items]
    scored_all.sort(key=lambda x: x.role_score, reverse=True)

    starters = [
        score_item_for_role(it, role, profile)
        for it in items
        if is_t1_starter(it)
    ]
    # re-rank starters with starter prefs
    for s in starters:
        s.role_score = score_starter(
            next(i for i in items if i["name"] == s.name), profile
        )
    starters.sort(key=lambda x: x.role_score, reverse=True)

    upgraded = [
        score_item_for_role(it, role, profile)
        for it in items
        if is_upgraded_starter(it)
    ]
    upgraded.sort(key=lambda x: x.role_score, reverse=True)

    t3 = [s for s in scored_all if is_t3_core(next(i for i in items if i["name"] == s.name))]
    offense = [
        s
        for s in t3
        if s.item_type == "Offensive"
        or "offensive" in s.flags
        or (_canon_stat_value(s.stats, "str") + _canon_stat_value(s.stats, "int"))
        >= (_canon_stat_value(s.stats, "pprot") + _canon_stat_value(s.stats, "mprot"))
    ]
    defense = [
        s
        for s in t3
        if s.item_type == "Defensive"
        or "defensive" in s.flags
        or _canon_stat_value(s.stats, "pprot") + _canon_stat_value(s.stats, "mprot") >= 40
        or _canon_stat_value(s.stats, "hp") >= 250
    ]
    hybrid = [s for s in t3 if s.item_type == "Hybrid" or "hybrid" in s.flags]

    slots = profile["build_slots"]
    # Pick extra candidates so we can always fill 6 non-starter slots
    core_n = max(slots["cores"], 4)
    def_n = max(slots["defense"], 2)
    flex_n = max(slots["flex"], 2)
    cores = pick_diverse(
        offense if role != "Support" else hybrid + defense + offense,
        core_n,
        "offense",
    )
    defs = pick_diverse(defense, def_n, "defense")
    flex_pool = hybrid + offense + defense
    flex_pool = [x for x in flex_pool if x.name not in {c.name for c in cores + defs}]
    flex_pool.sort(key=lambda x: x.role_score, reverse=True)
    flex = pick_diverse(flex_pool, flex_n, "offense")

    relics = [
        score_item_for_role(it, role, profile)
        for it in items
        if is_base_relic(it)
    ]
    for r in relics:
        r.role_score = score_relic(next(i for i in items if i["name"] == r.name), profile)
    relics.sort(key=lambda x: x.role_score, reverse=True)

    # Conquest: starter is separate; fill exactly 6 non-starter items
    max_act = DEFAULT_MAX_SHOP_ACTIVES
    items_6 = _fill_six_items(cores, defs, flex, t3, max_actives=max_act)
    prefer = profile.get("prefer_damage")
    items_6 = _ensure_pen_in_path(
        items_6,
        t3,
        role,
        max_act,
        mage=(prefer == "Magical"),
        physical=(prefer == "Physical"),
    )
    items_6 = _order_buy_path(items_6, role)
    pen_total = sum(item_pen_value(x) for x in items_6)
    n_act = sum(1 for x in items_6 if x.is_active_item)

    return {
        "role": role,
        "description": profile["description"],
        "stat_priorities": profile["stat_weights"],
        "build_notes": (
            f"Buy order: early power → penetration → more power → defense → luxury. "
            f"Shop actives {n_act}/{max_act} (hard game max {HARD_MAX_ACTIVE_ITEMS}; "
            f"curios share that budget). Build pen ≈ {pen_total:.0f}."
        ),
        "max_shop_actives": max_act,
        "hard_max_actives": HARD_MAX_ACTIVE_ITEMS,
        "pen_total": round(pen_total, 1),
        "starter": _item_card(starters[0]) if starters else None,
        "starter_alternatives": [_item_card(s) for s in starters[1:3]],
        "upgraded_starter": _item_card(upgraded[0]) if upgraded else None,
        "core_items": [_item_card(c) for c in cores[:4]],
        "defense_items": [_item_card(d) for d in defs[:2]],
        "flex_items": [_item_card(f) for f in flex[:2]],
        "items": [_item_card(p) for p in items_6],  # exactly 6, buy-order sorted
        "full_path": [_item_card(p) for p in items_6],
        "inventory_slots": 7,  # 1 starter + 6 items
        "relics": [_item_card(r) for r in relics[:2]],
        "top_scored_items": [_item_card(s) for s in t3[:8]],
    }


def build_god_build(
    conn: sqlite3.Connection,
    items: list[dict],
    role: str,
    god: dict,
) -> dict[str, Any]:
    profile = ROLE_PROFILES[role]
    bias = god_scaling_bias(conn, god["god_id"])
    dtype = god.get("primary_damage_type")
    scored = []
    for it in items:
        base = score_item_for_role(it, role, profile)
        base.role_score = rescore_for_god(base, bias, role, damage_type=dtype)
        scored.append(base)
    scored.sort(key=lambda x: x.role_score, reverse=True)

    starters = [s for s in scored if is_t1_starter(next(i for i in items if i["name"] == s.name))]
    for s in starters:
        raw = next(i for i in items if i["name"] == s.name)
        s.role_score = score_starter(raw, profile) + rescore_for_god(
            s, bias, role, damage_type=dtype
        ) * 0.2
        # Solo: Warrior's Axe / Bluestone over pure support Selflessness when STR/INT bruiser
        if role == "Solo" and "selfless" in s.name.lower() and bias.get("primary") != "Mixed":
            if (bias.get("str") or 0) > 0.15 or (bias.get("int") or 0) > 0.15:
                s.role_score -= 15
    starters.sort(key=lambda x: x.role_score, reverse=True)

    t3 = [s for s in scored if is_t3_core(next(i for i in items if i["name"] == s.name))]
    primary = bias.get("primary") or ""
    mage = primary == "Intelligence" or (dtype or "").lower() == "magical"
    physical = (primary == "Strength" or (dtype or "").lower() == "physical") and not mage

    def kit_ok(s: ScoredItem) -> bool:
        str_v = _canon_stat_value(s.stats, "str")
        int_v = _canon_stat_value(s.stats, "int")
        as_v = _canon_stat_value(s.stats, "as")
        crit_v = _canon_stat_value(s.stats, "crit")
        bap = _canon_stat_value(s.stats, "bap")
        if mage:
            # Reject basic-attack / STR toys on pure mages
            if str_v >= 30 and int_v < 40:
                return False
            if (as_v >= 15 or crit_v >= 15 or bap >= 15) and int_v < 50:
                return False
            return int_v >= 25 or s.item_type == "Defensive" or _canon_stat_value(s.stats, "hp") >= 250
        if physical:
            if int_v >= 40 and str_v < 25:
                return False
            return str_v >= 20 or as_v > 0 or s.item_type == "Defensive" or _canon_stat_value(s.stats, "hp") >= 250
        return True

    t3 = [s for s in t3 if kit_ok(s)]
    offense = [
        s
        for s in t3
        if s.item_type != "Defensive"
        or _canon_stat_value(s.stats, "str") + _canon_stat_value(s.stats, "int") > 45
    ]
    # Damage roles: keep defense light (1 slot) so cores aren't crowded out
    def_n = 1 if role in DAMAGE_ROLES_NEED_PEN else max(profile["build_slots"]["defense"], 2)
    defense = [
        s
        for s in t3
        if s.item_type == "Defensive"
        or "defensive" in s.flags
        or (
            _canon_stat_value(s.stats, "hp") >= 250
            and _canon_stat_value(s.stats, "str") + _canon_stat_value(s.stats, "int") < 50
        )
    ]
    slots = profile["build_slots"]
    cores = pick_diverse(offense, max(slots["cores"], 5), "offense")
    defs = pick_diverse(
        [d for d in defense if d.name not in {c.name for c in cores}],
        def_n,
        "defense",
    )
    flex_pool = [x for x in t3 if x.name not in {c.name for c in cores + defs}]
    flex = pick_diverse(flex_pool, max(slots["flex"], 2), "offense")

    max_act = max_shop_actives_for_god(role, dtype, bias)
    items_6 = _fill_six_items(cores, defs, flex, t3, max_actives=max_act)
    items_6 = _ensure_pen_in_path(
        items_6, t3, role, max_act, mage=mage, physical=physical
    )
    if role in DAMAGE_ROLES_NEED_PEN:
        items_6 = _trim_excess_defense(items_6, t3, max_defense=1, max_actives=max_act)
    items_6 = _order_buy_path(items_6, role)
    pen_total = sum(item_pen_value(x) for x in items_6)
    n_act = sum(1 for x in items_6 if x.is_active_item)

    relics = [s for s in scored if is_base_relic(next(i for i in items if i["name"] == s.name))]
    for r in relics:
        r.role_score = score_relic(next(i for i in items if i["name"] == r.name), profile)
        if bias.get("mobility", 0) == 0 and "blink" in r.name.lower():
            r.role_score += 12
        if bias.get("cc", 0) >= 2 and "bead" in r.name.lower():
            r.role_score += 8
    relics.sort(key=lambda x: x.role_score, reverse=True)

    return {
        "god": god["entity_name"],
        "role": role,
        "tier": god.get("tier"),
        "rank": god.get("rank_in_scope"),
        "model_score": god.get("score"),
        "damage_type": god.get("primary_damage_type"),
        "pantheon": god.get("pantheon"),
        "scaling": bias.get("primary"),
        "avg_str_scaling": round((bias.get("str") or 0) * 100, 1),
        "avg_int_scaling": round((bias.get("int") or 0) * 100, 1),
        "starter": _item_card(starters[0]) if starters else None,
        "items": [_item_card(p) for p in items_6],
        "full_path": [_item_card(p) for p in items_6],
        "inventory_slots": 7,
        "cores": [_item_card(c) for c in cores[:4]],
        "defense": [_item_card(d) for d in defs[:2]],
        "relics": [_item_card(r) for r in relics[:2]],
        "max_shop_actives": max_act,
        "hard_max_actives": HARD_MAX_ACTIVE_ITEMS,
        "active_count": n_act,
        "pen_total": round(pen_total, 1),
        "why": _explain_god_build(god, bias, role, items_6, starters, pen_total, n_act, max_act),
    }


def _fill_six_items(
    cores: list[ScoredItem],
    defs: list[ScoredItem],
    flex: list[ScoredItem],
    t3_pool: list[ScoredItem],
    max_actives: int = MAX_ACTIVE_ITEMS,
) -> list[ScoredItem]:
    """
    Assemble exactly 6 non-starter items (Conquest full build).

    Enforces SMITE 2 rule: at most `max_actives` (default 3) shop Active items.
    Relics are not in this list.
    """
    path: list[ScoredItem] = []
    seen: set[str] = set()
    active_count = 0

    def try_add(it: ScoredItem) -> bool:
        nonlocal active_count
        if it.name in seen:
            return False
        # never put starters in the 6-item grid
        if it.tier in ("1", "Starter") or (
            it.total_cost and it.total_cost < 800 and "starter" in (it.item_type or "").lower()
        ):
            if (it.total_cost or 0) < 1500:
                return False
        if it.is_active_item and active_count >= max_actives:
            return False
        path.append(it)
        seen.add(it.name)
        if it.is_active_item:
            active_count += 1
        return True

    def add_from(group: list[ScoredItem]) -> None:
        for it in group:
            if len(path) >= 6:
                return
            try_add(it)

    # Prefer highest-scored picks first, but respect active cap
    add_from(cores)
    add_from(defs)
    add_from(flex)
    if len(path) < 6:
        rest = [x for x in t3_pool if x.name not in seen]
        # Prefer passives to fill remaining slots once actives are full
        rest.sort(
            key=lambda x: (x.role_score - (80 if x.is_active_item and active_count >= max_actives else 0)),
            reverse=True,
        )
        add_from(rest)

    # If still short (too many actives blocked everything), force passives only
    if len(path) < 6:
        passives = [
            x
            for x in t3_pool
            if x.name not in seen and not x.is_active_item
        ]
        passives.sort(key=lambda x: x.role_score, reverse=True)
        add_from(passives)

    return path[:6]


def _item_card(it: ScoredItem | None) -> dict | None:
    if not it:
        return None
    top_stats = sorted(it.stats.items(), key=lambda x: -abs(x[1]))[:5]
    pen = item_pen_value(it)
    return {
        "name": it.name,
        "score": round(it.role_score, 1),
        "cost": it.total_cost,
        "type": it.item_type or it.tier,
        "slot": _slot_label(it),
        "momentum": round(it.momentum, 2),
        "stats": {k: v for k, v in top_stats},
        "pen": round(pen, 1) if pen else 0,
        "effect": (it.passive or it.active or "")[:180],
        "is_active": bool(it.is_active_item),
    }


def _explain_god_build(god, bias, role, path, starters, pen_total=0.0, n_act=0, max_act=2) -> str:
    parts = [
        f"{god['entity_name']} ({role}): {bias.get('primary')} scaling "
        f"(STR {(bias.get('str') or 0)*100:.0f}% / INT {(bias.get('int') or 0)*100:.0f}%).",
        f"Buy order early→late. Pen total ≈ {pen_total:.0f}. "
        f"Shop actives {n_act}/{max_act} (game hard max {HARD_MAX_ACTIVE_ITEMS}; curio shares budget).",
    ]
    pens = [p.name for p in path if is_pen_item(p)]
    if pens:
        parts.append("Pen: " + ", ".join(pens) + ".")
    elif role in DAMAGE_ROLES_NEED_PEN:
        parts.append("Warning: low pen — check Obsidian Shard / Spear / Titan's.")
    if bias.get("cc", 0) >= 2:
        parts.append("CC-heavy kit → CDR/peel valued.")
    if god.get("tier"):
        parts.append(f"Model tier {god.get('tier')} (#{god.get('rank_in_scope')}).")
    return " ".join(parts)


def generate_all(conn: sqlite3.Connection, gods_per_role: int = 4) -> dict[str, Any]:
    items = load_items(conn)
    report: dict[str, Any] = {
        "game": "SMITE 2",
        "mode": "Conquest",
        "method": (
            "Local statistical weighting: item stats × role priority + utility tags + "
            "cost band + patch momentum; per-god rescoring by kit STR/INT scaling. "
            f"Shop actives default max {DEFAULT_MAX_SHOP_ACTIVES} "
            f"(hard game max {HARD_MAX_ACTIVE_ITEMS}; melee physical may use 3). "
            "Curios share the active budget and drop at 3. Relics are separate. "
            f"Damage roles (Carry/Mid/Jungle) enforce ≥{MIN_BUILD_PEN:.0f} pen and "
            "prefer passive shred (Obsidian Shard / Titan's Bane / Spears) over pure power. "
            "Items listed in buy order (early power → pen → power → defense → luxury). "
            "No external build sites."
        ),
        "max_active_items": DEFAULT_MAX_SHOP_ACTIVES,
        "hard_max_active_items": HARD_MAX_ACTIVE_ITEMS,
        "default_max_shop_actives": DEFAULT_MAX_SHOP_ACTIVES,
        "min_build_pen": MIN_BUILD_PEN,
        "roles": {},
    }
    for role in ("Carry", "Mid", "Jungle", "Solo", "Support"):
        template = build_role_template(items, role)
        gods = top_gods_for_role(conn, role, limit=gods_per_role)
        god_builds = [build_god_build(conn, items, role, g) for g in gods]
        report["roles"][role] = {
            "template": template,
            "recommended_gods": god_builds,
        }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# SMITE 2 Conquest Builds — Statistically Weighted",
        "",
        report["method"],
        "",
        "> Not scraped from websites. Derived from wiki item stats, ability scaling, and patch-note item/god momentum in `smite2.db`.",
        "",
    ]
    for role, data in report["roles"].items():
        t = data["template"]
        lines.append(f"## {role}")
        lines.append("")
        lines.append(t["description"])
        lines.append("")
        lines.append("### Role stat priority vector")
        lines.append("")
        pri = sorted(t["stat_priorities"].items(), key=lambda x: -x[1])
        lines.append("| Stat | Weight |")
        lines.append("|------|-------:|")
        for k, v in pri:
            lines.append(f"| {k} | {v:.0%} |")
        lines.append("")
        lines.append("### Role template (best-in-role item scores)")
        lines.append("")
        if t["starter"]:
            lines.append(
                f"**Starter:** {t['starter']['name']} "
                f"(score {t['starter']['score']}, cost {t['starter']['cost']})"
            )
        if t.get("starter_alternatives"):
            alts = ", ".join(f"{a['name']} ({a['score']})" for a in t["starter_alternatives"])
            lines.append(f"**Starter alts:** {alts}")
        if t.get("upgraded_starter"):
            lines.append(
                f"**Upgrade path:** {t['upgraded_starter']['name']} "
                f"(score {t['upgraded_starter']['score']})"
            )
        lines.append("")
        lines.append(
            f"**Inventory: 1 starter + 6 items** · shop actives "
            f"**≤{DEFAULT_MAX_SHOP_ACTIVES}** typical / **{HARD_MAX_ACTIVE_ITEMS}** hard max "
            "(curios share active budget; relics separate)"
        )
        lines.append("")
        if t["starter"]:
            lines.append(
                f"| Starter | **{t['starter']['name']}** | `{t['starter']['score']}` | {t['starter']['cost']}g |"
            )
        lines.append("")
        lines.append("| Buy# | Item | Slot | Active | Pen | Cost |")
        lines.append("|-----:|------|------|:------:|----:|-----:|")
        items6 = t.get("items") or t["full_path"]
        n_act = sum(1 for it in items6 if it.get("is_active"))
        pen_t = t.get("pen_total") or sum(it.get("pen") or 0 for it in items6)
        for i, it in enumerate(items6, 1):
            act = "A" if it.get("is_active") else ""
            pen = it.get("pen") or "—"
            lines.append(
                f"| {i} | **{it['name']}** | {it.get('slot', '')} | {act} | {pen} | {it['cost']}g |"
            )
        lines.append("")
        lines.append(
            f"*Actives {n_act}/{t.get('max_shop_actives', DEFAULT_MAX_SHOP_ACTIVES)} · pen ≈ {pen_t}*"
        )
        if t.get("build_notes"):
            lines.append("")
            lines.append(t["build_notes"])
        lines.append("")
        lines.append("**Relics:** " + ", ".join(r["name"] for r in t["relics"]))
        lines.append("")
        lines.append("### Top gods in this role + buy paths")
        lines.append("")
        for gb in data["recommended_gods"]:
            lines.append(
                f"#### {gb['god']} — {gb.get('tier') or '?'}-tier "
                f"(role rank #{gb.get('rank')}, model {gb.get('model_score') and round(gb['model_score'],1)})"
            )
            lines.append("")
            lines.append(
                f"*{gb['damage_type']} · {gb.get('scaling')} scaling "
                f"(STR {gb.get('avg_str_scaling')}% / INT {gb.get('avg_int_scaling')}%)*"
            )
            lines.append("")
            lines.append(gb["why"])
            lines.append("")
            if gb.get("starter"):
                lines.append(f"- **Starter:** {gb['starter']['name']}")
            items_g = gb.get("items") or gb["full_path"]
            n_act = sum(1 for it in items_g if it.get("is_active"))
            max_a = gb.get("max_shop_actives", DEFAULT_MAX_SHOP_ACTIVES)
            lines.append(
                f"- **Buy order** (actives {n_act}/{max_a}, pen ≈ {gb.get('pen_total', '?')}):"
            )
            for i, it in enumerate(items_g, 1):
                bits = [it.get("slot") or ""]
                if it.get("is_active"):
                    bits.append("active")
                if it.get("pen"):
                    bits.append(f"pen {it['pen']}")
                bits.append(f"{it['cost']}g")
                lines.append(f"  {i}. {it['name']} ({', '.join(b for b in bits if b)})")
            if gb.get("relics"):
                lines.append(
                    "- **Relics:** "
                    + ", ".join(f"{r['name']} ({r['score']})" for r in gb["relics"])
                )
            lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Conquest role builds from local stats")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--gods", type=int, default=4, help="Top gods per role")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "conquest_builds.md",
    )
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args(argv)

    if not args.db.exists():
        print(f"DB not found: {args.db}")
        return 1

    conn = connect(args.db)
    report = generate_all(conn, gods_per_role=args.gods)
    conn.close()

    md = render_markdown(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(md, encoding="utf-8")
    print(f"Wrote {args.output}")

    json_path = args.json or args.output.with_suffix(".json")
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {json_path}")

    # also print compact summary to stdout
    print("\n" + "=" * 72)
    for role, data in report["roles"].items():
        t = data["template"]
        items6 = t.get("items") or t["full_path"]
        print(f"\n### {role.upper()}")
        n_act = sum(1 for p in items6 if p.get("is_active"))
        print(f"  Starter: {t['starter']['name'] if t['starter'] else '—'}")
        print(
            f"  Buy order ({len(items6)}, A{n_act}/{t.get('max_shop_actives', DEFAULT_MAX_SHOP_ACTIVES)}, "
            f"pen≈{t.get('pen_total', '?')}): "
            + " → ".join(
                p["name"]
                + ("*" if p.get("is_active") else "")
                + (f"[pen{p.get('pen')}]" if p.get("pen") else "")
                for p in items6
            )
        )
        print("  Relics:  " + ", ".join(r["name"] for r in t["relics"]))
        print("  Gods:")
        for gb in data["recommended_gods"]:
            path = gb.get("items") or gb["full_path"]
            ga = sum(1 for p in path if p.get("is_active"))
            max_a = gb.get("max_shop_actives", DEFAULT_MAX_SHOP_ACTIVES)
            print(
                f"    [{gb.get('tier')}] {gb['god']} (A{ga}/{max_a} pen≈{gb.get('pen_total', '?')}): "
                f"[{gb['starter']['name'] if gb.get('starter') else '?'}] + "
                + " → ".join(
                    p["name"] + ("*" if p.get("is_active") else "") for p in path[:6]
                )
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
