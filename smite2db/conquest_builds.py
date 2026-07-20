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
            "Conquest duo ADC (backline): sustained basic-attack DPS, crit, "
            "penetration, and lifesteal. Support peels so you can free-hit."
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
            "gilded": 40,
            "arrow": 36,
            "death": 32,
            "toll": 30,
            "cowl": 28,
            "leather": 26,
            "shroud": 12,
            "vampiric": 10,
            "bluestone": 8,
            "selfless": -50,
            "flag": -45,
            "bumba": -20,
            "warrior": -15,
            "conduit": -10,  # mage starter — physical ADC default
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
            "Conquest mid (backline): ability burst, wave clear, INT power, "
            "penetration, CDR. Support peels so you can unload combos."
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
            "conduit": 42,
            "sands": 38,
            "pendulum": 34,
            "archmage": 32,
            "vampiric": 26,
            "shroud": 22,
            "bluestone": 16,
            "death": 10,
            "selfless": -55,
            "flag": -50,
            "bumba": -25,
            "gilded": -15,
            "leather": -15,
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
            "Conquest jungle — job is ganks: Bumba clear, burst pen, CDR, "
            "Blink/mobility relics, enough HP to invade. Not a full-tank solo."
        ),
        "prefer_damage": None,
        "stat_weights": {
            "str": 0.14,
            "int": 0.12,
            "pen": 0.22,   # shred tanks so ganks stick
            "cdr": 0.16,   # ability uptime for multi-gank
            "hp": 0.10,
            "as": 0.08,
            "ls": 0.06,
            "crit": 0.04,
            "pprot": 0.04,
            "mprot": 0.04,
        },
        "tag_bonus": {"offensive": 14, "passive": 6, "active": 3, "ms": 8, "cc": 6},
        "starter_prefs": {
            "bumba": 42,
            "dagger": 32,
            "cudgel": 30,
            "spear": 28,
            "hammer": 26,
            "death": 10,
            "bluestone": 8,
            "conduit": 6,
            "selfless": -20,
            "flag": -20,
            "warrior": -10,
        },
        "relic_prefs": {
            "blink": 32,       # gank setup
            "beads": 22,
            "sundering": 20,   # execute / shell break
            "agility": 18,
            "aegis": 12,
            "phantom": 10,
        },
        "build_slots": {"starter": 1, "cores": 4, "defense": 1, "flex": 1},
        "tier_scope": "role:Jungle",
    },
    "Solo": {
        "description": (
            "Conquest solo — unkillable frontliner: dual prots, HP, Dampening/"
            "Plating/Tenacity, hybrid offline damage. Absorb pressure so mid/ADC free-hit."
        ),
        "prefer_damage": None,
        "stat_weights": {
            "hp": 0.18,
            "pprot": 0.16,
            "mprot": 0.16,
            "damp": 0.10,
            "plat": 0.08,
            "ten": 0.08,
            "cdr": 0.08,
            "str": 0.06,   # offline damage only — not glass
            "int": 0.05,
            "ls": 0.03,
            "pen": 0.02,
            "hpr": 0.0,
            "as": 0.0,
            "mp": 0.0,
        },
        "tag_bonus": {
            "defensive": 18,
            "hybrid": 14,
            "passive": 8,
            "offensive": -4,  # pure glass cores wrong for frontline
            "shield": 8,
        },
        "starter_prefs": {
            "warrior": 42,
            "axe": 40,
            "bluestone": 34,
            "sundering": 30,
            "shroud": 12,
            "vampiric": 10,
            "selfless": -15,  # support starter — not solo identity
            "flag": -20,
            "bumba": -25,
            "gilded": -30,
            "conduit": -15,
        },
        "relic_prefs": {
            "beads": 26,
            "aegis": 24,
            "shell": 16,
            "phantom": 14,
            "blink": 10,
            "sundering": 12,
            "agility": 6,
        },
        "build_slots": {"starter": 1, "cores": 2, "defense": 3, "flex": 1},
        "tier_scope": "role:Solo",
    },
    "Support": {
        "description": (
            "Conquest support — peel for ADC & mid: dual prots, Damp/Plat/Ten, "
            "anti-AS, anti-crit, aura/team utility. Body-block & counter, not personal DPS."
        ),
        "prefer_damage": None,
        "stat_weights": {
            "hp": 0.16,
            "pprot": 0.15,
            "mprot": 0.15,
            "damp": 0.12,   # reduces damage taken (esp. ability / on-hit stacks)
            "plat": 0.10,   # plating — crit / basic mitigation
            "ten": 0.08,    # tenacity — stay online through CC
            "cdr": 0.10,
            "int": 0.04,
            "str": 0.02,
            "mp": 0.03,
            "hpr": 0.02,
            "pen": 0.02,
            "as": 0.0,      # do not chase personal AS
            "ls": 0.0,      # supports do not core lifesteal
            "mpr": 0.01,
        },
        "tag_bonus": {
            "defensive": 18,
            "hybrid": 12,
            "passive": 8,
            "active": 4,
            "offensive": -6,  # pure glass DPS cores are wrong here
            "team": 10,
            "aura": 10,
            "antiheal": 8,
        },
        "starter_prefs": {
            "selfless": 40,
            "war": 36,
            "flag": 36,
            "banner": 32,
            "heroism": 30,
            # hard-avoid damage/sustain starters on support
            "vampiric": -40,
            "shroud": -30,
            "conduit": -25,
            "death": -30,
            "gilded": -30,
            "bluestone": -15,
            "bumba": -35,
        },
        "relic_prefs": {
            "beads": 30,
            "purification": 28,
            "aegis": 24,
            "shell": 20,
            "phantom": 16,
            "talisman": 20,
            "blink": 8,
            "sundering": 6,
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
    "plat": ("plat", "plating", "plate"),
    "ten": ("ten", "tenacity"),
    "echo": ("echo",),
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
    is_active_item: bool = False
    recent_momentum: float = 0.0
    patch_axes: dict[str, float] = field(default_factory=dict)
    patch_axes_r5: dict[str, float] = field(default_factory=dict)


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


def _parse_axes_json(raw: str | None) -> dict[str, float]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}
    if not isinstance(data, dict):
        return {}
    out: dict[str, float] = {}
    for k, v in data.items():
        try:
            out[str(k)] = float(v)
        except (TypeError, ValueError):
            continue
    return out


def load_items(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        """
        SELECT name, tier, item_type, cost, total_cost, stats_json, stats_text,
               passive, active, categories
        FROM items
        """
    ).fetchall()
    momentum: dict[str, float] = {}
    recent_mom: dict[str, float] = {}
    item_axes: dict[str, dict[str, float]] = {}
    item_axes_r5: dict[str, dict[str, float]] = {}
    try:
        for r in conn.execute(
            """
            SELECT entity_name, net_weighted_score, recent_5_score,
                   axes_json, recent_axes_json
            FROM entity_patch_summary WHERE entity_type='item'
            """
        ):
            name = r["entity_name"]
            momentum[name] = r["net_weighted_score"] or 0.0
            recent_mom[name] = r["recent_5_score"] or 0.0
            item_axes[name] = _parse_axes_json(r["axes_json"] if "axes_json" in r.keys() else None)
            item_axes_r5[name] = _parse_axes_json(
                r["recent_axes_json"] if "recent_axes_json" in r.keys() else None
            )
    except sqlite3.OperationalError:
        for r in conn.execute(
            "SELECT entity_name, net_weighted_score FROM entity_patch_summary WHERE entity_type='item'"
        ):
            momentum[r["entity_name"]] = r["net_weighted_score"] or 0.0
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
                "recent_momentum": recent_mom.get(r["name"], 0.0),
                "patch_axes": item_axes.get(r["name"], {}),
                "patch_axes_r5": item_axes_r5.get(r["name"], {}),
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
        "damp": 20,   # 15 Damp on Alchemist is huge
        "plat": 15,   # 10–15 Plating is full value
        "ten": 20,
        "echo": 30,
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
            util += 22
        if "cleanse" in blob or "cc immune" in blob:
            util += 12
        if "shield" in blob:
            util += 10
        # Counter meta: anti basic-attack / crit / AS (mitigate carries)
        if "critical" in blob or (
            "crit" in blob
            and any(k in blob for k in ("reduc", "mitigat", "take -", "plating", "less damage"))
        ):
            util += 20
        if "attack speed" in blob and any(k in blob for k in ("reduc", "slow", "enemy", "their")):
            util += 18
        if "basic attack" in blob and any(k in blob for k in ("reduc", "less", "mitigat", "enemy")):
            util += 14
        if "heal" in blob and any(k in blob for k in ("reduc", "anti", "curse")):
            util += 12
        # Dampening / Plating / Tenacity are support identity stats
        util += _canon_stat_value(item["stats"], "damp") * 1.2
        util += _canon_stat_value(item["stats"], "plat") * 1.4
        util += _canon_stat_value(item["stats"], "ten") * 0.9
        # Lifesteal cores are wrong on support
        ls_v = _canon_stat_value(item["stats"], "ls")
        if ls_v >= 5:
            util -= 22
        nlow = item["name"].lower()
        if "vampiric" in nlow or (nlow.startswith("blood") and "bound" not in nlow):
            util -= 18
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

    # patch momentum (recent meta signal) — recent_5 weighted harder
    mom = (item.get("momentum") or 0) * 6 + (item.get("recent_momentum") or 0) * 12
    # Item's own patch axes: if item was buffed on pen/damage, prefer it
    ia = item.get("patch_axes_r5") or item.get("patch_axes") or {}
    axis_boost = 0.0
    if ia:
        axis_boost += float(ia.get("damage", 0) or 0) * 10
        axis_boost += float(ia.get("pen", 0) or 0) * 14
        axis_boost += float(ia.get("survivability", 0) or 0) * 8
        axis_boost += float(ia.get("cooldown", 0) or 0) * 6
        axis_boost += float(ia.get("attack_speed", 0) or 0) * 8
        axis_boost += float(ia.get("crit", 0) or 0) * 8
        axis_boost += float(ia.get("heal", 0) or 0) * 6
    mom += axis_boost
    breakdown["momentum"] = round(mom, 2)
    breakdown["item_axes"] = round(axis_boost, 2)

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
        recent_momentum=float(item.get("recent_momentum") or 0),
        patch_axes=dict(item.get("patch_axes") or {}),
        patch_axes_r5=dict(item.get("patch_axes_r5") or {}),
    )


def score_starter(item: dict, profile: dict, role: str | None = None) -> float:
    """Rank T1 starters. Pref keys dominate — do not let tank stats steal Mid/Carry."""
    name = item["name"].lower()
    base = 0.0
    penalty = 0.0
    for key, w in profile.get("starter_prefs", {}).items():
        if key in name:
            if w >= 0:
                base = max(base, w)
            else:
                penalty += w  # e.g. Support hard-bans Vampiric / Conduit
    # Light stat nudge only (prefs must win). Use role when known.
    role_for_stats = role or "Mid"
    scored = score_item_for_role(
        item, role_for_stats, {**profile, "stat_weights": profile["stat_weights"]}
    )
    return base + penalty + scored.role_score * 0.08 + (item.get("momentum") or 0) * 3


def pick_god_starter(
    starters: list[ScoredItem],
    items: list[dict],
    profile: dict,
    bias: dict,
    role: str,
    damage_type: str | None,
) -> ScoredItem | None:
    """Choose a kit-fit T1 starter — role prefs + kit tags, not generic tank score."""
    if not starters:
        return None
    dtype = (damage_type or "").lower()
    mage = dtype == "magical" or bias.get("primary") == "Intelligence"
    physical = (not mage) and (
        dtype == "physical" or bias.get("primary") == "Strength"
    )
    tags = set(bias.get("tags") or [])
    gname = str(bias.get("god_name") or "")

    ranked: list[tuple[float, ScoredItem]] = []
    for s in starters:
        raw = next(i for i in items if i["name"] == s.name)
        sc = score_starter(raw, profile, role=role)
        n = s.name.lower()

        # Hard role identity
        if role in ("Mid", "Carry", "Jungle"):
            if "selfless" in n or n in ("war flag",) or n.startswith("war flag"):
                sc -= 90
            if "war flag" in n or (n.startswith("war ") and "banner" not in n and role != "Support"):
                if "flag" in n:
                    sc -= 70
        if role == "Support":
            if any(k in n for k in ("conduit", "death", "gilded", "bumba", "vampiric", "sands")):
                sc -= 50
            if "selfless" in n or "flag" in n:
                sc += 25
        if role == "Jungle":
            if "bumba" in n:
                sc += 45
            else:
                sc -= 30
        if role == "Solo":
            if any(k in n for k in ("warrior", "axe", "bluestone")):
                sc += 35
            if "selfless" in n:
                sc -= 40
            if "bumba" in n:
                sc -= 35

        # Damage-type fit
        if mage:
            if any(k in n for k in ("conduit", "sands", "vampiric", "archmage", "pendulum")):
                sc += 30
            if any(k in n for k in ("gilded", "leather", "death")):
                sc -= 20
        if physical and role in ("Carry", "Jungle"):
            if any(k in n for k in ("gilded", "death", "leather", "cowl", "arrow", "bluestone")):
                sc += 28
            if "conduit" in n or "sands" in n:
                sc -= 18

        # Kit tags
        if "mana_stack" in tags and any(k in n for k in ("conduit", "sands")):
            sc += 22
        if ("aa" in tags or float(bias.get("aa_score") or 0) >= 0.55) and any(
            k in n for k in ("gilded", "leather", "death", "cowl", "arrow")
        ):
            sc += 20
        if ("heal" in tags or "self_sustain" in tags) and any(
            k in n for k in ("vampiric", "death", "shroud")
        ):
            sc += 14
        if "spam" in tags and any(k in n for k in ("sands", "pendulum", "conduit")):
            sc += 12
        if float(bias.get("patch_axes_r5", {}).get("mana", 0) or 0) >= 0.2 and "conduit" in n:
            sc += 10

        # Stable micro-diversity so near-ties don't all clone
        if gname:
            sc += (sum(ord(c) for c in (gname + s.name)) % 11) * 0.35

        ranked.append((sc, s))

    ranked.sort(key=lambda t: t[0], reverse=True)
    return ranked[0][1]


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


def god_scaling_bias(conn: sqlite3.Connection, god_id: int) -> dict[str, Any]:
    """
    Full per-god kit profile used for itemization.

    Combines ability metrics (burst/dps/dot/shield/cc), ability text cues,
    and patch trajectory so builds diverge across gods in the same role.
    """
    row = conn.execute(
        """
        SELECT primary_scaling, avg_scaling_str, avg_scaling_int, kit_power_score,
               kit_burst_score, kit_dps_score, kit_utility_score,
               cc_count, heal_count, mobility_count, min_ability_cd, ult_cooldown
        FROM god_kit_metrics WHERE god_id=?
        """,
        (god_id,),
    ).fetchone()
    if not row:
        return {
            "str": 0.5,
            "int": 0.5,
            "cc": 0,
            "heal": 0,
            "mobility": 0,
            "kit": 40,
            "burst": 0.5,
            "ult_scale": 0.0,
            "ability_power": 40.0,
            "tags": set(),
            "style_burst": 0.5,
            "style_dps": 0.5,
            "style_utility": 0.3,
            "kit_burst": 20.0,
            "kit_dps": 20.0,
            "dots": 0,
            "shields": 0,
            "patch_score": 0.0,
            "recent_patch": 0.0,
            "trajectory": "stable",
            "patch_axes": {},
            "patch_axes_r5": {},
            "god_name": "",
            "aa_score": 0.0,
            "avg_cd": 12.0,
        }

    ab = conn.execute(
        """
        SELECT
          AVG(COALESCE(m.power_score, 0)) AS avg_pwr,
          MAX(COALESCE(m.power_score, 0)) AS max_pwr,
          MAX(CASE WHEN UPPER(a.slot) LIKE '%ULT%' OR a.slot_order >= 4
              THEN COALESCE(m.scaling_int_pct, 0) + COALESCE(m.scaling_str_pct, 0)
              ELSE 0 END) AS ult_scale,
          AVG(CASE WHEN m.cooldown_rank5 IS NOT NULL AND m.cooldown_rank5 > 0
              THEN m.cooldown_rank5 END) AS avg_cd,
          SUM(CASE WHEN COALESCE(m.has_cc, 0) THEN 1 ELSE 0 END) AS ab_cc,
          SUM(CASE WHEN COALESCE(m.has_mobility, 0) THEN 1 ELSE 0 END) AS ab_mob,
          SUM(CASE WHEN COALESCE(m.has_dot, 0) THEN 1 ELSE 0 END) AS ab_dot,
          SUM(CASE WHEN COALESCE(m.has_shield, 0) THEN 1 ELSE 0 END) AS ab_shield,
          SUM(CASE WHEN COALESCE(m.has_heal, 0) THEN 1 ELSE 0 END) AS ab_heal,
          AVG(COALESCE(m.burst_proxy, 0)) AS avg_burst_px,
          AVG(COALESCE(m.dps_proxy, 0)) AS avg_dps_px
        FROM abilities a
        LEFT JOIN ability_metrics m ON m.ability_id = a.id
        WHERE a.god_id = ?
        """,
        (god_id,),
    ).fetchone()

    # Ability text for keyword tags — exclude Basic Attack rows (they all say "basic attack")
    texts = conn.execute(
        """
        SELECT a.slot, a.name, a.description, a.stats_text, a.notes_text, a.slot_order
        FROM abilities a WHERE a.god_id = ?
        """,
        (god_id,),
    ).fetchall()
    kit_texts = []
    basic_texts = []
    for t in texts:
        slot_l = (t["slot"] or "").lower()
        chunk = (
            f"{t['slot'] or ''} {t['name'] or ''} {t['description'] or ''} "
            f"{t['stats_text'] or ''} {t['notes_text'] or ''}"
        ).lower()
        if "basic" in slot_l:
            basic_texts.append(chunk)
        else:
            kit_texts.append(chunk)
    blob = " ".join(kit_texts)  # kit only
    full_blob = " ".join(kit_texts + basic_texts)

    gname_row = conn.execute("SELECT name FROM gods WHERE id=?", (god_id,)).fetchone()
    god_name = gname_row["name"] if gname_row else ""

    patch = None
    try:
        patch = conn.execute(
            """
            SELECT net_weighted_score, recent_5_score, trajectory,
                   axes_json, recent_axes_json
            FROM entity_patch_summary
            WHERE entity_type='god' AND entity_name=?
            """,
            (god_name,),
        ).fetchone()
    except sqlite3.OperationalError:
        patch = conn.execute(
            """
            SELECT net_weighted_score, recent_5_score, trajectory
            FROM entity_patch_summary
            WHERE entity_type='god' AND entity_name=?
            """,
            (god_name,),
        ).fetchone()
    patch_score = float(patch["net_weighted_score"] or 0) if patch else 0.0
    recent_patch = float(patch["recent_5_score"] or 0) if patch else 0.0
    trajectory = (patch["trajectory"] if patch else None) or "stable"
    patch_axes = {}
    patch_axes_r5 = {}
    if patch:
        keys = patch.keys()
        if "axes_json" in keys:
            patch_axes = _parse_axes_json(patch["axes_json"])
        if "recent_axes_json" in keys:
            patch_axes_r5 = _parse_axes_json(patch["recent_axes_json"])

    avg_pwr = float(ab["avg_pwr"] or 40) if ab else 40.0
    max_pwr = float(ab["max_pwr"] or 40) if ab else 40.0
    ult_scale = float(ab["ult_scale"] or 0) if ab else 0.0
    # Non-ult average CD for spam detection
    cd_row = conn.execute(
        """
        SELECT AVG(m.cooldown_rank5) AS avg_cd
        FROM abilities a
        JOIN ability_metrics m ON m.ability_id = a.id
        WHERE a.god_id = ?
          AND m.cooldown_rank5 IS NOT NULL AND m.cooldown_rank5 > 0
          AND UPPER(COALESCE(a.slot,'')) NOT LIKE '%ULT%'
          AND COALESCE(a.slot_order, 0) < 4
        """,
        (god_id,),
    ).fetchone()
    avg_cd = float(cd_row["avg_cd"] or 12) if cd_row and cd_row["avg_cd"] else (
        float(ab["avg_cd"] or 12) if ab and ab["avg_cd"] else 12.0
    )
    dots = int(ab["ab_dot"] or 0) if ab else 0
    shields = int(ab["ab_shield"] or 0) if ab else 0
    ab_heal = int(ab["ab_heal"] or 0) if ab else 0

    kit_burst = float(row["kit_burst_score"] or 0)
    kit_dps = float(row["kit_dps_score"] or 0)
    kit_util = float(row["kit_utility_score"] or 0)
    total_style = max(kit_burst + kit_dps, 1.0)
    style_burst = kit_burst / total_style
    style_dps = kit_dps / total_style
    # Secondary burst ratio from ability power shape
    spike = min(1.5, max(0.2, max_pwr / max(avg_pwr, 1.0) - 0.35))

    tags: set[str] = set()
    # metric-driven tags
    if dots >= 1:
        tags.add("dot")
    if dots >= 2:
        tags.add("heavy_dot")
    if shields >= 1:
        tags.add("shield")
    if shields >= 2:
        tags.add("heavy_shield")
    if max(row["heal_count"] or 0, ab_heal) >= 1:
        tags.add("heal")
    if max(row["heal_count"] or 0, ab_heal) >= 3:
        tags.add("heavy_heal")
    if max(row["cc_count"] or 0, int(ab["ab_cc"] or 0) if ab else 0) >= 3:
        tags.add("high_cc")
    if max(row["mobility_count"] or 0, int(ab["ab_mob"] or 0) if ab else 0) == 0:
        tags.add("immobile")
    if max(row["mobility_count"] or 0, int(ab["ab_mob"] or 0) if ab else 0) >= 3:
        tags.add("mobile")
    if avg_cd <= 8.0:
        tags.add("spam")
    if avg_cd >= 14:
        tags.add("long_cd")
    if ult_scale >= 100:
        tags.add("ult_nuke")
    if style_burst >= 0.55 and kit_burst >= 25:
        tags.add("burst")
    if style_dps >= 0.55 and kit_dps >= 25:
        tags.add("sustained")
    if kit_util >= 55:
        tags.add("utility")

    # text-driven tags (non-basic ability descriptions only)
    aa_hits = len(re.findall(r"basic attack", blob))
    if aa_hits >= 2 or re.search(
        r"while active.{0,40}basic|basic attacks deal|your basic attacks|empowered basic|next basic",
        blob,
    ):
        tags.add("aa")
    # True mana-stacking passives only (e.g. Kukulkan: build Mana items → INT)
    if re.search(
        r"items that provide mana|build items that provide mana|"
        r"as you build.{0,40}mana.{0,40}intelligence|"
        r"mana items|from (?:your )?mana\b",
        blob,
    ):
        tags.add("mana_stack")
    if re.search(r"penetrat|protection.?reduc|shred|decompose|voids? their", blob):
        tags.add("prot_shred")
    if re.search(r"execut|low health|below \d|threshold|harvest|killing blow", blob):
        tags.add("execute")
    if re.search(r"\bchannel\b|channeling", blob):
        tags.add("channel")
    if re.search(r"\bpet\b|summon|deploy|create a wall|totem|minion", blob):
        tags.add("pet_zone")
    if re.search(r"damage over time|poison|burn|blight|frostbite|whirlwind", blob):
        tags.add("zone")
    if re.search(r"\broot\b|\bstun\b|silence|knock(?:\s|-)?back|cripple|mesmerize|\bfear\b", blob):
        tags.add("hard_cc")
    if re.search(r"gain.{0,20}attack speed|increased attack speed|attack speed for", blob):
        tags.add("as_steroid")
    if re.search(r"lifesteal|heal yourself|heals? you\b|restor(?:e|es) your|drain(?:s|ing)? life", blob):
        tags.add("self_sustain")
    if re.search(r"\ballies\b|\bally\b|\baura\b|nearby (?:friendly|allied)", blob):
        tags.add("team_buff")
    if re.search(r"slow immune|cc immune|crowd control immun", blob):
        tags.add("anti_cc")
    if re.search(r"\bdash\b|\bleap\b|teleport|fly into", blob):
        tags.add("gap_close")

    aa_score = min(1.0, aa_hits / 4.0)
    if "aa" in tags:
        aa_score = max(aa_score, 0.7)

    return {
        "str": (row["avg_scaling_str"] or 0) / 100.0,
        "int": (row["avg_scaling_int"] or 0) / 100.0,
        "primary": row["primary_scaling"] or "Mixed",
        "cc": max(row["cc_count"] or 0, int(ab["ab_cc"] or 0) if ab else 0),
        "heal": max(row["heal_count"] or 0, ab_heal),
        "mobility": max(row["mobility_count"] or 0, int(ab["ab_mob"] or 0) if ab else 0),
        "kit": row["kit_power_score"] or 40,
        "burst": spike,  # legacy key
        "ult_scale": ult_scale,
        "ability_power": avg_pwr,
        "avg_cd": avg_cd,
        "tags": tags,
        "style_burst": style_burst,
        "style_dps": style_dps,
        "style_utility": min(1.0, kit_util / 100.0),
        "kit_burst": kit_burst,
        "kit_dps": kit_dps,
        "dots": dots,
        "shields": shields,
        "patch_score": patch_score,
        "recent_patch": recent_patch,
        "trajectory": trajectory,
        "patch_axes": patch_axes,
        "patch_axes_r5": patch_axes_r5,
        "god_name": god_name,
        "aa_score": aa_score,
        "ability_blob": blob[:4000],
        "full_blob": full_blob[:2000],
    }


def rescore_for_god(
    item: ScoredItem,
    bias: dict,
    role: str,
    damage_type: str | None = None,
) -> float:
    """Role base score + large per-god kit affinity (must move rankings)."""
    s = item.role_score * 0.55  # shrink generic role signal so kit can win
    str_v = _canon_stat_value(item.stats, "str")
    int_v = _canon_stat_value(item.stats, "int")
    as_v = _canon_stat_value(item.stats, "as")
    crit_v = _canon_stat_value(item.stats, "crit")
    pen_v = _canon_stat_value(item.stats, "pen")
    cdr_v = _canon_stat_value(item.stats, "cdr")
    ls_v = _canon_stat_value(item.stats, "ls")
    mp_v = _canon_stat_value(item.stats, "mp")
    primary = bias.get("primary", "Mixed")
    dtype = (damage_type or "").lower()
    tags: set[str] = set(bias.get("tags") or [])
    nlow = item.name.lower()
    blob = f"{item.passive} {item.active} {item.name}".lower()

    mage = dtype == "magical" or primary == "Intelligence"
    physical = (not mage) and (dtype == "physical" or primary == "Strength")

    # --- Damage-type alignment (hard) ---
    if mage:
        s += int_v * 1.15
        s -= str_v * 0.9
        s -= as_v * 0.55
        s -= crit_v * 0.65
        s -= _canon_stat_value(item.stats, "bap") * 0.5
        if str_v >= 30 and int_v < 35:
            s -= 60
        if str_v >= 40 and int_v < 25:
            s -= 80
    elif physical:
        s += str_v * 1.05
        s -= int_v * 0.7
        if int_v >= 40 and str_v < 25:
            s -= 60
        if role == "Carry":
            s += as_v * 0.55 + crit_v * 0.65 + ls_v * 0.4
    else:  # hybrid
        s += (str_v + int_v) * 0.45
        s += min(str_v, int_v) * 0.35

    if dtype == "physical" and int_v > str_v + 20:
        s -= 40
    if dtype == "magical" and str_v > int_v + 15:
        s -= 45

    # --- Role shells ---
    if role == "Support":
        s += (
            _canon_stat_value(item.stats, "hp") * 0.12
            + _canon_stat_value(item.stats, "pprot") * 0.5
            + _canon_stat_value(item.stats, "mprot") * 0.5
            + _canon_stat_value(item.stats, "damp") * 2.5
            + _canon_stat_value(item.stats, "plat") * 3.0
            + _canon_stat_value(item.stats, "ten") * 1.8
        )
        s -= as_v * 1.0 + crit_v * 1.0
        if ls_v >= 5:
            s -= 45
        if item.item_type == "Offensive" and _canon_stat_value(item.stats, "hp") < 200:
            s -= 35
        if item.item_type == "Defensive":
            s += 28
        if any(k in blob for k in ("ally", "allies", "aura", "team")):
            s += 28
        if "critical" in blob or ("crit" in blob and "plating" in blob):
            s += 24
        if "attack speed" in blob and any(k in blob for k in ("reduc", "enemy", "their")):
            s += 22
        # Support should not core pure antiheal DPS
        if any(k in nlow for k in ("divine ruin", "brawler", "titan", "obsi", "deathbringer")):
            s -= 30
    elif role == "Solo":
        s += (
            _canon_stat_value(item.stats, "hp") * 0.14
            + _canon_stat_value(item.stats, "pprot") * 0.5
            + _canon_stat_value(item.stats, "mprot") * 0.5
            + _canon_stat_value(item.stats, "damp") * 2.2
            + _canon_stat_value(item.stats, "plat") * 2.4
            + _canon_stat_value(item.stats, "ten") * 1.6
        )
        if item.item_type == "Defensive":
            s += 24
        if item.item_type == "Hybrid":
            s += 14
        if item.item_type == "Offensive" and _canon_stat_value(item.stats, "hp") < 200:
            s -= 32
        s -= as_v * 0.55 + crit_v * 0.7
        if any(k in blob for k in ("shield", "protections", "mitigat", "heal")):
            s += 16
    elif role == "Jungle":
        s += pen_v * 1.3 + cdr_v * 0.65
        if any(k in blob for k in ("jungle", "monster", "minion")):
            s += 18
        if item.item_type == "Defensive" and pen_v < 5 and (str_v + int_v) < 20:
            s -= 12

    # --- Kit tag affinities (LARGE — this is what diversifies gods) ---
    if "mana_stack" in tags:
        if mp_v >= 200 or "mana" in blob or any(
            k in nlow for k in ("thoth", "book", "doom orb", "pendant", "transcend")
        ):
            s += 55
        if "intelligence" in blob and "mana" in blob:
            s += 20
    if "dot" in tags or "heavy_dot" in tags:
        if any(k in nlow for k in ("desolat", "magus", "divine", "soul reaver", "contagion", "gem of isolation")):
            s += 42
        if "heavy_dot" in tags:
            s += pen_v * 0.8 + 12
        if "over time" in blob or "burn" in blob or "poison" in blob:
            s += 18
    if "aa" in tags or float(bias.get("aa_score") or 0) >= 0.55:
        s += as_v * 1.2 + crit_v * 1.1 + _canon_stat_value(item.stats, "bap") * 0.7
        if any(k in nlow for k in ("riptalon", "deathbringer", "demon", "qins", "ichival", "wind", "musashi", "avenging", "eros")):
            s += 38
        if mage and (as_v >= 15 or crit_v >= 15):
            s += 20  # AA mages are rare — reward AS hybrids
    if "burst" in tags or float(bias.get("style_burst") or 0) >= 0.55:
        s += pen_v * 0.9
        if (item.total_cost or 0) >= 2800 and (int_v >= 60 or str_v >= 45):
            s += 28
        if any(k in nlow for k in ("obsi", "titan", "soul reaver", "tahuti", "parashu", "dreamer", "rod of")):
            s += 22
    if "sustained" in tags or float(bias.get("style_dps") or 0) >= 0.55:
        s += cdr_v * 1.4
        if any(k in nlow for k in ("chronos", "pendant", "breastplate", "genji", "valor", "focus")):
            s += 30
        if ls_v >= 10:
            s += 18
    if "spam" in tags or float(bias.get("avg_cd") or 12) <= 8.5:
        s += cdr_v * 1.8 + 18
    if "channel" in tags:
        s += pen_v * 1.1 + 15
        if any(k in nlow for k in ("obsi", "titan", "desolat", "magus")):
            s += 25
        # channel gods need bulk mid-fight
        if _canon_stat_value(item.stats, "hp") >= 250 or item.item_type == "Defensive":
            s += 16
    if "heal" in tags or "heavy_heal" in tags or "self_sustain" in tags:
        if ls_v >= 8 or any(k in nlow for k in ("bancroft", "blood", "gluttonous", "asclepius", "lifebinder", "devourer", "sanguine")):
            s += 40
        if "heavy_heal" in tags and ("heal" in blob or "lifesteal" in blob):
            s += 18
    if "execute" in tags:
        s += pen_v * 1.2
        if any(k in nlow for k in ("titan", "obsi", "soul reaver", "deathbringer", "bloodforge")):
            s += 32
    if "prot_shred" in tags:
        if pen_v >= 8 or "penetrat" in blob or "protection" in blob:
            s += 28
        if any(k in nlow for k in ("magus", "executioner", "desolat", "void", "obsi", "titan")):
            s += 20
    if "shield" in tags or "heavy_shield" in tags:
        if item.item_type in ("Defensive", "Hybrid") or "shield" in blob:
            s += 30
        if any(k in nlow for k in ("pridwen", "phoenix", "shifter", "spectral", "thebes")):
            s += 18
    if "high_cc" in tags or "hard_cc" in tags:
        s += cdr_v * 1.3 + 12
        if role == "Support" and item.item_type == "Defensive":
            s += 10
    if "immobile" in tags:
        if item.item_type == "Defensive" or _canon_stat_value(item.stats, "hp") >= 250:
            s += 22
        if any(k in nlow for k in ("alchemist", "magi", "cloak", "mantle", "spectral")):
            s += 16
    if "mobile" in tags or "gap_close" in tags:
        if role == "Jungle":
            s += pen_v * 0.5 + 8
        if any(k in nlow for k in ("jotunn", "hydras", "arondight", "heartseeker")):
            s += 14
    if "pet_zone" in tags or "zone" in tags:
        if any(k in nlow for k in ("magus", "gem of isolation", "divine", "soul gem", "grimoire")):
            s += 26
        s += cdr_v * 0.4
    if "ult_nuke" in tags:
        s += pen_v * 1.0 + 14
        if any(k in nlow for k in ("obsi", "titan", "tahuti", "soul reaver", "dreamer")):
            s += 20
    if "team_buff" in tags and role in ("Support", "Solo"):
        if any(k in blob for k in ("ally", "allies", "aura", "team")):
            s += 32
    if "anti_cc" in tags:
        if _canon_stat_value(item.stats, "ten") >= 5 or "tenacit" in blob or "magi" in nlow:
            s += 24

    # --- Patch exploit: god axis vector + item momentum (role-gated) ---
    traj = (bias.get("trajectory") or "stable").lower()
    pscore = float(bias.get("patch_score") or 0)
    r5 = float(bias.get("recent_patch") or 0)
    frontline = role in ("Solo", "Support")
    damage_backline = role in DAMAGE_ROLES_NEED_PEN

    # Item momentum: strong on matching role; pure tanks don't invade Mid/Carry
    pure_tank = (
        item.item_type == "Defensive"
        and pen_v < 5
        and (str_v + int_v) < 35
        and as_v < 10
        and crit_v < 10
    )
    # Hybrid “offline tanks” that were flooding Mid via survivability momentum
    meta_bulk = any(
        k in nlow
        for k in (
            "shifter",
            "spectral armor",
            "gauntlet of thebes",
            "midgardian",
            "nemean",
            "heartwood",
            "radiant bulwark",
            "stygian",
        )
    ) and pen_v < 8
    mom_w = 8.0
    r_mom_w = 14.0
    dmg_gate = float((bias.get("patch_axes_r5") or {}).get("damage", 0) or 0)
    if damage_backline and (pure_tank or meta_bulk):
        mom_w = 1.5
        r_mom_w = 2.0
        # Only allow meta bulk if god was hard-nerfed on damage / falling hard
        if dmg_gate > -0.8 and r5 > -1.0:
            s -= 40  # backline stays glass + pen, not Shifter’s meta
    elif frontline and (pure_tank or meta_bulk):
        mom_w = 10.0
        r_mom_w = 18.0
    s += (item.momentum or 0) * mom_w + (item.recent_momentum or 0) * r_mom_w

    g_axes = bias.get("patch_axes_r5") or bias.get("patch_axes") or {}
    if not g_axes:
        g_axes = {}
    dmg_ax = float(g_axes.get("damage", 0) or 0)
    cd_ax = float(g_axes.get("cooldown", 0) or 0)
    pen_ax = float(g_axes.get("pen", 0) or 0)
    surv_ax = float(g_axes.get("survivability", 0) or 0)
    heal_ax = float(g_axes.get("heal", 0) or 0)
    as_ax = float(g_axes.get("attack_speed", 0) or 0)
    crit_ax = float(g_axes.get("crit", 0) or 0)
    mana_ax = float(g_axes.get("mana", 0) or 0)

    if dmg_ax >= 0.25:
        s += pen_v * 0.9 + 8
        if int_v >= 50 or str_v >= 40:
            s += 14
        if item.item_type == "Offensive":
            s += 10
    elif dmg_ax <= -0.35:
        if item.item_type == "Defensive" or _canon_stat_value(item.stats, "hp") >= 250:
            s += 18 if frontline else 12
        s += cdr_v * 0.8
        if item.is_active_item and (item.total_cost or 0) >= 3200:
            s -= 14
    if cd_ax >= 0.25:
        s += pen_v * 0.4 + (10 if (int_v >= 40 or str_v >= 30) else 0)
    elif cd_ax <= -0.25:
        s += cdr_v * 1.6 + 12
    if pen_ax >= 0.15:
        s += pen_v * 1.4 + 10
    if surv_ax >= 0.25 and frontline:
        s += (
            _canon_stat_value(item.stats, "hp") * 0.08
            + _canon_stat_value(item.stats, "pprot") * 0.25
            + _canon_stat_value(item.stats, "mprot") * 0.25
            + 8
        )
    elif surv_ax <= -0.25 and damage_backline:
        if _canon_stat_value(item.stats, "hp") >= 200 or item.item_type == "Defensive":
            s += 12
    if heal_ax >= 0.2 and (ls_v >= 8 or "heal" in blob):
        s += 18
    if as_ax >= 0.2:
        s += as_v * 1.1 + 10
    if crit_ax >= 0.15:
        s += crit_v * 1.2 + 10
    if mana_ax >= 0.2 and (
        _canon_stat_value(item.stats, "mp") >= 150
        or any(k in nlow for k in ("thoth", "book", "doom orb", "pendant"))
    ):
        s += 16

    # Item's own recent patch axes (meta) — role-gated
    ia = item.patch_axes_r5 or item.patch_axes or {}
    if ia:
        s += float(ia.get("damage", 0) or 0) * 12
        s += float(ia.get("pen", 0) or 0) * 16
        surv_item = float(ia.get("survivability", 0) or 0)
        if frontline:
            s += surv_item * 12
        elif damage_backline:
            s += surv_item * 2  # hot tanks barely pull backline
        else:
            s += surv_item * 8
        s += float(ia.get("cooldown", 0) or 0) * 8
        s += float(ia.get("attack_speed", 0) or 0) * 10
        s += float(ia.get("crit", 0) or 0) * 10

    if traj == "rising" or r5 >= 0.8 or pscore >= 1.0:
        if item.item_type == "Offensive":
            s += 10
    elif traj == "falling" or r5 <= -0.8 or pscore <= -1.5:
        if item.item_type == "Defensive" or _canon_stat_value(item.stats, "hp") >= 250:
            s += 14 if frontline else 8
        s += cdr_v * 0.4
        if item.is_active_item and (item.total_cost or 0) >= 3200:
            s -= 8

    # Damage-role pen requirement (matching type)
    if role in DAMAGE_ROLES_NEED_PEN:
        if mage:
            if int_v >= 30 and pen_v >= 8:
                s += pen_v * 1.8 + 14
            elif pen_v >= 8 and int_v < 25:
                s -= 30
            if pen_v >= 15 and int_v >= 45 and not item.is_active_item:
                s += 26
        elif physical:
            if str_v >= 25 and pen_v >= 8:
                s += pen_v * 1.7 + 12
            elif pen_v >= 15 and str_v >= 35 and not item.is_active_item:
                s += 24
            elif pen_v >= 8 and str_v < 20 and int_v >= 40:
                s -= 30
        else:
            s += pen_v * 1.3
        if pen_v >= 8 and item.is_active_item and (item.total_cost or 0) >= 3200:
            s -= 10

    # Deterministic per-god reordering so near-ties don't all pick the same flex.
    # Large enough to swap #1/#2 among peer items; kit tags + signatures still dominate.
    g = bias.get("god_name") or ""
    if g:
        h = sum((i + 1) * ord(c) for i, c in enumerate(g + "|" + item.name)) % 41
        s += h * 0.85

    return s


# ---------------------------------------------------------------------------
# Archetype recipes — force different slot patterns per kit identity
# ---------------------------------------------------------------------------

def detect_archetype(bias: dict, role: str, mage: bool, physical: bool) -> str:
    tags: set[str] = set(bias.get("tags") or [])
    sb = float(bias.get("style_burst") or 0.5)
    sd = float(bias.get("style_dps") or 0.5)
    aa = float(bias.get("aa_score") or 0)

    if role == "Support":
        if "heavy_heal" in tags or "heal" in tags and "team_buff" in tags:
            return "heal_support"
        if "heavy_shield" in tags or "shield" in tags:
            return "shield_support"
        if "high_cc" in tags or "hard_cc" in tags:
            return "lockdown_support"
        if "team_buff" in tags:
            return "aura_support"
        return "peel_support"

    if role == "Solo":
        # Frontline first — only pure mage tanks use mage_solo
        if "heavy_heal" in tags or ("heal" in tags and "self_sustain" in tags):
            return "sustain_solo"
        if "heavy_shield" in tags or "shield" in tags:
            return "shield_solo"
        if mage and float(bias.get("int") or 0) >= float(bias.get("str") or 0) + 0.2:
            return "mage_solo"
        if sb >= 0.55 and float(bias.get("kit_burst") or 0) >= 30:
            return "bruiser_solo"
        return "tank_solo"

    if role == "Jungle":
        if mage:
            return "mage_jungle"
        if "execute" in tags or "heal" in tags:
            return "sustain_assassin"
        if "aa" in tags or aa >= 0.55:
            return "aa_assassin"
        if sb >= sd + 0.08:
            return "burst_assassin"
        return "bruiser_jungle"

    if role == "Carry":
        if mage:
            if "dot" in tags:
                return "dot_mage_adc"
            if "aa" in tags or aa >= 0.5:
                return "aa_mage_adc"
            return "ability_mage_adc"
        if "aa" in tags or aa >= 0.55 or "as_steroid" in tags:
            return "crit_adc"
        if sd > sb:
            return "onhit_adc"
        return "power_adc"

    # Mid — most specific kit identity first
    if "mana_stack" in tags:
        return "mana_mage"
    if "heavy_dot" in tags or ("dot" in tags and "zone" in tags):
        return "dot_mage"
    if "channel" in tags and sb >= 0.45:
        return "channel_mage"
    if ("aa" in tags or aa >= 0.55) and float(bias.get("int") or 0) < 0.9:
        return "aa_mage"
    if "self_sustain" in tags or ("heal" in tags and "heavy_heal" in tags):
        return "sustain_mage"
    if "spam" in tags or (sd >= sb + 0.12 and float(bias.get("avg_cd") or 12) <= 9.0):
        return "spam_mage"
    if "pet_zone" in tags:
        return "zone_mage"
    if "ult_nuke" in tags or (sb >= 0.55 and float(bias.get("kit_burst") or 0) >= 20):
        return "burst_mage"
    if "dot" in tags:
        return "dot_mage"
    return "burst_mage"


# Slot recipes: ordered identity of the 6-item grid (pen still enforced later)
ARCHETYPE_SLOTS: dict[str, list[str]] = {
    # Mid / mage
    "burst_mage": ["power", "flat_pen", "pct_pen", "cdr", "defense", "luxury"],
    "dot_mage": ["flat_pen", "dot_core", "pct_pen", "sustain", "cdr", "defense"],
    "mana_mage": ["mana_stack", "flat_pen", "pct_pen", "cdr", "power", "defense"],
    "channel_mage": ["pct_pen", "flat_pen", "power", "defense", "cdr", "luxury"],
    "spam_mage": ["cdr", "flat_pen", "pct_pen", "power", "sustain", "defense"],
    "sustain_mage": ["sustain", "flat_pen", "pct_pen", "cdr", "power", "defense"],
    "aa_mage": ["aa_core", "flat_pen", "pct_pen", "as_core", "power", "defense"],
    "zone_mage": ["flat_pen", "zone_core", "pct_pen", "cdr", "power", "defense"],
    # Carry
    "crit_adc": ["as_core", "crit_core", "pct_pen", "ls_core", "power", "defense"],
    "onhit_adc": ["as_core", "onhit", "pct_pen", "ls_core", "power", "defense"],
    "power_adc": ["power", "pct_pen", "as_core", "ls_core", "crit_core", "defense"],
    "dot_mage_adc": ["dot_core", "flat_pen", "pct_pen", "sustain", "power", "defense"],
    "aa_mage_adc": ["as_core", "flat_pen", "pct_pen", "power", "ls_core", "defense"],
    "ability_mage_adc": ["power", "flat_pen", "pct_pen", "cdr", "sustain", "defense"],
    # Jungle
    "burst_assassin": ["power", "flat_pen", "pct_pen", "cdr", "gap", "defense"],
    "sustain_assassin": ["sustain", "flat_pen", "pct_pen", "power", "cdr", "defense"],
    "aa_assassin": ["as_core", "flat_pen", "pct_pen", "power", "ls_core", "defense"],
    "bruiser_jungle": ["power", "flat_pen", "pct_pen", "hybrid_bulk", "cdr", "defense"],
    "mage_jungle": ["power", "flat_pen", "pct_pen", "cdr", "sustain", "defense"],
    # Solo
    "tank_solo": ["mitigate", "defense", "hybrid_bulk", "antiheal", "aura", "cdr_def"],
    "sustain_solo": ["sustain_tank", "defense", "hybrid_bulk", "mitigate", "antiheal", "aura"],
    "shield_solo": ["shield_item", "defense", "hybrid_bulk", "mitigate", "antiheal", "cdr_def"],
    "bruiser_solo": ["hybrid_bulk", "defense", "power_bruiser", "mitigate", "antiheal", "cdr_def"],
    "mage_solo": ["hybrid_bulk", "defense", "mitigate", "flat_pen", "cdr_def", "antiheal"],
    # Support
    "peel_support": ["mitigate", "counter", "aura", "defense", "cdr_def", "tenacity"],
    "lockdown_support": ["cdr_def", "mitigate", "aura", "defense", "counter", "tenacity"],
    "shield_support": ["shield_item", "aura", "mitigate", "defense", "cdr_def", "counter"],
    "heal_support": ["heal_aura", "aura", "mitigate", "defense", "cdr_def", "counter"],
    "aura_support": ["aura", "mitigate", "defense", "cdr_def", "counter", "tenacity"],
}


def _item_matches_slot(
    it: ScoredItem,
    slot: str,
    *,
    mage: bool,
    physical: bool,
    role: str,
) -> bool:
    n = it.name.lower()
    blob = f"{it.passive} {it.active}".lower()
    str_v = _canon_stat_value(it.stats, "str")
    int_v = _canon_stat_value(it.stats, "int")
    pen = item_pen_value(it)
    as_v = _canon_stat_value(it.stats, "as")
    crit_v = _canon_stat_value(it.stats, "crit")
    ls_v = _canon_stat_value(it.stats, "ls")
    cdr = _canon_stat_value(it.stats, "cdr")
    hp = _canon_stat_value(it.stats, "hp")
    damp = _canon_stat_value(it.stats, "damp")
    plat = _canon_stat_value(it.stats, "plat")
    ten = _canon_stat_value(it.stats, "ten")
    pprot = _canon_stat_value(it.stats, "pprot")
    mprot = _canon_stat_value(it.stats, "mprot")
    mp = _canon_stat_value(it.stats, "mp")

    def power_ok() -> bool:
        if mage:
            return int_v >= 40 and str_v < 40
        if physical:
            return str_v >= 30 and int_v < 45
        return (str_v + int_v) >= 40

    if slot == "power":
        # pure power — not shield/defense hybrids that snuck in
        if it.item_type == "Defensive":
            return False
        if any(k in n for k in ("phoenix", "pridwen", "thebes", "spectral")):
            return False
        return power_ok() and it.item_type in ("Offensive", "Hybrid") and pen < 15
    if slot == "flat_pen":
        return pen >= 8 and pen < 18 and _pen_matches_kit(it, mage=mage, physical=physical)
    if slot == "pct_pen":
        return pen >= 15 and _pen_matches_kit(it, mage=mage, physical=physical) and not it.is_active_item
    if slot == "cdr":
        return cdr >= 10 and (power_ok() or it.item_type != "Defensive")
    if slot == "cdr_def":
        return cdr >= 10 and (it.item_type == "Defensive" or pprot + mprot >= 30)
    if slot == "defense":
        # Backline: prefer light defense with CDR/power, not pure aura tanks
        if role in ("Carry", "Mid", "Jungle"):
            if any(
                k in n
                for k in (
                    "shifter",
                    "spectral",
                    "thebes",
                    "midgardian",
                    "nemean",
                    "heartwood",
                    "stygian",
                    "radiant bulwark",
                )
            ):
                return False
            return (
                (it.item_type == "Defensive" or (hp >= 200 and pen < 15))
                and (cdr >= 8 or int_v >= 20 or str_v >= 20 or damp >= 5 or ten >= 5)
            )
        return it.item_type == "Defensive" or (hp >= 250 and (str_v + int_v) < 55)
    if slot == "luxury":
        if role in ("Solo", "Support"):
            return False
        return (it.total_cost or 0) >= 3000 and power_ok() and it.item_type == "Offensive"
    if slot == "sustain":
        return ls_v >= 8 or any(k in n for k in ("bancroft", "gluttonous", "blood", "lifebinder", "asclepius", "devourer", "sanguine"))
    if slot == "ls_core":
        return ls_v >= 8 or any(k in n for k in ("bloodforge", "devourer", "gluttonous", "bancroft"))
    if slot == "mana_stack":
        return (
            mp >= 250
            or any(k in n for k in ("thoth", "book of", "doom orb", "transcend"))
            or (mp >= 150 and "pendant" in n)
        )
    if slot == "dot_core":
        return any(k in n for k in ("desolat", "magus", "divine", "soul reaver", "gem of isolation", "contagion", "grimoire"))
    if slot == "zone_core":
        return any(k in n for k in ("magus", "isolation", "divine", "soul gem", "grimoire", "gem of focus"))
    if slot == "aa_core" or slot == "as_core":
        return as_v >= 15 or any(k in n for k in ("riptalon", "ichival", "demon", "wind demon", "golden blade", "avenging", "musashi", "eros", "qins"))
    if slot == "crit_core":
        return crit_v >= 15 or any(k in n for k in ("deathbringer", "demon blade", "rage", "wind"))
    if slot == "onhit":
        return as_v >= 10 and (pen >= 5 or "basic" in blob or any(k in n for k in ("riptalon", "executioner", "qins", "silverbranch")))
    if slot == "gap":
        return any(k in n for k in ("jotunn", "arondight", "hydra", "heartseeker", "transcend")) or (cdr >= 10 and power_ok())
    if slot == "hybrid_bulk":
        return it.item_type == "Hybrid" or (hp >= 200 and (str_v >= 20 or int_v >= 20) and (pprot + mprot) >= 15)
    if slot == "power_bruiser":
        return power_ok() and (hp >= 150 or pprot + mprot >= 20 or it.item_type == "Hybrid")
    if slot == "mitigate":
        return damp >= 5 or plat >= 5 or ten >= 5 or any(k in n for k in ("alchemist", "spectral", "nemean", "mantle", "magi"))
    if slot == "counter":
        return (
            ("critical" in blob or "attack speed" in blob)
            and any(k in blob for k in ("reduc", "enemy", "less", "plating"))
        ) or any(k in n for k in ("spectral", "nemean", "midgardian", "witchblade"))
    if slot == "aura":
        return any(k in blob for k in ("ally", "allies", "aura", "team")) or any(
            k in n for k in ("thebes", "sovereignty", "heartward", "chandra", "providence", "contagion")
        )
    if slot == "tenacity":
        return ten >= 5 or "magi" in n or "tenacit" in blob
    if slot == "antiheal":
        return any(k in n for k in ("divine", "brawler", "pestilence", "contagion", "toxic")) or (
            "heal" in blob and any(k in blob for k in ("reduc", "anti", "curse"))
        )
    if slot == "shield_item":
        return "shield" in blob or any(k in n for k in ("pridwen", "phoenix", "shifter", "spectral"))
    if slot == "heal_aura":
        return any(k in n for k in ("asclepius", "chandra", "thebes", "sovereignty")) or (
            "heal" in blob and any(k in blob for k in ("ally", "allies", "aura"))
        )
    if slot == "sustain_tank":
        return (ls_v >= 5 and hp >= 150) or any(k in n for k in ("sanguine", "gladiator", "ancile", "shifter"))
    return power_ok()


# Preferred item-name substrings by kit tag — large boosts inside matching slots.
# This is the main god-specific differentiator (not global #1 pen every time).
TAG_ITEM_SIGNATURES: dict[str, list[str]] = {
    "mana_stack": ["thoth", "doom orb", "book of", "transcend"],
    "heavy_dot": ["magus", "isolation", "desolat", "divine", "contagion"],
    "dot": ["magus", "desolat", "isolation", "divine", "contagion"],
    "channel": ["chronos", "gem of focus", "myrddin", "desolat"],
    "spam": ["chronos", "pendant", "gem of focus", "breastplate", "genji"],
    "ult_nuke": ["soul reaver", "tahuti", "obsidian", "titan", "desolat"],
    "burst": ["desolat", "obsi", "titan", "soul reaver", "tahuti", "heartseeker"],
    "pet_zone": ["isolation", "magus", "soul gem", "divine", "grimoire"],
    "zone": ["isolation", "magus", "soul gem", "divine"],
    "aa": ["riptalon", "demon", "deathbringer", "qins", "ichival", "wind", "avenging", "musashi"],
    "as_steroid": ["riptalon", "demon", "ichival", "avenging", "wind"],
    "heal": ["bancroft", "soul gem", "typhon", "asclepius", "lifebinder", "gluttonous"],
    "heavy_heal": ["asclepius", "bancroft", "typhon", "lifebinder"],
    "self_sustain": ["bancroft", "typhon", "gluttonous", "bloodforge", "devourer"],
    "execute": ["soul reaver", "bloodforge", "titan", "obsi", "desolat"],
    "prot_shred": ["magus", "executioner", "desolat", "void", "obsi", "titan"],
    "shield": ["pridwen", "phoenix", "shifter", "spectral"],
    "heavy_shield": ["pridwen", "phoenix", "spectral", "shifter"],
    "high_cc": ["isolation", "binding", "chronos", "breastplate", "genji"],
    "hard_cc": ["isolation", "binding", "stygian"],
    "immobile": ["alchemist", "magi", "cloak", "mantle", "spectral", "oni"],
    "mobile": ["jotunn", "hydra", "arondight", "heartseeker"],
    "gap_close": ["jotunn", "hydra", "arondight", "heartseeker", "transcend"],
    "team_buff": ["thebes", "sovereign", "heartward", "chandra", "providence"],
    "anti_cc": ["magi", "mantle", "alchemist", "prophetic"],
    "sustained": ["chronos", "pendant", "bloodforge", "devourer", "qins"],
}


def _god_slot_salt(diversify_key: str, slot: str, role: str, item_name: str = "") -> int:
    """Deterministic 0..N salt unique per god × slot × item."""
    raw = f"{diversify_key}|{slot}|{role}|{item_name}"
    return sum((i + 1) * ord(ch) for i, ch in enumerate(raw))


def _tag_signature_boost(nlow: str, tags: set[str], slot: str) -> float:
    """Large preference for items that match the god's kit tags."""
    boost = 0.0
    matched_tags = 0
    for tag in tags:
        prefs = TAG_ITEM_SIGNATURES.get(tag)
        if not prefs:
            continue
        for i, key in enumerate(prefs):
            if key in nlow:
                # earlier preference list entry = stronger
                boost += 48 - i * 4
                matched_tags += 1
                break
    # Identity slots get an extra kick when a signature hits
    if matched_tags and slot in (
        "flat_pen",
        "pct_pen",
        "power",
        "dot_core",
        "zone_core",
        "mana_stack",
        "sustain",
        "cdr",
        "aa_core",
        "as_core",
        "crit_core",
        "onhit",
        "gap",
        "luxury",
        "mitigate",
        "counter",
        "aura",
        "shield_item",
        "heal_aura",
    ):
        boost += 18 * min(matched_tags, 3)
    return boost


def _pick_slot_item(
    pool: list[ScoredItem],
    slot: str,
    seen: set[str],
    *,
    mage: bool,
    physical: bool,
    role: str,
    max_actives: int,
    active_count: int,
    diversify_key: str = "",
    tags: set[str] | None = None,
    luxury_actives: int = 0,
    max_luxury_actives: int = 1,
) -> ScoredItem | None:
    tags = tags or set()
    cands = [
        x
        for x in pool
        if x.name not in seen
        and _item_matches_slot(x, slot, mage=mage, physical=physical, role=role)
        and not (x.is_active_item and active_count >= max_actives)
    ]
    if not cands:
        return None

    # Hard cap luxury On-Use (Dreamer's / Wish / Parashu) — one per path max
    if slot == "luxury" or slot in ("power", "cdr", "sustain"):
        if luxury_actives >= max_luxury_actives:
            cands = [
                x
                for x in cands
                if not (x.is_active_item and (x.total_cost or 0) >= 3200)
            ]
            if not cands:
                return None

    def slot_rank(x: ScoredItem) -> float:
        sc = float(x.role_score)
        n = x.name.lower()
        # prefer true identity items inside a slot
        if slot == "mana_stack":
            if any(k in n for k in ("thoth", "book of", "doom orb", "transcend")):
                sc += 55
            elif "pendant" in n:
                sc += 18
        if slot == "pct_pen" and not x.is_active_item:
            sc += 20
        if slot == "flat_pen" and not x.is_active_item:
            sc += 12
            # Prefer real flat pen cores over Gluttonous/Dreamer-as-pen
            if any(k in n for k in ("desolat", "magus", "divine", "pendulum", "crusher", "jotunn", "cosmic")):
                sc += 22
            if any(k in n for k in ("dreamer", "wish-granting", "parashu")):
                sc -= 35
        if slot in ("mitigate", "counter", "aura") and x.item_type == "Defensive":
            sc += 12
        if slot == "dot_core" and any(k in n for k in ("desolat", "magus", "isolation", "divine")):
            sc += 28
        if slot == "zone_core" and any(k in n for k in ("isolation", "magus", "soul gem", "grimoire")):
            sc += 28
        if slot == "defense" and role in ("Carry", "Mid", "Jungle"):
            if any(k in n for k in ("genji", "breastplate", "valor", "alchemist", "magi", "cloak")):
                sc += 28
            if _canon_stat_value(x.stats, "cdr") >= 10:
                sc += 15
        if slot == "luxury":
            # Prefer passives for most gods; actives only when kit wants burst finisher
            if x.is_active_item and (x.total_cost or 0) >= 3200:
                if "burst" in tags or "ult_nuke" in tags or "execute" in tags:
                    sc += 8
                else:
                    sc -= 25
            elif any(k in n for k in ("tahuti", "soul reaver", "myrddin", "deathbringer", "bloodforge")):
                sc += 18
        # Kit-tag signature affinity (primary god differentiator)
        sc += _tag_signature_boost(n, tags, slot)
        # Per-god reordering of the entire candidate list (not only near-ties).
        # Magnitude is large enough to swap #1/#2/#3 among legitimate slot peers.
        if diversify_key:
            salt = _god_slot_salt(diversify_key, slot, role, x.name) % 53
            sc += salt * 1.15
        return sc

    cands.sort(key=slot_rank, reverse=True)

    # Always pick among top-K by god salt — every slot, including pen/power.
    # Full top-K (no score-floor collapse) so similar-tag gods still diverge.
    if diversify_key and len(cands) > 1:
        wide = {
            "flat_pen",
            "pct_pen",
            "power",
            "luxury",
            "defense",
            "mitigate",
            "counter",
            "aura",
            "hybrid_bulk",
            "sustain",
            "cdr",
            "cdr_def",
            "gap",
            "ls_core",
            "as_core",
            "crit_core",
            "antiheal",
            "shield_item",
            "heal_aura",
            "sustain_tank",
            "power_bruiser",
            "dot_core",
            "zone_core",
            "mana_stack",
            "tenacity",
            "onhit",
        }
        top_k = 7 if slot in wide else 5
        top_k = min(top_k, len(cands))
        # Soft quality gate: drop only true junk (>35% behind #1), keep ≥3 when possible
        best = slot_rank(cands[0])
        floor = best - max(80.0, abs(best) * 0.35)
        near = [c for c in cands[:top_k] if slot_rank(c) >= floor]
        if len(near) < min(3, top_k):
            near = cands[:top_k]
        idx = _god_slot_salt(diversify_key, slot, role) % len(near)
        return near[idx]
    return cands[0]


def _inject_signature_items(
    path: list[ScoredItem],
    pool: list[ScoredItem],
    tags: set[str],
    dkey: str,
    role: str,
    *,
    mage: bool,
    physical: bool,
    max_actives: int,
    seen: set[str],
    actives: int,
) -> tuple[list[ScoredItem], set[str], int]:
    """
    Force 1–2 kit-signature items into the path if tags demand them and
    they are not already present. Replaces lowest-score non-pen filler.
    """
    # Weight rarer/identity tags first so two zone mages with different secondary
    # tags (heal vs hard_cc) inject different cores.
    tag_priority = [
        "mana_stack",
        "heavy_dot",
        "channel",
        "aa",
        "as_steroid",
        "heavy_heal",
        "self_sustain",
        "heal",
        "execute",
        "ult_nuke",
        "prot_shred",
        "pet_zone",
        "zone",
        "spam",
        "heavy_shield",
        "shield",
        "team_buff",
        "immobile",
        "mobile",
        "gap_close",
        "hard_cc",
        "high_cc",
        "anti_cc",
        "dot",
        "burst",
        "sustained",
    ]
    ordered_tags = [t for t in tag_priority if t in tags] + sorted(
        t for t in tags if t not in tag_priority
    )
    # God-exclusive secondary: start from a god-rotated tag so shared tags don't
    # always inject the same first preference (Divine Ruin / Magus clones).
    if ordered_tags and dkey:
        rot = _god_slot_salt(dkey, "tagrot", role) % len(ordered_tags)
        ordered_tags = ordered_tags[rot:] + ordered_tags[:rot]

    prefs: list[str] = []
    for tag in ordered_tags:
        for key in TAG_ITEM_SIGNATURES.get(tag, []):
            if key not in prefs:
                prefs.append(key)
    if not prefs:
        return path, seen, actives

    # Second rotation on preference keys by god name
    if prefs and dkey:
        rot = _god_slot_salt(dkey, "signature", role) % len(prefs)
        prefs = prefs[rot:] + prefs[:rot]

    path = list(path)
    injected = 0
    max_inject = 2
    for key in prefs:
        if injected >= max_inject or len(path) >= 6 and injected >= 1:
            break
        # already have a matching item?
        if any(key in x.name.lower() for x in path):
            continue
        cands = [
            x
            for x in pool
            if x.name not in seen
            and key in x.name.lower()
            and not (x.is_active_item and actives >= max_actives)
        ]
        if mage:
            cands = [
                x
                for x in cands
                if _canon_stat_value(x.stats, "int") >= _canon_stat_value(x.stats, "str")
                or x.item_type == "Defensive"
                or _canon_stat_value(x.stats, "int") >= 25
            ]
        elif physical:
            cands = [
                x
                for x in cands
                if _canon_stat_value(x.stats, "str") >= _canon_stat_value(x.stats, "int")
                or x.item_type == "Defensive"
                or _canon_stat_value(x.stats, "str") >= 20
                or _canon_stat_value(x.stats, "as") > 0
            ]
        if not cands:
            continue
        cands.sort(
            key=lambda x: x.role_score
            + (_god_slot_salt(dkey, "sig", role, x.name) % 23),
            reverse=True,
        )
        pick = cands[0]
        # Prefer replacing luxury actives / low-score filler, never strip last pen
        drop_idx = None
        pen_idxs = [
            i
            for i, it in enumerate(path)
            if is_pen_item(it) and _pen_matches_kit(it, mage=mage, physical=physical)
        ]
        for i, it in enumerate(path):
            if it.is_active_item and (it.total_cost or 0) >= 3200:
                drop_idx = i
                break
        if drop_idx is None:
            ranked = sorted(
                range(len(path)),
                key=lambda i: path[i].role_score,
            )
            for i in ranked:
                if len(pen_idxs) <= 1 and i in pen_idxs:
                    continue
                drop_idx = i
                break
        if drop_idx is None:
            if len(path) < 6:
                path.append(pick)
                seen.add(pick.name)
                if pick.is_active_item:
                    actives += 1
                injected += 1
            continue
        seen.discard(path[drop_idx].name)
        if path[drop_idx].is_active_item:
            actives = max(0, actives - 1)
        path[drop_idx] = pick
        seen.add(pick.name)
        if pick.is_active_item:
            actives += 1
        injected += 1
    return path, seen, actives


def assemble_kit_path(
    pool: list[ScoredItem],
    bias: dict,
    role: str,
    *,
    mage: bool,
    physical: bool,
    max_actives: int,
) -> tuple[list[ScoredItem], str]:
    """Build a 6-item path from archetype slots + god-specific scores (not global top-6)."""
    arch = detect_archetype(bias, role, mage, physical)
    slots = list(ARCHETYPE_SLOTS.get(arch, ARCHETYPE_SLOTS["burst_mage"]))
    tags = set(bias.get("tags") or [])
    # Secondary flex: spammy kits swap last luxury for CDR if not already
    if "spam" in tags and "cdr" not in slots[:3]:
        slots = slots[:-1] + ["cdr"] if slots[-1] == "luxury" else slots
    if "ult_nuke" in tags and "pct_pen" not in slots[:2]:
        if "pct_pen" in slots:
            slots.remove("pct_pen")
            slots.insert(1, "pct_pen")
    # Dot/zone kits: ensure identity core slot early
    if ("heavy_dot" in tags or "dot" in tags) and "dot_core" not in slots and role in ("Mid", "Carry"):
        if slots[0] in ("power", "flat_pen", "cdr"):
            slots = ["dot_core"] + [s for s in slots if s != "dot_core"]
            slots = slots[:6]
    if ("pet_zone" in tags or "zone" in tags) and "zone_core" not in slots and role == "Mid":
        if "flat_pen" in slots:
            idx = slots.index("flat_pen")
            slots.insert(idx + 1, "zone_core")
            slots = slots[:6]

    path: list[ScoredItem] = []
    seen: set[str] = set()
    actives = 0
    luxury_actives = 0
    dkey = str(bias.get("god_name") or "")
    max_lux = 1  # hard: at most one Dreamer's/Wish/Parashu-class active

    for slot in slots:
        if len(path) >= 6:
            break
        pick = _pick_slot_item(
            pool,
            slot,
            seen,
            mage=mage,
            physical=physical,
            role=role,
            max_actives=max_actives,
            active_count=actives,
            diversify_key=dkey,
            tags=tags,
            luxury_actives=luxury_actives,
            max_luxury_actives=max_lux,
        )
        if not pick:
            continue
        path.append(pick)
        seen.add(pick.name)
        if pick.is_active_item:
            actives += 1
            if (pick.total_cost or 0) >= 3200:
                luxury_actives += 1

    # Force kit signatures so two zone mages don't share identical shells
    path, seen, actives = _inject_signature_items(
        path,
        pool,
        tags,
        dkey,
        role,
        mage=mage,
        physical=physical,
        max_actives=max_actives,
        seen=seen,
        actives=actives,
    )
    luxury_actives = sum(
        1 for x in path if x.is_active_item and (x.total_cost or 0) >= 3200
    )

    # Fill remaining — god-salted ranking, ban extra luxury actives
    if len(path) < 6:
        rest = [x for x in pool if x.name not in seen]
        rest.sort(
            key=lambda x: (
                x.role_score
                - (120 if x.is_active_item and actives >= max_actives else 0)
                - (
                    80
                    if x.is_active_item
                    and (x.total_cost or 0) >= 3200
                    and luxury_actives >= max_lux
                    else 0
                )
                + _tag_signature_boost(x.name.lower(), tags, "fill")
                + (_god_slot_salt(dkey, "fill", role, x.name) % 47) * 1.2
            ),
            reverse=True,
        )
        for x in rest:
            if len(path) >= 6:
                break
            if x.is_active_item and actives >= max_actives:
                continue
            if (
                x.is_active_item
                and (x.total_cost or 0) >= 3200
                and luxury_actives >= max_lux
            ):
                continue
            path.append(x)
            seen.add(x.name)
            if x.is_active_item:
                actives += 1
                if (x.total_cost or 0) >= 3200:
                    luxury_actives += 1

    def _is_luxury_toy(it: ScoredItem) -> bool:
        """Late glass cannons — Dreamer's, Wish-Granting, Parashu, Tahuti, etc."""
        n = it.name.lower()
        # Named finisher toys always count (Rod of Tahuti is 3000)
        if any(k in n for k in ("dreamer", "wish-granting", "parashu", "tahuti")):
            return True
        cost = it.total_cost or 0
        if it.is_active_item and cost >= 3400:
            return True
        # expensive pure power with no defenses
        if (
            cost >= 3400
            and it.item_type in ("Offensive", "Hybrid")
            and _canon_stat_value(it.stats, "hp") < 200
            and _canon_stat_value(it.stats, "pprot") + _canon_stat_value(it.stats, "mprot") < 20
        ):
            return True
        return False

    # Luxury scrub: at most one expensive glass toy (active OR Wish-class passive)
    lux_idxs = [i for i, x in enumerate(path) if _is_luxury_toy(x)]
    if len(lux_idxs) > max_lux:
        keep = max(
            lux_idxs,
            key=lambda i: _god_slot_salt(dkey, "luxkeep", role, path[i].name)
            + path[i].role_score * 0.01,
        )
        for i in lux_idxs:
            if i == keep:
                continue
            for alt in pool:
                if alt.name in {x.name for x in path}:
                    continue
                if _is_luxury_toy(alt):
                    continue
                if mage and _canon_stat_value(alt.stats, "int") < 30 and alt.item_type != "Defensive":
                    continue
                if physical and _canon_stat_value(alt.stats, "str") < 20 and alt.item_type != "Defensive":
                    if _canon_stat_value(alt.stats, "as") <= 0:
                        continue
                path[i] = alt
                break

    # Final god-flavor swap: guarantee one flex slot is unique to this god name
    # even when tags/archetype fully overlap with another god.
    path = _god_flavor_flex(
        path[:6],
        pool,
        dkey,
        role,
        tags,
        mage=mage,
        physical=physical,
        max_actives=max_actives,
    )
    # Re-scrub after flavor (flavor can reintroduce a second luxury)
    lux_idxs = [i for i, x in enumerate(path) if _is_luxury_toy(x)]
    if len(lux_idxs) > max_lux:
        keep = max(
            lux_idxs,
            key=lambda i: _god_slot_salt(dkey, "luxkeep2", role, path[i].name),
        )
        for i in lux_idxs:
            if i == keep:
                continue
            for alt in pool:
                if alt.name in {x.name for x in path} or _is_luxury_toy(alt):
                    continue
                if alt.is_active_item and sum(1 for x in path if x.is_active_item) >= max_actives:
                    continue
                path[i] = alt
                break
    return path[:6], arch


def _god_flavor_flex(
    path: list[ScoredItem],
    pool: list[ScoredItem],
    dkey: str,
    role: str,
    tags: set[str],
    *,
    mage: bool,
    physical: bool,
    max_actives: int,
) -> list[ScoredItem]:
    """Replace one non-critical slot with a god-salted alternate from a wide peer pool."""
    if not path or not dkey:
        return path
    path = list(path)
    seen = {x.name for x in path}
    # Never swap the sole matching pen item
    pen_idxs = [
        i
        for i, it in enumerate(path)
        if is_pen_item(it) and _pen_matches_kit(it, mage=mage, physical=physical)
    ]
    # Prefer swapping luxury / defense / power filler
    candidates_idx = list(range(len(path)))
    # Rotate which index we flavor by god
    start = _god_slot_salt(dkey, "flavor_idx", role) % len(candidates_idx)
    order = candidates_idx[start:] + candidates_idx[:start]
    target = None
    for i in order:
        if len(pen_idxs) <= 1 and i in pen_idxs:
            continue
        target = i
        break
    if target is None:
        return path

    actives = sum(1 for x in path if x.is_active_item)
    alts = [
        x
        for x in pool
        if x.name not in seen
        and not (x.is_active_item and actives >= max_actives and not path[target].is_active_item)
    ]
    # Kit/type filter
    filtered: list[ScoredItem] = []
    for x in alts:
        str_v = _canon_stat_value(x.stats, "str")
        int_v = _canon_stat_value(x.stats, "int")
        nlow = x.name.lower()
        if mage and int_v < 25 and x.item_type not in ("Defensive", "Hybrid") and str_v > int_v + 10:
            continue
        if physical and str_v < 15 and x.item_type not in ("Defensive", "Hybrid") and int_v > str_v + 20:
            continue
        # Damage roles: skip pure aura tanks as flavor
        if role in DAMAGE_ROLES_NEED_PEN and x.item_type == "Defensive" and item_pen_value(x) < 5:
            if _canon_stat_value(x.stats, "cdr") < 8 and int_v + str_v < 25:
                continue
        # Support: no glass DPS toys / pure pen cores as "flavor"
        if role == "Support":
            if any(k in nlow for k in ("dreamer", "wish-granting", "parashu", "deathbringer", "tahuti", "soul reaver")):
                continue
            if x.item_type == "Offensive" and _canon_stat_value(x.stats, "hp") < 150:
                continue
        # Solo: no pure ADC crit toys
        if role == "Solo" and any(k in nlow for k in ("deathbringer", "dreamer", "wish-granting", "parashu")):
            continue
        filtered.append(x)
    if not filtered:
        return path
    filtered.sort(
        key=lambda x: (
            x.role_score
            + _tag_signature_boost(x.name.lower(), tags, "flavor")
            + (_god_slot_salt(dkey, "flavor", role, x.name) % 61) * 1.4
        ),
        reverse=True,
    )
    # Take god-rotated pick among top 8 so names always split
    top = filtered[:8]
    pick = top[_god_slot_salt(dkey, "flavor_pick", role) % len(top)]
    # Only swap if it actually changes the set (always true if not in seen)
    if pick.name != path[target].name:
        path[target] = pick
    return path


def max_shop_actives_for_god(role: str, damage_type: str | None, bias: dict | None = None) -> int:
    """
    Practical active budget for the 6-item grid.

    Most builds: 2 (leave room for free Curio which also eats the active budget).
    Melee-leaning physical Solo/Jungle: up to hard cap 3.
    Magical gods never get the melee-3 exception.
    """
    dtype = (damage_type or "").lower()
    if dtype == "magical":
        return DEFAULT_MAX_SHOP_ACTIVES
    primary = (bias or {}).get("primary") or ""
    melee_role = role in ("Solo", "Jungle")
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
    damp = _canon_stat_value(it.stats, "damp")
    plat = _canon_stat_value(it.stats, "plat")
    ten = _canon_stat_value(it.stats, "ten")
    if damp >= 5 or plat >= 5 or ten >= 10:
        return "mitigate"
    blob = f"{it.passive} {it.active}".lower()
    # Counter = mitigate enemy offense — not items that *grant* crit/AS to you.
    if any(
        k in blob
        for k in (
            "damage from critical",
            "critical strikes are mitigated",
            "take -",
            "attack speed reduced",
            "their attack speed",
            "enemy has their attack speed",
            "plating",
            "dampening",
            "healing reduction",
        )
    ):
        return "counter"
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
            next(i for i in items if i["name"] == s.name), profile, role=role
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
        or _canon_stat_value(s.stats, "damp")
        or _canon_stat_value(s.stats, "plat")
        or _canon_stat_value(s.stats, "ten")
    ]
    hybrid = [s for s in t3 if s.item_type == "Hybrid" or "hybrid" in s.flags]
    mitigate = [
        s
        for s in t3
        if _slot_label(s) in ("mitigate", "counter", "defense")
        or _canon_stat_value(s.stats, "damp")
        or _canon_stat_value(s.stats, "plat")
        or _canon_stat_value(s.stats, "ten")
    ]

    slots = profile["build_slots"]
    # Pick extra candidates so we can always fill 6 non-starter slots
    core_n = max(slots["cores"], 4)
    def_n = max(slots["defense"], 2)
    flex_n = max(slots["flex"], 2)
    if role in ("Support", "Solo"):
        pool = mitigate or defense
        if role == "Solo":
            pool = list({x.name: x for x in (mitigate + defense + hybrid)}.values())
            pool.sort(key=lambda x: x.role_score, reverse=True)
        cores = pick_diverse(pool, core_n, "defense")
        defs = pick_diverse(
            [d for d in defense if d.name not in {c.name for c in cores}],
            def_n,
            "defense",
        )
        flex_pool = [x for x in pool if x.name not in {c.name for c in cores + defs}]
        flex = pick_diverse(flex_pool, flex_n, "defense")
    elif role == "Jungle":
        cores = pick_diverse(offense, core_n, "offense")
        defs = pick_diverse(defense, 1, "defense")
        flex_pool = [x for x in offense + hybrid if x.name not in {c.name for c in cores + defs}]
        flex_pool.sort(key=lambda x: x.role_score, reverse=True)
        flex = pick_diverse(flex_pool, flex_n, "offense")
    else:
        cores = pick_diverse(offense, core_n, "offense")
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

    # Role guide only — NOT a full 6-item build (gods get kit-fit paths).
    pri = sorted(profile["stat_weights"].items(), key=lambda x: -x[1])
    top_pri = [k for k, v in pri if v > 0][:5]
    common = pick_diverse(
        cores + defs + flex if (cores or defs) else t3,
        8,
        "defense" if role in ("Support", "Solo") else "offense",
    )

    return {
        "role": role,
        "is_role_guide": True,
        "description": profile["description"],
        "job": profile["description"],
        "stat_priorities": profile["stat_weights"],
        "priority_stats": top_pri,
        "build_notes": (
            f"This is the {role} job description + common items — not a complete build. "
            f"Open a god below for a kit-specific 1 starter + 6 buy order "
            f"(actives ≤{DEFAULT_MAX_SHOP_ACTIVES}, hard max {HARD_MAX_ACTIVE_ITEMS})."
        ),
        "max_shop_actives": DEFAULT_MAX_SHOP_ACTIVES,
        "hard_max_actives": HARD_MAX_ACTIVE_ITEMS,
        "typical_starter": _item_card(starters[0]) if starters else None,
        "starter": _item_card(starters[0]) if starters else None,  # legacy key
        "starter_alternatives": [_item_card(s) for s in starters[1:3]],
        "common_items": [_item_card(c) for c in common],
        # Do NOT expose a fake full buy path as "items" (was confusing vs god builds)
        "items": [],
        "full_path": [],
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
    primary = bias.get("primary") or ""
    mage = primary == "Intelligence" or (dtype or "").lower() == "magical"
    physical = (primary == "Strength" or (dtype or "").lower() == "physical") and not mage
    starter_pick = pick_god_starter(starters, items, profile, bias, role, dtype)
    # Keep full ranked list for alts (re-score lightly for display order)
    for s in starters:
        raw = next(i for i in items if i["name"] == s.name)
        s.role_score = score_starter(raw, profile, role=role)
    starters.sort(key=lambda x: x.role_score, reverse=True)
    if starter_pick:
        # Pin chosen starter first
        starters = [starter_pick] + [s for s in starters if s.name != starter_pick.name]

    t3 = [s for s in scored if is_t3_core(next(i for i in items if i["name"] == s.name))]

    def kit_ok(s: ScoredItem) -> bool:
        str_v = _canon_stat_value(s.stats, "str")
        int_v = _canon_stat_value(s.stats, "int")
        as_v = _canon_stat_value(s.stats, "as")
        crit_v = _canon_stat_value(s.stats, "crit")
        bap = _canon_stat_value(s.stats, "bap")
        ls_v = _canon_stat_value(s.stats, "ls")
        if role == "Support":
            if ls_v >= 5:
                return False
            # personal AS/crit toys are not support cores
            if (as_v >= 20 or crit_v >= 15 or bap >= 15) and _slot_label(s) == "power":
                return False
            return True
        if role == "Solo":
            nlow = s.name.lower()
            # frontline: skip pure glass AS/crit carries and luxury mage toys
            if (as_v >= 25 or crit_v >= 20) and _canon_stat_value(s.stats, "hp") < 200:
                return False
            if s.item_type == "Offensive" and _canon_stat_value(s.stats, "hp") < 150 and (
                _canon_stat_value(s.stats, "pprot") + _canon_stat_value(s.stats, "mprot") < 20
            ):
                return False
            if any(k in nlow for k in ("wish-granting", "dreamer", "parashu", "tahuti", "deathbringer")):
                return False
            if (s.total_cost or 0) >= 3400 and s.item_type == "Offensive":
                return False
            return True
        if role == "Jungle":
            # keep gank items; drop pure aura-support tanks without damage
            if s.item_type == "Defensive" and not is_pen_item(s) and (str_v + int_v) < 15:
                # still allow one via pool; don't hard-ban all
                pass
            return True
        if mage:
            nlow = s.name.lower()
            # Reject basic-attack / STR toys on pure mages
            if str_v >= 30 and int_v < 40:
                return False
            if (as_v >= 15 or crit_v >= 15 or bap >= 15) and int_v < 50:
                return False
            # Mid/Carry mages: no frontline shield cores as "power"
            if role in ("Mid", "Carry") and any(
                k in nlow for k in ("phoenix", "pridwen", "thebes", "spectral armor", "midgardian")
            ):
                return False
            return int_v >= 25 or s.item_type == "Defensive" or _canon_stat_value(s.stats, "hp") >= 250
        if physical:
            if int_v >= 40 and str_v < 25:
                return False
            return str_v >= 20 or as_v > 0 or s.item_type == "Defensive" or _canon_stat_value(s.stats, "hp") >= 250
        return True

    t3 = [s for s in t3 if kit_ok(s)]
    max_act = max_shop_actives_for_god(role, dtype, bias)

    # Slot-based path from kit archetype (primary differentiator across gods)
    items_6, archetype = assemble_kit_path(
        t3, bias, role, mage=mage, physical=physical, max_actives=max_act
    )
    items_6 = _ensure_pen_in_path(
        items_6, t3, role, max_act, mage=mage, physical=physical
    )
    if role in DAMAGE_ROLES_NEED_PEN:
        items_6 = _trim_excess_defense(items_6, t3, max_defense=1, max_actives=max_act)
    elif role in ("Solo", "Support"):
        # keep frontline bulk — no trim
        pass
    items_6 = _order_buy_path(items_6, role)
    # Avoid double luxury actives (Dreamer's + Wish-Granting) on damage roles
    luxury = [
        i
        for i, x in enumerate(items_6)
        if x.is_active_item and (x.total_cost or 0) >= 3400
    ]
    if len(luxury) > 1 and role in DAMAGE_ROLES_NEED_PEN:
        # keep highest scored luxury, replace others with passive power
        keep = max(luxury, key=lambda i: items_6[i].role_score)
        for i in luxury:
            if i == keep:
                continue
            for alt in t3:
                if (
                    alt.name not in {x.name for x in items_6}
                    and not alt.is_active_item
                    and (
                        _canon_stat_value(alt.stats, "int")
                        + _canon_stat_value(alt.stats, "str")
                        >= 40
                        or is_pen_item(alt)
                    )
                ):
                    items_6[i] = alt
                    break
        items_6 = _order_buy_path(items_6, role)
    pen_total = sum(item_pen_value(x) for x in items_6)
    n_act = sum(1 for x in items_6 if x.is_active_item)

    cores = [x for x in items_6 if x.item_type in ("Offensive", "Hybrid") or is_pen_item(x)][:4]
    defs = [x for x in items_6 if x.item_type == "Defensive"][:2]

    relics = [s for s in scored if is_base_relic(next(i for i in items if i["name"] == s.name))]
    for r in relics:
        r.role_score = score_relic(next(i for i in items if i["name"] == r.name), profile)
        if bias.get("mobility", 0) == 0 and "blink" in r.name.lower():
            r.role_score += 12
        if bias.get("cc", 0) >= 2 and "bead" in r.name.lower():
            r.role_score += 8
        if "immobile" in set(bias.get("tags") or []) and "aegis" in r.name.lower():
            r.role_score += 10
    relics.sort(key=lambda x: x.role_score, reverse=True)

    tags = sorted(bias.get("tags") or [])
    return {
        "god": god["entity_name"],
        "role": role,
        "tier": god.get("tier"),
        "rank": god.get("rank_in_scope"),
        "model_score": god.get("score"),
        "damage_type": god.get("primary_damage_type"),
        "pantheon": god.get("pantheon"),
        "scaling": bias.get("primary"),
        "archetype": archetype,
        "kit_tags": tags,
        "patch_trajectory": bias.get("trajectory"),
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
        "why": _explain_god_build(
            god, bias, role, items_6, starters, pen_total, n_act, max_act, archetype=archetype
        ),
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
    # Prefer showing identity stats first (pen / damp / plat / ten / prots)
    priority = ("pen", "damp", "plat", "ten", "pprot", "mprot", "hp", "int", "str", "cdr", "ls", "as")
    ordered = []
    seen = set()
    for k in priority:
        v = _canon_stat_value(it.stats, k)
        if v:
            ordered.append((k, v))
            seen.add(k)
    for k, v in sorted(it.stats.items(), key=lambda x: -abs(x[1])):
        if k not in seen and k not in {p for p, _ in ordered}:
            ordered.append((k, v))
        if len(ordered) >= 5:
            break
    pen = item_pen_value(it)
    return {
        "name": it.name,
        "score": round(it.role_score, 1),
        "cost": it.total_cost,
        "type": it.item_type or it.tier,
        "slot": _slot_label(it),
        "momentum": round(it.momentum, 2),
        "stats": {k: v for k, v in ordered[:5]},
        "pen": round(pen, 1) if pen else 0,
        "damp": round(_canon_stat_value(it.stats, "damp"), 1) or 0,
        "plat": round(_canon_stat_value(it.stats, "plat"), 1) or 0,
        "ten": round(_canon_stat_value(it.stats, "ten"), 1) or 0,
        "effect": (it.passive or it.active or "")[:180],
        "is_active": bool(it.is_active_item),
    }


def _explain_god_build(
    god, bias, role, path, starters, pen_total=0.0, n_act=0, max_act=2, archetype: str | None = None
) -> str:
    dtype = god.get("primary_damage_type") or god.get("damage_type") or ""
    power_style = (
        "INT / magical"
        if str(dtype).lower() == "magical"
        else "STR / physical"
        if str(dtype).lower() == "physical"
        else f"{bias.get('primary')}"
    )
    tags = sorted(bias.get("tags") or [])
    tag_show = ", ".join(tags[:8]) if tags else "generic"
    arch = archetype or detect_archetype(
        bias,
        role,
        mage=str(dtype).lower() == "magical" or bias.get("primary") == "Intelligence",
        physical=str(dtype).lower() == "physical" or bias.get("primary") == "Strength",
    )
    style = (
        f"burst {float(bias.get('style_burst') or 0):.0%}/"
        f"dps {float(bias.get('style_dps') or 0):.0%}"
    )
    traj = bias.get("trajectory") or "stable"
    psc = float(bias.get("patch_score") or 0)
    r5 = float(bias.get("recent_patch") or 0)
    axes = bias.get("patch_axes_r5") or bias.get("patch_axes") or {}
    top_axes = sorted(axes.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
    axis_txt = (
        ", ".join(f"{k} {v:+.1f}" for k, v in top_axes) if top_axes else "none"
    )

    parts = [
        f"{god['entity_name']} · {role} · archetype «{arch}» ({power_style}).",
        f"Kit tags: {tag_show}.",
        f"Style {style}; patch {traj} (net {psc:+.1f}, r5 {r5:+.1f}).",
        f"Patch axes (r5): {axis_txt}.",
        f"Scale STR {(bias.get('str') or 0)*100:.0f}% / INT {(bias.get('int') or 0)*100:.0f}%.",
    ]
    # Link first items to tags
    if path:
        parts.append("Path exploits: " + ", ".join(p.name for p in path[:3]) + "…")
    pens = [p.name for p in path if is_pen_item(p)]
    if pens:
        parts.append("Pen: " + ", ".join(pens) + ".")
    parts.append(f"Actives {n_act}/{max_act} · pen ≈ {pen_total:.0f}.")
    return " ".join(parts)


def generate_all(conn: sqlite3.Connection, gods_per_role: int = 10) -> dict[str, Any]:
    items = load_items(conn)
    report: dict[str, Any] = {
        "game": "SMITE 2",
        "mode": "Conquest",
        "method": (
            "God-first Conquest builds: each path is assembled from that god's ability kit "
            "(metrics + ability text tags + burst/dps style) and patch trajectory, "
            "using archetype slot recipes so gods in the same role diverge. "
            "Role cards explain the job only — they are NOT a full build. "
            "Carry/Mid backline + pen; Jungle ganks; Solo frontline bulk; Support peels. "
            f"Shop actives ≤{DEFAULT_MAX_SHOP_ACTIVES} default "
            f"(hard max {HARD_MAX_ACTIVE_ITEMS}). "
            f"Damage roles enforce ≥{MIN_BUILD_PEN:.0f} matching pen."
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
        lines.append("### Role job (not a full build)")
        lines.append("")
        lines.append(t.get("build_notes") or "")
        lines.append("")
        if t.get("typical_starter") or t.get("starter"):
            st = t.get("typical_starter") or t["starter"]
            lines.append(f"**Typical starter:** {st['name']}")
        if t.get("priority_stats"):
            lines.append("**Priority stats:** " + ", ".join(t["priority_stats"]))
        if t.get("common_items"):
            lines.append(
                "**Common role items (not ordered as a build):** "
                + ", ".join(c["name"] for c in t["common_items"][:8])
            )
        lines.append("")
        lines.append("### God-specific kit builds (use these)")
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
    parser.add_argument("--gods", type=int, default=12, help="Top gods per role")
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
        print(f"\n### {role.upper()} — job guide (not a full build)")
        st = t.get("typical_starter") or t.get("starter")
        print(f"  Typical starter: {st['name'] if st else '—'}")
        if t.get("priority_stats"):
            print(f"  Priorities: {', '.join(t['priority_stats'])}")
        commons = t.get("common_items") or t.get("top_scored_items") or []
        if commons:
            print("  Common items: " + ", ".join(c["name"] for c in commons[:6]))
        print("  Kit-fit gods:")
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
