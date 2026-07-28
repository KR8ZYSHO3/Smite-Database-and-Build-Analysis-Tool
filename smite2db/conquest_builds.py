"""
Statistically weighted Conquest builds per role.

Formal multi-phase algorithm: docs/BUILD_ALGORITHM.md
Orchestration API: smite2db.build_pipeline

Phases (priority: gates > role > order > kit > ladder > high-SR inspire > diversify):
  P0 Context → P1 Score universe → P2 Hard gates → P3 God rescore
  → P4 Archetype → P5 Assemble slots → P6 Structural repair
  → P7 Buy order (spike timing) → P8 Explain

Data: kit metrics, item ladder, patch axes, optional tracker.gg soft inspiration.
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
from .aspect_kit import aspect_item_score_delta, build_aspect_bias, list_god_aspects
from .kit_effects import (
    apply_kit_overrides,
    effect_labels,
    explain_item_pick,
    extract_kit_effects,
    family_score_boost,
    prefer_ban_adjust,
)
from .tracker_inspire import inspiration_boost, inspiration_buy_rank
# algorithm_card imported lazily in build_god_build to avoid circular import

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
# Ranked carry floor: enough shred that tanks don't hard-wall you.
MIN_BUILD_PEN = 20.0

# Critical slots — always take the best candidate (no diversify salt).
# Uniqueness comes from kit tags + last flex, not random mid cores.
RANKED_CORE_SLOTS = frozenset(
    {
        "flat_pen",
        "pct_pen",
        "as_core",
        "crit_core",
        "onhit",
        "gap",
        "mana_stack",
        "ls_core",
        "power",
        "dot_core",
        "zone_core",
        "hybrid_bulk",
        "power_bruiser",
        "aura",  # Support Thebes/Stampede — do not diversify into Spectral
        "heal_aura",
    }
)

# Pure heal-amp / team-heal actives — only real heal kits should buy these early.
# Chandra / Thebes / etc. stay available as normal support auras.
HEAL_CORE_KEYS = ("asclepius", "lifebinder")
# Primary SMITE 2 healers (user-confirmed).
TRUE_HEALER_NAMES = frozenset({"aphrodite", "guan yu", "yemoja"})

# Mage lifesteal power cores — NOT default mid items (need real self-sustain).
MAGE_LS_CORE_KEYS = ("bancroft", "typhon", "gluttonous")
# Starters that lead into mage LS / sustain stacking.
VAMP_STARTER_KEYS = ("vampiric", "shroud")

# Wiki / scrape may still list these, but they are not reliably in the live SMITE 2 shop.
# Hard-ban from all recommended Conquest paths (substring match on item name).
# Eye of Providence: ward T3 — players report missing from shop; do not recommend.
REMOVED_OR_UNAVAILABLE_ITEM_KEYS = (
    "eye of providence",
    "providence",  # only matches Eye of Providence (not Eye of Erebus / Storm)
)


def _is_heal_core_item(name: str) -> bool:
    n = (name or "").lower()
    return any(k in n for k in HEAL_CORE_KEYS)


def _is_mage_ls_core_item(name: str) -> bool:
    n = (name or "").lower()
    return any(k in n for k in MAGE_LS_CORE_KEYS)


def _is_vamp_starter_name(name: str) -> bool:
    n = (name or "").lower()
    return any(k in n for k in VAMP_STARTER_KEYS)


def _is_removed_or_unavailable_item(name: str) -> bool:
    """True if item should never appear on recommended paths."""
    n = (name or "").lower()
    # Providence only — do not ban Eye of Erebus / Eye of the Storm
    if "providence" in n:
        return True
    for key in REMOVED_OR_UNAVAILABLE_ITEM_KEYS:
        if key == "providence":
            continue
        if key in n:
            return True
    return False


def _is_true_healer(bias: dict | None) -> bool:
    """
    Hard gate for Asclepius / Lifebinder class items.
    Name allowlist only (Aphrodite / Guan Yu / Yemoja) — kit heal_count is noisy
    and was putting heal cores on non-heal supports like Athena/Artio.
    """
    if not bias:
        return False
    name = (bias.get("god_name") or "").lower().strip()
    return name in TRUE_HEALER_NAMES


def _wants_mage_lifesteal(bias: dict | None) -> bool:
    """
    Bancroft / Typhon / Gluttonous / Vampiric Shroud only when the kit actually
    self-heals or drains — not every mage with a noisy heal_count flag.
    """
    if not bias:
        return False
    tags = set(bias.get("tags") or [])
    # Real self-heal / drain language from kit (not team heal, not ally buffs)
    if "self_sustain" in tags:
        return True
    # Dedicated heal gods sometimes sit in the LS line
    if _is_true_healer(bias):
        return True
    return False


# ---------------------------------------------------------------------------
# Melee vs ranged — Carry only works for ranged basics (or aspect that enables it)
# ---------------------------------------------------------------------------

_RANGED_TAG_MARKERS = (
    "character.type.ranged",
    "keyword.descriptor.ranged",
    "descriptor.ranged",
)
_MELEE_TAG_MARKERS = (
    "character.type.melee",
    "keyword.descriptor.melee",
    "descriptor.melee",
)
_ASPECT_RANGED_BASICS_RE = re.compile(
    r"basics? are ranged|basic attacks? are ranged|attacks are ranged|"
    r"attacks are ranged|geb'?s attacks are ranged|"
    r"basics? become ranged|become(?:s)? ranged|"
    r"ranged attack|mangetsu ranged|fire a projectile|throw a piercing projectile",
    re.I,
)
_ASPECT_MELEE_BASICS_RE = re.compile(
    r"basic attacks? are now melee|attacks are now melee|are now melee|"
    r"basics? are now melee|your basic attacks are now melee",
    re.I,
)


def _parse_character_tags(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw]
    if isinstance(raw, str):
        s = raw.strip()
        if not s:
            return []
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except json.JSONDecodeError:
            pass
        return [s]
    return []


def detect_base_attack_range(
    character_tags: Any = None,
    basic_attack_text: str = "",
) -> str:
    """
    Return 'ranged', 'melee', or 'unknown' from wiki character tags / basic text.
    Prefer tags (Character.Type.Ranged / Melee); fall back to basic attack prose.
    """
    tags_l = " ".join(_parse_character_tags(character_tags)).lower()
    has_r = any(m in tags_l for m in _RANGED_TAG_MARKERS)
    has_m = any(m in tags_l for m in _MELEE_TAG_MARKERS)
    if has_r and not has_m:
        return "ranged"
    if has_m and not has_r:
        return "melee"
    if has_r and has_m:
        # Prefer the Character.Type.* form if both appear
        if "character.type.ranged" in tags_l:
            return "ranged"
        if "character.type.melee" in tags_l:
            return "melee"

    blob = (basic_attack_text or "").lower()
    if "projectile" in blob or "ranged" in blob or "fire a" in blob:
        return "ranged"
    if "in front of you" in blob or "melee" in blob:
        return "melee"
    return "unknown"


def load_god_attack_range(conn: sqlite3.Connection, god_id: int) -> str:
    """Look up melee/ranged from DB character_tags + Basic Attack description."""
    row = conn.execute(
        "SELECT character_tags, type_label FROM gods WHERE id=?",
        (god_id,),
    ).fetchone()
    tags = row["character_tags"] if row else None
    basic = conn.execute(
        """
        SELECT description, stats_text, notes_text
        FROM abilities
        WHERE god_id = ? AND LOWER(COALESCE(slot,'')) LIKE '%basic%'
        ORDER BY slot_order LIMIT 1
        """,
        (god_id,),
    ).fetchone()
    basic_blob = ""
    if basic:
        basic_blob = " ".join(
            str(basic[k] or "") for k in ("description", "stats_text", "notes_text")
        )
    return detect_base_attack_range(tags, basic_blob)


def aspect_enables_ranged_basics(blob: str) -> bool:
    """True when aspect text turns basics into ranged (Kali Unbound, Geb Calamity, …)."""
    return bool(blob and _ASPECT_RANGED_BASICS_RE.search(blob))


def aspect_forces_melee_basics(blob: str) -> bool:
    """True when aspect text forces melee basics (e.g. Cernunnos Strife)."""
    return bool(blob and _ASPECT_MELEE_BASICS_RE.search(blob))


def carry_role_allowed(
    *,
    base_range: str,
    is_aspect: bool = False,
    aspect_blob: str = "",
    native_roles: list[str] | None = None,
) -> tuple[bool, str]:
    """
    Duo Carry needs ranged basic attacks.
    Melee gods only get Carry when an aspect changes basics to ranged (or ADC kit).
    """
    native = {str(r) for r in (native_roles or [])}
    if is_aspect:
        if aspect_forces_melee_basics(aspect_blob):
            return False, "aspect_melee_basics"
        if aspect_enables_ranged_basics(aspect_blob):
            return True, "aspect_ranged_basics"
        if base_range == "ranged":
            return True, "ranged_base"
        if base_range == "melee":
            return False, "melee_no_aspect_ranged"
        # unknown base: still allow if native Carry (hunters mis-tagged)
        if "Carry" in native:
            return True, "native_carry"
        return False, "unknown_melee_safe"
    # Base kit
    if base_range == "ranged":
        return True, "ranged"
    if "Carry" in native and base_range != "melee":
        return True, "native_carry"
    if base_range == "melee":
        return False, "melee_base"
    # Unknown: only native Carry
    if "Carry" in native:
        return True, "native_carry"
    return False, "unknown_not_native"


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
            # Vamp is a mage starter — never default on physical Carry
            "shroud": -40,
            "vampiric": -40,
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
            # Vamp only when kit self-sustains — default is Conduit/Sands
            "vampiric": -35,
            "shroud": -35,
            "bluestone": 22,
            "death": 12,
            "warrior": 8,
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
            "Conquest jungle — ganks first: Bumba clear, Jotunn/Hydra (or stack) openers, "
            "then power + pen. Not a Solo shell — Shifter/BoV mid is wrong for most junglers."
        ),
        "prefer_damage": None,
        "stat_weights": {
            "str": 0.16,
            "int": 0.13,
            "pen": 0.24,   # shred tanks so ganks stick
            "cdr": 0.18,   # ability uptime for multi-gank
            "hp": 0.08,
            "as": 0.08,
            "ls": 0.06,
            "crit": 0.03,
            "pprot": 0.02,
            "mprot": 0.02,
        },
        "tag_bonus": {"offensive": 16, "passive": 6, "active": 4, "ms": 8, "cc": 5},
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
        # No dedicated defense slot — damage path; optional late shell only via flex
        "build_slots": {"starter": 1, "cores": 5, "defense": 0, "flex": 1},
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
            # Warrior's Axe = default Solo shell (works into CC / poke)
            "warrior": 42,
            "axe": 40,
            "bluestone": 34,
            "sundering": 30,
            # Death's Toll is strong AA/sustain — but hard-countered by CC (can't auto)
            "death": 28,
            "leather": 22,
            "gilded": 14,
            "shroud": 12,
            "vampiric": 10,
            "selfless": -15,  # support starter — not solo identity
            "flag": -20,
            "bumba": -25,
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
    # Item tier ladder (scope items:overall) — meta strength from analysis
    ladder_tier: str | None = None
    ladder_rank: int | None = None
    ladder_score: float = 0.0


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
    # Item tier ladder (items:overall) — composite score from analysis
    ladder: dict[str, dict[str, Any]] = {}
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
    try:
        for r in conn.execute(
            """
            SELECT entity_name, tier, rank_in_scope, score
            FROM tier_list
            WHERE scope = 'items:overall' AND entity_type = 'item'
            """
        ):
            ladder[r["entity_name"]] = {
                "ladder_tier": r["tier"],
                "ladder_rank": int(r["rank_in_scope"] or 0),
                "ladder_score": float(r["score"] or 0.0),
            }
    except sqlite3.OperationalError:
        pass
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
        lad = ladder.get(r["name"]) or {}
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
                "ladder_tier": lad.get("ladder_tier"),
                "ladder_rank": lad.get("ladder_rank"),
                "ladder_score": lad.get("ladder_score", 0.0),
                "passive": r["passive"] or "",
                "active": active,
                "categories": cats,
                "is_active_item": is_active,
            }
        )
    return items


def _item_ladder_boost(
    *,
    ladder_tier: str | None,
    ladder_score: float,
    ladder_rank: int | None,
    role: str,
    item_type: str,
    is_pen: bool = False,
) -> float:
    """
    Map items:overall tier ladder into a role-score delta.
    Strong enough that S/A items beat B/C peers of similar stats, but not so strong
    that kit identity (pen, damage type) is ignored. Tank S-tiers are muted on
    damage backline roles unless the item is real pen.
    """
    if not ladder_tier and not ladder_score:
        return 0.0
    letter = (ladder_tier or "").upper().strip()
    letter_w = {"S": 28.0, "A": 18.0, "B": 5.0, "C": -8.0, "D": -16.0}.get(letter, 0.0)
    # Continuous score 0..100 (top items ~60–100)
    score_w = 0.0
    if ladder_score > 0:
        score_w = (float(ladder_score) / 100.0) * 22.0  # 0..22
    # Rank: #1 gets a bit more love
    rank_w = 0.0
    if ladder_rank and ladder_rank > 0:
        if ladder_rank <= 10:
            rank_w = 8.0 - (ladder_rank - 1) * 0.5
        elif ladder_rank <= 25:
            rank_w = 3.0
    raw = letter_w + score_w + rank_w

    # Role-gate: don't let pure defensive ladder S-tier invade Mid/Carry/Jungle
    itype = (item_type or "").lower()
    damage_backline = role in DAMAGE_ROLES_NEED_PEN
    frontline = role in ("Solo", "Support")
    if damage_backline and itype == "defensive" and not is_pen:
        raw *= 0.2  # soft awareness only
    elif damage_backline and itype == "hybrid" and not is_pen:
        raw *= 0.5
    elif frontline and itype in ("defensive", "hybrid"):
        raw *= 1.2  # tanks should prefer hot defensive ladder items
    elif damage_backline and itype == "offensive":
        raw *= 1.25  # ranked: lean into hot damage ladder items

    # Soft cap so ladder never alone overrides kit bans / signatures
    return max(-20.0, min(40.0, raw))


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
        nlow_sup = (item.get("name") or "").lower()
        # Ally-heal actives look like auras in text but are not peel cores
        if _is_heal_core_item(nlow_sup):
            util -= 8  # base role score: real healers re-score these up later
        elif any(k in blob for k in ("ally", "allies", "aura", "team")):
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

    # Item tier ladder (items:overall) — prefer S/A meta items in role score
    ladder_part = _item_ladder_boost(
        ladder_tier=item.get("ladder_tier"),
        ladder_score=float(item.get("ladder_score") or 0),
        ladder_rank=item.get("ladder_rank"),
        role=role,
        item_type=item.get("item_type") or "",
        is_pen=_canon_stat_value(item.get("stats") or {}, "pen") >= 8
        or "penetrat" in (item.get("passive") or "").lower()
        or "penetrat" in (item.get("categories") or "").lower(),
    )
    breakdown["ladder"] = round(ladder_part, 2)

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

    total = stat_score + tag_score + util + mom + cost_part + align + active_tax + ladder_part
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
        ladder_tier=item.get("ladder_tier"),
        ladder_rank=int(item["ladder_rank"]) if item.get("ladder_rank") is not None else None,
        ladder_score=float(item.get("ladder_score") or 0),
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
            if any(k in n for k in ("conduit", "death", "gilded", "bumba", "vampiric", "sands", "shroud")):
                sc -= 50
            if "selfless" in n or "flag" in n:
                sc += 25
        if role == "Jungle":
            if "bumba" in n:
                sc += 45
            else:
                sc -= 30
            # Never open jungle on Vamp / Conduit / Gilded
            if _is_vamp_starter_name(n) or any(k in n for k in ("conduit", "gilded", "selfless")):
                sc -= 80
        if role == "Solo":
            if any(k in n for k in ("warrior", "axe", "bluestone")):
                sc += 35
            if "selfless" in n:
                sc -= 40
            if "bumba" in n:
                sc -= 35
            if _is_vamp_starter_name(n):
                sc -= 90  # Solo is Axe / Bluestone / Death's — not mage vamp
            # AA / self-sustain bruisers: Death's Toll is a *conditional* maniac path.
            # High CC shuts it down (can't auto → no LS). Default stays Warrior's Axe;
            # salt + strong AA can flip to Death's when the lobby looks free-hit.
            if physical and (
                "self_sustain" in tags
                or "aa" in tags
                or float(bias.get("aa_score") or 0) >= 0.5
            ):
                aa_w = float(bias.get("aa_score") or 0)
                # Only pure AA identity strongly prefers Death's; mixed kits stay Axe
                if "death" in n:
                    if aa_w >= 0.65 or ("aa" in tags and "self_sustain" in tags):
                        sc += 28  # competitive with Axe, not auto-win
                    else:
                        sc += 8
                elif any(k in n for k in ("leather", "gilded")):
                    sc += 12
                # Warrior's Axe remains the safe default into unknown / CC lobbies
                if "warrior" in n or "axe" in n:
                    sc += 6

        # --- Vampiric Shroud: mage-only self-sustain niche ---
        # Physical gods never open Vamp (wrong damage type + wrong role job).
        if _is_vamp_starter_name(n):
            if physical:
                sc -= 120
            elif not mage:
                sc -= 80
            elif not _wants_mage_lifesteal(bias):
                sc -= 90  # Conduit/Sands default for almost every mid mage
            else:
                sc += 55  # real drain/self-heal kit only

        # Damage-type fit
        if mage:
            if any(k in n for k in ("conduit", "sands", "archmage", "pendulum")):
                sc += 30
            if any(k in n for k in ("gilded", "leather", "death")) and role != "Carry":
                sc -= 20
        if physical and role == "Mid":
            # Flex physical mid: Bluestone / Death's / Warrior — not Conduit, not Vamp
            if any(k in n for k in ("bluestone", "death", "warrior", "axe")):
                sc += 40
            if any(k in n for k in ("conduit", "sands", "archmage", "pendulum")):
                sc -= 45
            if any(k in n for k in ("gilded", "leather", "cowl", "arrow")):
                sc += 10  # AA hunters flexed mid
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
    if is_god_specific_item(it):
        return False
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


def is_god_specific_item(it: dict | ScoredItem | str) -> bool:
    """Ratatoskr acorns, Vulcan mods, Baron's Brew, etc. — not buyable by other gods."""
    if isinstance(it, str):
        n = it.lower()
        # Name cues when we only have a string (client / inject keys)
        if "acorn" in n:
            return True
        if n.endswith(" mod") or " mod" in n:
            return True
        if "baron's brew" in n or "genie's lamp" in n or "training grounds" in n:
            return True
        return False
    if isinstance(it, ScoredItem):
        n = (it.name or "").lower()
        itype = (it.item_type or "").lower()
        # ScoredItem may not carry categories; name + type
        if "god specific" in itype or itype == "god specific":
            return True
        if "acorn" in n:
            return True
        if n.endswith(" mod") or " mod" in n:
            return True
        if "baron's brew" in n or "genie's lamp" in n or "training grounds" in n:
            return True
        return False
    n = (it.get("name") or "").lower()
    cats_raw = it.get("categories") or ""
    if isinstance(cats_raw, (list, tuple)):
        cats = " ".join(str(c) for c in cats_raw).lower()
    else:
        cats = str(cats_raw).lower()
    itype = (it.get("item_type") or "").lower()
    tier = str(it.get("tier") or "")
    if (
        "god specific" in cats
        or "god-specific" in cats
        or "god specific" in itype
        or tier == "God Specific"
    ):
        return True
    if "acorn" in n:  # Ratatoskr-only family
        return True
    if n.endswith(" mod") or " mod" in n:
        return True
    if "baron's brew" in n or "genie's lamp" in n or "training grounds" in n:
        return True
    return False


def item_allowed_for_god(it: dict | ScoredItem | str, god_name: str | None) -> bool:
    """
    Shared-shop gate for builds / troll / random.
    God-specific items are banned unless this god owns them.
    Acorns → Ratatoskr only.
    """
    if not is_god_specific_item(it):
        return True
    if isinstance(it, str):
        n = it.lower()
    elif isinstance(it, ScoredItem):
        n = (it.name or "").lower()
    else:
        n = (it.get("name") or "").lower()
    g = (god_name or "").lower()
    if "acorn" in n and "ratatoskr" in g:
        return True
    return False


def is_t3_core(it: dict) -> bool:
    """True for normal shop T3 cores — never god-specific / relics / starters."""
    if is_god_specific_item(it):
        return False
    if it["tier"] == "3":
        return True
    if it["item_type"] in ("Offensive", "Defensive", "Hybrid") and (it["total_cost"] or 0) >= 2200:
        return True
    return False


def is_build_pool_item(it: dict | ScoredItem | str, god_name: str | None) -> bool:
    """
    Items legal in a Conquest path for this god:
      - normal shared T3 cores, or
      - god-specific lines this god owns (Ratatoskr acorns only today).
    """
    if isinstance(it, ScoredItem):
        name = it.name
        # Reconstruct minimal dict-like checks via helpers
        if _is_removed_or_unavailable_item(name):
            return False
        if item_allowed_for_god(name, god_name) and is_god_specific_item(name):
            return True
        # Shared T3 via name alone is ambiguous — callers usually pass raw dict
        return False
    if isinstance(it, str):
        if _is_removed_or_unavailable_item(it):
            return False
        return is_god_specific_item(it) and item_allowed_for_god(it, god_name)
    if _is_removed_or_unavailable_item(it.get("name") or ""):
        return False
    if is_t3_core(it):
        return True
    if is_god_specific_item(it) and item_allowed_for_god(it, god_name):
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

    base_bias = {
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
    # Structured effects + optional human overrides
    base_bias = apply_kit_overrides(base_bias, god_name)
    effects = extract_kit_effects(base_bias)
    base_bias["effects"] = effects
    base_bias["effect_labels"] = effect_labels(effects)
    return base_bias


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

    # Soft high-SR inspiration (tracker.gg) — never hard-override kit bans
    t_boost, _t_why = inspiration_boost(
        item.name,
        god_name=str(bias.get("god_name") or ""),
        role=role,
    )
    if t_boost:
        s += t_boost

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

    # --- Hard cross-type bans (fixes Bancroft-on-physical / Titan-on-mage) ---
    mage_only_names = (
        "bancroft",
        "typhon",
        "soul gem",
        "soul reaver",
        "gluttonous",
        "tahuti",
        "chronos' pendant",
        "chronos pendant",
        "book of thoth",
        "doom orb",
        "obsidian shard",
        "spear of the magus",
        "spear of desolation",
        "rod of asclepius",
        "divine ruin",
        "gem of focus",
        "the world stone",
        "cosmic horror",
        "jade scepter",
    )
    phys_only_names = (
        "titan's bane",
        "titan’s bane",
        "bloodforge",
        "deathbringer",
        "demon blade",
        "riptalon",
        "musashi",
        "avenging blade",
        "executioner",
        "qin's",
        "qins",
        "jotunn",
        "hydra's",
        "heartseeker",
        "tekko",
        "death metal",
        "runeforged",
    )
    if physical:
        if any(k in nlow for k in mage_only_names):
            s -= 140
        if int_v >= 35 and str_v < 28:
            s -= 100
    if mage:
        if any(k in nlow for k in phys_only_names):
            s -= 140
        if str_v >= 35 and int_v < 28:
            s -= 100

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
        # Support should not core pure DPS / mid-mage toys
        if any(
            k in nlow
            for k in (
                "divine ruin",
                "brawler",
                "titan",
                "obsi",
                "deathbringer",
                "soul reaver",
                "tahuti",
                "desolat",
                "chronos",
                "gem of focus",
                "spear of desolation",
                "spear of the magus",
                "dreamer",
                "wish-granting",
            )
        ):
            s -= 55
        # Greedy pure power without bulk
        if int_v >= 50 and _canon_stat_value(item.stats, "hp") < 200 and (
            _canon_stat_value(item.stats, "pprot") + _canon_stat_value(item.stats, "mprot") < 25
        ):
            s -= 45
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
        # Offline hybrid damage for solos (not full ADC)
        if physical and pen_v >= 8 and _canon_stat_value(item.stats, "hp") >= 150:
            s += 12
    elif role == "Jungle":
        s += pen_v * 1.5 + cdr_v * 0.7
        if any(k in blob for k in ("jungle", "monster", "minion")):
            s += 22
        # Standard ability jungle: Jotunn / Hydra / stack first, then pen+power
        if "jotunn" in nlow:
            s += 52
        elif "hydra" in nlow:
            s += 48
        elif any(k in nlow for k in ("transcend", "heartseeker", "arondight", "crusher", "reaper", "pendulum")):
            s += 36
        elif any(k in nlow for k in ("devourer", "bloodforge", "titan")):
            s += 30
        # Mid-shell is Solo identity — kills gank tempo (esp. post-Shifter nerf)
        if any(
            k in nlow
            for k in (
                "shifter",
                "breastplate",
                "genji",
                "spectral",
                "midgardian",
                "prophetic",
                "thebes",
                "chandra",
                "oni hunter",
                "leviathan",
                "gladiator",
            )
        ):
            s -= 55
        if item.item_type == "Defensive" and pen_v < 8 and (str_v + int_v) < 35:
            s -= 40
        # Spectral / aura peel is Support identity — not jungle core
        if any(k in nlow for k in ("spectral", "midgardian", "thebes", "chandra", "contagion")):
            s -= 50
        # Crit ADC toys rarely belong on ability junglers
        if any(k in nlow for k in ("deathbringer", "musashi", "avenging", "wind demon")):
            s -= 35
        if physical:
            s += str_v * 0.4 + pen_v * 0.45
    elif role == "Carry":
        # AA carries: AS/crit/LS first-class; ability hunters stay secondary
        aaish = "aa" in tags or float(bias.get("aa_score") or 0) >= 0.5 or "as_steroid" in tags
        if aaish and physical:
            s += as_v * 0.9 + crit_v * 1.0 + ls_v * 0.45
            if any(k in nlow for k in ("jotunn", "hydra")):
                s -= 35  # gap/ability items, not ADC cores
            if any(
                k in nlow
                for k in (
                    "riptalon",
                    "deathbringer",
                    "demon",
                    "musashi",
                    "avenging",
                    "qins",
                    "ichival",
                    "wind",
                    "eros",
                    "death metal",
                )
            ):
                s += 28

    # --- Kit tag affinities (LARGE — this is what diversifies gods) ---
    if "mana_stack" in tags:
        if mp_v >= 200 or "mana" in blob or any(
            k in nlow for k in ("thoth", "book", "doom orb", "pendant", "transcend")
        ):
            s += 55
        if "intelligence" in blob and "mana" in blob:
            s += 20
    if "dot" in tags or "heavy_dot" in tags:
        if mage and any(
            k in nlow
            for k in ("desolat", "magus", "divine", "soul reaver", "contagion", "gem of isolation")
        ):
            s += 42
        if physical and any(k in nlow for k in ("crusher", "serpentine", "toxic", "brawler")):
            s += 28
        if "heavy_dot" in tags:
            s += pen_v * 0.8 + 12
        if "over time" in blob or "burn" in blob or "poison" in blob:
            s += 18
    if "aa" in tags or float(bias.get("aa_score") or 0) >= 0.55:
        s += as_v * 1.35 + crit_v * 1.25 + _canon_stat_value(item.stats, "bap") * 0.75
        if any(
            k in nlow
            for k in ("riptalon", "deathbringer", "demon", "qins", "ichival", "wind", "musashi", "avenging", "eros")
        ):
            s += 42
        if mage and (as_v >= 15 or crit_v >= 15):
            s += 20  # AA mages are rare — reward AS hybrids
        if physical and any(k in nlow for k in ("jotunn", "bancroft", "soul gem")):
            s -= 40
    if "burst" in tags or float(bias.get("style_burst") or 0) >= 0.55:
        s += pen_v * 0.9
        if (item.total_cost or 0) >= 2800 and (int_v >= 60 or str_v >= 45):
            s += 28
        if mage and any(k in nlow for k in ("obsi", "soul reaver", "tahuti", "parashu", "dreamer", "rod of")):
            s += 22
        if physical and any(k in nlow for k in ("titan", "heartseeker", "parashu", "bloodforge")):
            s += 22
    if "sustained" in tags or float(bias.get("style_dps") or 0) >= 0.55:
        s += cdr_v * 1.4
        if mage and any(k in nlow for k in ("chronos", "pendant", "focus")):
            s += 30
        if physical and any(k in nlow for k in ("breastplate", "genji", "valor", "bloodforge", "devourer")):
            s += 22
        if ls_v >= 10:
            s += 18
    if "spam" in tags or float(bias.get("avg_cd") or 12) <= 8.5:
        s += cdr_v * 1.8 + 18
    if "channel" in tags:
        s += pen_v * 1.1 + 15
        if mage and any(k in nlow for k in ("obsi", "desolat", "magus", "chronos")):
            s += 25
        if physical and any(k in nlow for k in ("titan", "jotunn", "hydra")):
            s += 20
        # channel gods need bulk mid-fight
        if _canon_stat_value(item.stats, "hp") >= 250 or item.item_type == "Defensive":
            s += 16
    wants_ls = _wants_mage_lifesteal(bias)
    true_healer = _is_true_healer(bias)
    if "heal" in tags or "heavy_heal" in tags or "self_sustain" in tags:
        # Damage-type-correct sustain only — Bancroft line needs real self_sustain
        if mage and wants_ls and (
            ls_v >= 8
            or any(k in nlow for k in ("bancroft", "typhon", "gluttonous", "soul gem"))
        ):
            s += 40
        elif mage and not wants_ls and any(k in nlow for k in ("soul gem",)):
            # Soul Gem is late luxury sustain — not a mid opener for ranked
            if role == "Mid":
                s -= 25
            else:
                s += 6
        if mage and true_healer and any(k in nlow for k in ("asclepius", "lifebinder")):
            if role in ("Support", "Solo"):
                s += 40
            elif role == "Mid":
                s -= 30  # mid is damage; heal items belong on Support
        if physical and (
            ls_v >= 8 or any(k in nlow for k in ("bloodforge", "devourer", "sanguine", "gladiator"))
        ):
            s += 40
        if true_healer and "heavy_heal" in tags and ("heal" in blob or "lifesteal" in blob):
            s += 18
        # Don't let heal tags pull mage LS onto physical (or reverse)
        if physical and any(k in nlow for k in ("bancroft", "typhon", "gluttonous", "soul gem")):
            s -= 90
        if mage and any(k in nlow for k in ("bloodforge", "devourer")) and int_v < 20:
            s -= 90
        # Hard: Asclepius/Lifebinder are dead weight on non-heal kits
        if _is_heal_core_item(item.name) and not true_healer:
            s -= 200
        elif _is_heal_core_item(item.name) and true_healer:
            s += 55  # real healers actually want these early
    # Hard: Bancroft / Typhon / Gluttonous only on self-sustain mages
    if _is_mage_ls_core_item(item.name):
        if wants_ls and mage:
            s += 50
        else:
            s -= 200
    if "execute" in tags:
        s += pen_v * 1.2
        if physical and any(k in nlow for k in ("titan", "deathbringer", "bloodforge")):
            s += 32
        if mage and any(k in nlow for k in ("obsi", "soul reaver", "desolat")):
            s += 32
    if "prot_shred" in tags:
        if pen_v >= 8 or "penetrat" in blob or "protection" in blob:
            s += 28
        if mage and any(k in nlow for k in ("magus", "desolat", "void stone", "obsi")):
            s += 20
        if physical and any(k in nlow for k in ("executioner", "void shield", "titan", "crusher")):
            s += 20
    if "shield" in tags or "heavy_shield" in tags:
        if role in ("Solo", "Support") and (
            item.item_type in ("Defensive", "Hybrid") or "shield" in blob
        ):
            s += 30
        if role in ("Solo", "Support") and any(
            k in nlow for k in ("pridwen", "phoenix", "shifter", "spectral", "thebes")
        ):
            s += 18
        # Jungle/Carry shields are not Spectral-first
        if role in ("Jungle", "Carry", "Mid") and "spectral" in nlow:
            s -= 25
    # Solo AA / self-sustain bruisers: early Shifter's + hybrid LS when ladder is hot
    if role == "Solo" and (
        "self_sustain" in tags
        or "aa" in tags
        or float(bias.get("aa_score") or 0) >= 0.5
    ):
        if "shifter" in nlow:
            s += 36
            # Extra when item ladder says it's the meta king
            if (item.ladder_tier or "").upper() in ("S", "A"):
                s += 22
        if any(k in nlow for k in ("sanguine", "gladiator", "bloodforge", "devourer")):
            s += 24
        if item.item_type == "Hybrid" and (
            (item.ladder_tier or "").upper() in ("S", "A") or float(item.ladder_score or 0) >= 55
        ):
            s += 16
    if "high_cc" in tags or "hard_cc" in tags:
        s += cdr_v * 1.3 + 12
        if role == "Support" and item.item_type == "Defensive":
            s += 10
        if role == "Support" and any(k in nlow for k in ("isolation", "binding", "stygian")):
            s += 16
    if "immobile" in tags:
        if item.item_type == "Defensive" or _canon_stat_value(item.stats, "hp") >= 250:
            s += 22
        if any(k in nlow for k in ("alchemist", "magi", "cloak", "mantle", "spectral")):
            s += 16
    if "mobile" in tags or "gap_close" in tags:
        if role == "Jungle":
            s += pen_v * 0.5 + 8
        if physical and any(k in nlow for k in ("jotunn", "hydras", "arondight", "heartseeker")):
            s += 18
        if mage and any(k in nlow for k in ("blink", "spear of desolation")):
            s += 8
    if "pet_zone" in tags or "zone" in tags:
        if mage and any(k in nlow for k in ("magus", "gem of isolation", "divine", "soul gem", "grimoire")):
            s += 26
        s += cdr_v * 0.4
    if "ult_nuke" in tags:
        s += pen_v * 1.0 + 14
        if mage and any(k in nlow for k in ("obsi", "tahuti", "soul reaver", "dreamer")):
            s += 20
        if physical and any(k in nlow for k in ("titan", "parashu", "heartseeker", "bloodforge")):
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

    # Item tier ladder again at god-rescore (kit path assembly uses this score)
    # Slightly stronger here so S/A meta items win near-ties after kit filters.
    ladder_delta = _item_ladder_boost(
        ladder_tier=item.ladder_tier,
        ladder_score=float(item.ladder_score or 0),
        ladder_rank=item.ladder_rank,
        role=role,
        item_type=item.item_type or "",
        is_pen=pen_v >= 8 or "penetrat" in blob,
    )
    s += ladder_delta * 0.85

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
        # Patch heal axis only boosts true heal cores on real healers
        if _is_heal_core_item(item.name) and not _is_true_healer(bias):
            pass
        else:
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

    # Structured effect → item family boost (Magus for multi-hit, Chronos for spam, …)
    effects = bias.get("effects")
    if not effects:
        effects = extract_kit_effects(bias)
    fam_boost, _ = family_score_boost(item.name, effects)
    s += fam_boost
    s += prefer_ban_adjust(item.name, bias)
    s += aspect_item_score_delta(item.name, bias)

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
    if bias.get("force_archetype"):
        return str(bias["force_archetype"])
    tags: set[str] = set(bias.get("tags") or [])
    sb = float(bias.get("style_burst") or 0.5)
    sd = float(bias.get("style_dps") or 0.5)
    aa = float(bias.get("aa_score") or 0)

    if role == "Support":
        # Heal cores (Asclepius/Lifebinder) only for real heal kits — not every team_buff support
        if _is_true_healer(bias) and (
            "heavy_heal" in tags or "heal" in tags or "team_buff" in tags
        ):
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
        # Flex-friendly: mages, solo bruisers, and traditional assassins all get paths
        if mage:
            return "mage_jungle"
        # True AA jungle only — noisy "basic attack" tags made everyone aa_assassin
        if (aa >= 0.7 or ("aa" in tags and "as_steroid" in tags)) and "as_steroid" in tags:
            return "aa_assassin"
        if aa >= 0.75 and "aa" in tags:
            return "aa_assassin"
        # LS stack jungle (Thanatos / Kali style) — DG then pen, not pure ADC
        if "self_sustain" in tags and ("execute" in tags or "aa" in tags):
            return "sustain_assassin"
        if "execute" in tags and "gap_close" in tags:
            return "sustain_assassin"
        # Solo-style tanks / low-mobility bruisers flexed into jungle
        if (
            "gap_close" not in tags
            and aa < 0.45
            and (
                "heavy_shield" in tags
                or "shield" in tags
                or float(bias.get("style_utility") or 0) >= 0.45
            )
            and sb < 0.55
        ):
            return "bruiser_jungle"
        # Default ability jungle (includes most warriors flexed from Solo)
        return "burst_assassin"

    if role == "Carry":
        if mage:
            if "dot" in tags:
                return "dot_mage_adc"
            if "aa" in tags or aa >= 0.5:
                return "aa_mage_adc"
            return "ability_mage_adc"
        if "aa" in tags or aa >= 0.5 or "as_steroid" in tags:
            return "crit_adc"
        if sd > sb and ("prot_shred" in tags or aa >= 0.35):
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
    # Sustain mage only for real self-heal kits — not noisy heal_count flags
    if "self_sustain" in tags:
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


# Slot recipes: ordered identity of the 6-item grid (pen still enforced later).
# Ranked-first order: spike items early, luxury/shell late.
ARCHETYPE_SLOTS: dict[str, list[str]] = {
    # Mid / mage — pen + power first (not Soul Gem / sustain openers)
    "burst_mage": ["flat_pen", "pct_pen", "power", "cdr", "defense", "luxury"],
    "dot_mage": ["flat_pen", "pct_pen", "dot_core", "power", "cdr", "defense"],
    "mana_mage": ["mana_stack", "flat_pen", "pct_pen", "power", "cdr", "defense"],
    "channel_mage": ["flat_pen", "pct_pen", "power", "cdr", "defense", "luxury"],
    "spam_mage": ["cdr", "flat_pen", "pct_pen", "power", "defense", "sustain"],
    "sustain_mage": ["flat_pen", "pct_pen", "power", "sustain", "cdr", "defense"],
    "aa_mage": ["aa_core", "flat_pen", "pct_pen", "as_core", "power", "defense"],
    "zone_mage": ["flat_pen", "pct_pen", "zone_core", "power", "cdr", "defense"],
    # Carry — AS/LS → pen → crit/power (standard ranked ADC)
    "crit_adc": ["as_core", "ls_core", "pct_pen", "crit_core", "power", "defense"],
    "onhit_adc": ["as_core", "onhit", "pct_pen", "ls_core", "power", "defense"],
    "power_adc": ["as_core", "pct_pen", "ls_core", "power", "crit_core", "defense"],
    "dot_mage_adc": ["flat_pen", "pct_pen", "dot_core", "power", "sustain", "defense"],
    "aa_mage_adc": ["as_core", "flat_pen", "pct_pen", "power", "ls_core", "defense"],
    "ability_mage_adc": ["flat_pen", "pct_pen", "power", "cdr", "sustain", "defense"],
    # Jungle — Jotunn/Hydra OR stack, then power + pen (no mid Shifter/BoV)
    "burst_assassin": ["gap", "flat_pen", "power", "power", "pct_pen", "cdr"],
    "sustain_assassin": ["gap", "ls_core", "flat_pen", "power", "pct_pen", "cdr"],
    "aa_assassin": ["gap", "ls_core", "as_core", "flat_pen", "pct_pen", "power"],
    "bruiser_jungle": ["gap", "flat_pen", "power", "power", "pct_pen", "hybrid_bulk"],
    "mage_jungle": ["flat_pen", "power", "cdr", "pct_pen", "sustain", "power"],
    # Solo — offline damage + bulk (not pure aura shell)
    "tank_solo": ["hybrid_bulk", "defense", "mitigate", "power_bruiser", "antiheal", "cdr_def"],
    "sustain_solo": ["hybrid_bulk", "power_bruiser", "defense", "mitigate", "antiheal", "sustain_tank"],
    "shield_solo": ["hybrid_bulk", "shield_item", "defense", "power_bruiser", "antiheal", "mitigate"],
    "bruiser_solo": ["hybrid_bulk", "power_bruiser", "defense", "mitigate", "antiheal", "cdr_def"],
    "mage_solo": ["hybrid_bulk", "flat_pen", "defense", "mitigate", "cdr_def", "antiheal"],
    # Support — aura/utility first (Thebes/Stampede line), peel second
    "peel_support": ["aura", "mitigate", "defense", "cdr_def", "counter", "tenacity"],
    "lockdown_support": ["aura", "cdr_def", "mitigate", "defense", "counter", "tenacity"],
    "shield_support": ["aura", "shield_item", "mitigate", "defense", "cdr_def", "counter"],
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
        # ADC power is not Jotunn (hunter CDR lives in gap)
        if role == "Carry" and physical and any(k in n for k in ("jotunn",)):
            return False
        if physical and int_v >= 40 and str_v < 28:
            return False
        if mage and str_v >= 40 and int_v < 28:
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
        # Damage-type-correct sustain only
        if physical:
            return ls_v >= 8 or any(
                k in n for k in ("bloodforge", "devourer", "sanguine", "gladiator")
            )
        if mage:
            # Soul Gem is general mage sustain; Bancroft-line only via kit_ok + self_sustain
            return ls_v >= 8 or any(k in n for k in ("soul gem",))
        return ls_v >= 8
    if slot == "ls_core":
        if physical:
            return ls_v >= 8 or any(k in n for k in ("bloodforge", "devourer"))
        if mage:
            # ls_core on mages = Soul Gem path; Bancroft gated out of pool unless self_sustain
            return ls_v >= 8 or any(k in n for k in ("bancroft", "typhon", "gluttonous", "soul gem"))
        return ls_v >= 8
    if slot == "mana_stack":
        return (
            mp >= 250
            or any(k in n for k in ("thoth", "book of", "doom orb", "transcend"))
            or (mp >= 150 and "pendant" in n)
        )
    if slot == "dot_core":
        if physical:
            return any(k in n for k in ("crusher", "serpentine", "toxic", "brawler", "contagion"))
        return any(
            k in n
            for k in ("desolat", "magus", "divine", "soul reaver", "gem of isolation", "contagion", "grimoire")
        )
    if slot == "zone_core":
        return any(k in n for k in ("magus", "isolation", "divine", "soul gem", "grimoire", "gem of focus"))
    if slot == "aa_core" or slot == "as_core":
        if mage and any(k in n for k in ("titan", "bloodforge", "jotunn")):
            return False
        return as_v >= 15 or any(
            k in n
            for k in (
                "riptalon",
                "ichival",
                "demon",
                "wind demon",
                "golden blade",
                "avenging",
                "musashi",
                "eros",
                "qins",
                "death metal",
            )
        )
    if slot == "crit_core":
        return crit_v >= 15 or any(k in n for k in ("deathbringer", "demon blade", "rage", "wind", "death metal"))
    if slot == "onhit":
        return as_v >= 10 and (
            pen >= 5
            or "basic" in blob
            or any(k in n for k in ("riptalon", "executioner", "qins", "silverbranch"))
        )
    if slot == "gap":
        if mage:
            return cdr >= 10 and power_ok()
        # Jungle openers ONLY: Jotunn / Hydra / stacking (Trans, HS, DG).
        # Arondight / Crusher / Bloodforge are mid-build pen/power — not gap openers.
        if role == "Jungle":
            return any(
                k in n
                for k in ("jotunn", "hydra", "heartseeker", "transcend", "devourer")
            )
        return any(k in n for k in ("jotunn", "arondight", "hydra", "heartseeker", "transcend")) or (
            cdr >= 10 and power_ok()
        )
    if slot == "hybrid_bulk":
        return it.item_type == "Hybrid" or (
            hp >= 200 and (str_v >= 20 or int_v >= 20) and (pprot + mprot) >= 15
        )
    if slot == "power_bruiser":
        return power_ok() and (hp >= 150 or pprot + mprot >= 20 or it.item_type == "Hybrid")
    if slot == "mitigate":
        return damp >= 5 or plat >= 5 or ten >= 5 or any(
            k in n for k in ("alchemist", "spectral", "nemean", "mantle", "magi")
        )
    if slot == "counter":
        return (
            ("critical" in blob or "attack speed" in blob)
            and any(k in blob for k in ("reduc", "enemy", "less", "plating"))
        ) or any(k in n for k in ("spectral", "nemean", "midgardian", "witchblade"))
    if slot == "aura":
        # Pure heal actives must not fill generic aura slots (they have "ally" in text).
        # Heal gods pick them via heal_aura only.
        if _is_heal_core_item(it.name):
            return False
        # Spectral / Midgardian are counter peel — not generic aura openers
        if any(k in n for k in ("spectral", "midgardian", "nemean")):
            return False
        # Support meta auras + true team auras
        if any(
            k in n
            for k in (
                "thebes",
                "sovereignty",
                "heartward",
                "chandra",
                "contagion",
                "stampede",
                "amanita",
                "shogun",
            )
        ):
            return True
        return any(k in blob for k in ("ally", "allies", "aura", "team")) and it.item_type in (
            "Defensive",
            "Hybrid",
        )
    if slot == "tenacity":
        return ten >= 5 or "magi" in n or "tenacit" in blob
    if slot == "antiheal":
        if role == "Support":
            return any(k in n for k in ("contagion", "pestilence", "brawler")) or (
                "heal" in blob and any(k in blob for k in ("reduc", "anti", "curse", "aura"))
            )
        return any(k in n for k in ("divine", "brawler", "pestilence", "contagion", "toxic")) or (
            "heal" in blob and any(k in blob for k in ("reduc", "anti", "curse"))
        )
    if slot == "shield_item":
        # Frontline only — jungle must not open Spectral via shield_item
        if role in ("Jungle", "Carry", "Mid"):
            return False
        # Spectral is anti-crit counter (mitigate/counter), not a shield-aura opener
        if "spectral" in n:
            return False
        return "shield" in blob or any(k in n for k in ("pridwen", "phoenix", "shifter"))
    if slot == "heal_aura":
        # Asclepius / Lifebinder / Chandra-class team sustain (heal_support archetype only)
        return any(k in n for k in ("asclepius", "lifebinder", "chandra", "thebes", "sovereignty")) or (
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
    # Jungle ability openers first (Jotunn/Hydra), then pen finishers
    "burst": ["jotunn", "hydra", "desolat", "obsi", "titan", "soul reaver", "tahuti", "heartseeker"],
    "pet_zone": ["isolation", "magus", "soul gem", "divine", "grimoire"],
    "zone": ["isolation", "magus", "soul gem", "divine"],
    "aa": ["riptalon", "demon", "deathbringer", "qins", "ichival", "wind", "avenging", "musashi"],
    "as_steroid": ["riptalon", "demon", "ichival", "avenging", "wind"],
    # asclepius/lifebinder only land on true healers via kit_ok; chandra is safe aura
    # bancroft only injects when self_sustain (kit_ok) — keep off generic heal signatures
    "heal": ["chandra", "soul gem", "asclepius", "lifebinder"],
    "heavy_heal": ["asclepius", "lifebinder", "chandra"],
    # LS cores + Shifter offline hybrid (Solo AA/sustain maniacs when patch-hot)
    "self_sustain": [
        "shifter",
        "sanguine",
        "gladiator",
        "bancroft",
        "typhon",
        "gluttonous",
        "bloodforge",
        "devourer",
        "soul gem",
    ],
    "execute": ["bloodforge", "titan", "soul reaver", "deathbringer", "desolat", "obsi"],
    "prot_shred": ["executioner", "titan", "magus", "desolat", "void", "obsi", "crusher"],
    "shield": ["shifter", "pridwen", "phoenix"],
    "heavy_shield": ["shifter", "pridwen", "phoenix"],
    "high_cc": ["isolation", "binding", "breastplate", "genji", "stygian"],
    "hard_cc": ["isolation", "binding", "stygian"],
    "immobile": ["alchemist", "magi", "cloak", "mantle", "oni", "genji"],
    "mobile": ["jotunn", "hydra", "arondight", "heartseeker"],
    "gap_close": ["jotunn", "hydra", "arondight", "heartseeker", "transcend"],
    "team_buff": ["thebes", "sovereign", "heartward", "chandra"],
    "anti_cc": ["magi", "mantle", "alchemist", "prophetic"],
    "sustained": ["bloodforge", "devourer", "qins", "chronos", "pendant", "breastplate"],
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
        if slot == "heal_aura":
            # True healers: Asclepius/Lifebinder. Everyone else should not be here.
            if any(k in n for k in ("asclepius", "lifebinder")):
                sc += 70
            elif "chandra" in n:
                sc += 35
            elif any(k in n for k in ("thebes", "sovereignty")):
                sc += 20
        if slot == "aura" and role == "Support":
            # Meta support openers — Thebes / Stampede / Amanita beat Chandra/Spectral
            if any(k in n for k in ("thebes", "stampede", "amanita")):
                sc += 160
            elif any(k in n for k in ("sovereignty", "heartward", "shogun")):
                sc += 70
            elif "chandra" in n:
                sc += 15  # fine aura, not default over Thebes
            elif "contagion" in n:
                sc += 40
        if slot == "dot_core" and any(k in n for k in ("desolat", "magus", "isolation", "divine")):
            sc += 40
        if slot == "zone_core" and any(k in n for k in ("isolation", "magus", "desolat")):
            sc += 40
        if slot == "zone_core" and "soul gem" in n:
            sc -= 25  # luxury sustain, not zone identity
        if slot == "defense" and role in ("Carry", "Mid", "Jungle"):
            if any(k in n for k in ("genji", "breastplate", "valor", "alchemist", "magi", "cloak")):
                sc += 28
            if _canon_stat_value(x.stats, "cdr") >= 10:
                sc += 15
            # No team auras as "defense" on damage roles
            if any(k in n for k in ("thebes", "chandra", "spectral", "phoenix")):
                sc -= 40
        # --- Ranked meta cores by role (carry games need these spikes) ---
        if role == "Mid":
            if slot in ("flat_pen", "pct_pen", "power", "cdr", "dot_core", "zone_core", "mana_stack"):
                # High-SR openers: Deso / Book / Chronos — Obsidian is mid-build
                if any(k in n for k in ("desolat", "thoth", "book of", "chronos", "pendant", "doom orb")):
                    sc += 70
                if any(k in n for k in ("magus",)):
                    sc += 50
                if "obsi" in n:
                    sc += 35  # needed after online spike, not item 1
                if any(k in n for k in ("tahuti", "soul reaver", "rod of")):
                    sc += 30
                if any(k in n for k in ("soul gem", "gluttonous", "bancroft", "typhon")):
                    sc -= 25  # late luxury, not opener
                if any(k in n for k in ("world stone", "cosmic horror", "dreamer", "wish-granting")):
                    sc -= 35
                if any(k in n for k in ("lifebinder", "asclepius")):
                    sc -= 50  # mid is damage, not heal support
        if role == "Carry":
            if slot in ("as_core", "crit_core", "onhit", "ls_core", "pct_pen", "power"):
                # High-SR openers: Tyrfing / DG / Trans / AS shred
                if any(k in n for k in ("tyrfing", "odysseus", "devourer", "transcend")):
                    sc += 70
                if any(k in n for k in ("executioner", "riptalon", "qins", "ichival", "lernaean")):
                    sc += 55
                if any(k in n for k in ("titan", "deathbringer", "demon blade")):
                    sc += 40  # mid/late staples
                if any(k in n for k in ("bloodforge", "avenging", "musashi", "wind demon")):
                    sc += 30
                if any(k in n for k in ("runeforged", "crusher", "jotunn", "hydra", "pendulum")):
                    sc -= 45  # solo/jungle toys, not ADC cores
                if any(k in n for k in ("freya", "chandra", "phoenix", "spectral")):
                    sc -= 40
                if any(k in n for k in ("death metal",)):
                    sc -= 15  # situational, not default opener
        if role == "Jungle":
            if slot == "gap":
                if "jotunn" in n:
                    sc += 120
                elif "hydra" in n:
                    sc += 110
                elif "transcend" in n:
                    sc += 70
                elif "devourer" in n:
                    sc += 65
                elif "heartseeker" in n:
                    sc += 55
            if slot == "ls_core":
                if "devourer" in n:
                    sc += 80
                elif "bloodforge" in n:
                    sc += 25
            if slot in ("flat_pen", "pct_pen"):
                if any(k in n for k in ("titan", "pendulum", "crusher", "desolat", "obsi")):
                    sc += 45
                if any(k in n for k in ("executioner", "riptalon", "qins")):
                    sc -= 30
            if slot == "power":
                if any(k in n for k in ("arondight", "bloodforge", "reaper")):
                    sc += 35
                if any(k in n for k in ("executioner", "riptalon", "musashi", "avenging")):
                    sc -= 40
            if any(k in n for k in ("parashu", "dreamer", "wish-granting", "eye of erebus")):
                sc -= 20  # luxury last, not core
        if role == "Solo":
            if slot in ("hybrid_bulk", "power_bruiser", "sustain_tank"):
                if any(k in n for k in ("shifter", "gladiator", "sanguine", "berserker", "ancile")):
                    sc += 45
                if any(k in n for k in ("brawler", "runeforged", "void shield", "pestilence")):
                    sc += 30
            if slot in ("aura", "mitigate") and any(k in n for k in ("chandra", "thebes")):
                sc -= 25  # support auras are not solo cores
            if slot == "defense" and "spectral" in n:
                sc += 15  # fine mid-build anti-crit, not item 1
        if role == "Support":
            if slot in ("aura", "mitigate", "cdr_def", "defense"):
                if any(k in n for k in ("thebes", "stampede", "amanita")):
                    sc += 55
                if any(k in n for k in ("sovereignty", "heartward", "contagion", "genji", "breastplate")):
                    sc += 30
                # High-SR supports often open Shifter offline — allow it
                if "shifter" in n:
                    sc += 50
                if any(k in n for k in ("arondight", "tahuti", "deathbringer")):
                    sc -= 40  # not support cores
        if slot == "luxury":
            # Prefer passives for most gods; actives only when kit wants burst finisher
            if x.is_active_item and (x.total_cost or 0) >= 3200:
                if "burst" in tags or "ult_nuke" in tags or "execute" in tags:
                    sc += 8
                else:
                    sc -= 35
            elif any(k in n for k in ("tahuti", "soul reaver", "myrddin", "deathbringer", "bloodforge")):
                sc += 18
            if any(k in n for k in ("world stone", "cosmic horror", "dreamer", "wish-granting", "parashu")):
                sc -= 10
        # Kit-tag signature affinity (primary god differentiator)
        sc += _tag_signature_boost(n, tags, slot)
        # Light salt only on flex/shell slots — never scramble ranked cores
        if diversify_key and slot not in RANKED_CORE_SLOTS:
            salt = _god_slot_salt(diversify_key, slot, role, x.name) % 17
            sc += salt * 0.35
        return sc

    cands.sort(key=slot_rank, reverse=True)

    # Ranked spike slots: always best candidate (pen / AS / gap / etc.)
    hard_core = slot in RANKED_CORE_SLOTS and slot not in ("power", "ls_core", "hybrid_bulk")
    if hard_core or (role == "Jungle" and slot == "gap"):
        return cands[0]

    # Mild diversify on power / shell / flex so gods aren't clones, without
    # scrambling Deso/Titan/Jotunn openers.
    if diversify_key and len(cands) > 1:
        top_k = 2 if slot in ("power", "ls_core", "defense", "cdr", "hybrid_bulk") else 3
        top_k = min(top_k, len(cands))
        best = slot_rank(cands[0])
        # Tight floor — only true near-peers (not random junk)
        floor = best - max(25.0, abs(best) * 0.12)
        near = [c for c in cands[:top_k] if slot_rank(c) >= floor]
        if not near:
            near = cands[:1]
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


def _ensure_owned_god_items(
    path: list[ScoredItem],
    pool: list[ScoredItem],
    god_name: str,
    *,
    max_actives: int,
    role: str,
) -> list[ScoredItem]:
    """
    Pin owner-only lines when they exist in the pool (Ratatoskr acorns).
    Shared shop remains the rest of the path.
    """
    if not path or not god_name:
        return path
    g = god_name.lower()
    if "ratatoskr" not in g:
        return path
    path = list(path)
    if any("acorn" in x.name.lower() for x in path):
        return path
    acorns = [
        x
        for x in pool
        if "acorn" in x.name.lower() and item_allowed_for_god(x.name, god_name)
    ]
    if not acorns:
        return path
    # Prefer higher-scored T3-ish acorn; salt by role so Solo ≠ Jungle
    acorns.sort(
        key=lambda x: x.role_score + (_god_slot_salt(god_name, "acorn", role, x.name) % 11),
        reverse=True,
    )
    pick = acorns[0]
    seen = {x.name for x in path}
    if pick.name in seen:
        return path
    # Replace lowest-priority non-opener / non-pen slot
    drop = None
    ranked = sorted(range(len(path)), key=lambda i: path[i].role_score)
    for i in ranked:
        n = path[i].name.lower()
        if is_pen_item(path[i]) or _is_jungle_standard_opener(n):
            continue
        if path[i].is_active_item and pick.is_active_item:
            continue
        drop = i
        break
    if drop is None:
        if len(path) < 6:
            path.append(pick)
        return path[:6]
    if path[drop].is_active_item and not pick.is_active_item:
        pass  # free an active slot
    path[drop] = pick
    return path[:6]


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
    """
    Light last-slot flavor only. Never scramble pen / power / AS / crit cores —
    ranked paths must stay spike-first; uniqueness is kit tags + defense/luxury.
    Jungle: also flavor one mid power toy so assassin clones (Rat/Thor) diverge.
    """
    if not path or not dkey:
        return path
    path = list(path)
    seen = {x.name for x in path}
    # Never swap pen, openers, or early cores — only last 1–2 shell/luxury slots
    pen_idxs = [
        i
        for i, it in enumerate(path)
        if is_pen_item(it) and _pen_matches_kit(it, mage=mage, physical=physical)
    ]
    protected_keys = (
        "jotunn",
        "hydra",
        "transcend",
        "heartseeker",
        "devourer",
        "titan",
        "obsi",
        "desolat",
        "magus",
        "executioner",
        "deathbringer",
        "demon blade",
        "riptalon",
        # Solo/Support staples only — never protect mid-shell on Jungle
        "thebes",
        "stampede",
    )
    if role != "Jungle":
        protected_keys = protected_keys + ("shifter",)

    def is_protected(it: ScoredItem, idx: int) -> bool:
        n = it.name.lower()
        if is_pen_item(it) and _pen_matches_kit(it, mage=mage, physical=physical):
            return True
        if role == "Jungle" and _is_jungle_standard_opener(n):
            return True
        # Jungle: shells are never protected (gank damage path)
        if role == "Jungle" and any(
            k in n
            for k in (
                "shifter",
                "breastplate",
                "genji",
                "spectral",
                "midgardian",
                "thebes",
                "prophetic",
            )
        ):
            return False
        if any(k in n for k in protected_keys):
            return True
        # First two slots are spike openers — leave them
        if idx < 2:
            return True
        return False

    # Flavor 1–2 trailing slots (defense / last power) so gods diverge without
    # touching Jotunn/Deso/Titan cores. Jungle may also re-roll one mid power toy.
    order = list(range(len(path) - 1, -1, -1))
    targets: list[int] = []
    for i in order:
        if is_protected(path[i], i):
            continue
        if len(pen_idxs) <= 2 and i in pen_idxs:
            continue
        if role in DAMAGE_ROLES_NEED_PEN and i < max(3, len(path) - 2):
            # Jungle exception: allow one mid-index power flex (slot 2–4)
            if not (role == "Jungle" and 2 <= i <= 4):
                continue
        targets.append(i)
        if len(targets) >= (3 if role == "Jungle" else 2):
            break
    if not targets:
        return path

    for ti, target in enumerate(targets):
        seen = {x.name for x in path}
        actives = sum(1 for x in path if x.is_active_item)
        alts = [
            x
            for x in pool
            if x.name not in seen
            and not (x.is_active_item and actives >= max_actives and not path[target].is_active_item)
        ]
        filtered: list[ScoredItem] = []
        for x in alts:
            str_v = _canon_stat_value(x.stats, "str")
            int_v = _canon_stat_value(x.stats, "int")
            nlow = x.name.lower()
            if mage and int_v < 25 and x.item_type not in ("Defensive", "Hybrid") and str_v > int_v + 10:
                continue
            if physical and str_v < 15 and x.item_type not in ("Defensive", "Hybrid") and int_v > str_v + 20:
                continue
            if role in DAMAGE_ROLES_NEED_PEN and x.item_type == "Defensive" and item_pen_value(x) < 5:
                if _canon_stat_value(x.stats, "cdr") < 8 and int_v + str_v < 25:
                    continue
            if role == "Support":
                if any(
                    k in nlow
                    for k in ("dreamer", "wish-granting", "parashu", "deathbringer", "tahuti", "soul reaver")
                ):
                    continue
                if x.item_type == "Offensive" and _canon_stat_value(x.stats, "hp") < 150:
                    continue
            if role == "Solo" and any(k in nlow for k in ("deathbringer", "dreamer", "wish-granting", "parashu")):
                continue
            if role == "Jungle" and (_is_jungle_adc_toy(nlow) or "executioner" in nlow):
                if "as_steroid" not in tags:
                    continue
            filtered.append(x)
        if not filtered:
            continue
        filtered.sort(
            key=lambda x: (
                x.role_score
                + _tag_signature_boost(x.name.lower(), tags, "flavor")
                + (_god_slot_salt(dkey, f"flavor{ti}", role, x.name) % 71) * 1.6
            ),
            reverse=True,
        )
        # Jungle: offset into near-best cluster so assassin clones diverge.
        # Other roles: keep mild salt pick among top 10 (spike cores stay tight).
        if role == "Jungle":
            top = filtered[:14]
            off = _god_slot_salt(dkey, f"flavor_pick{ti}", role) % min(len(top), 6)
            pick = top[off]
            if pick.name == path[target].name and len(top) > 1:
                pick = top[
                    (off + 1 + _god_slot_salt(dkey, f"flavor_bump{ti}", role) % 3) % len(top)
                ]
        else:
            top = filtered[:10]
            pick = top[_god_slot_salt(dkey, f"flavor_pick{ti}", role) % len(top)]
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


def _is_jungle_standard_opener(nlow: str) -> bool:
    """True for Jotunn / Hydra / stacking openers (Trans, HS, DG) only."""
    return any(
        k in nlow for k in ("jotunn", "hydra", "transcend", "heartseeker", "devourer")
    )


def _is_jungle_adc_toy(nlow: str) -> bool:
    """Crit/AS ADC items that do not belong on ability jungle paths."""
    return any(
        k in nlow
        for k in (
            "deathbringer",
            "demon blade",
            "musashi",
            "avenging blade",
            "wind demon",
            "rage",
            "riptalon",
            "death metal",
            "ichival",
            "eros",
            "lernaean",
            "silverbranch",
            "qins",
        )
    )


def _is_jungle_opener_family(nlow: str) -> bool:
    """Opener-line items — cap how many sit in one path (Jotunn+Hydra OK)."""
    return _is_jungle_standard_opener(nlow)


def _normalize_jungle_path(
    path: list[ScoredItem],
    pool: list[ScoredItem],
    bias: dict,
    *,
    mage: bool,
    physical: bool,
    max_actives: int,
) -> list[ScoredItem]:
    """
    Enforce standard jungle identity:
      1) Open Jotunn / Hydra OR a stacking item (Trans / HS / DG)
      2) Then pen + power (not four more openers, not ADC toys)
    """
    if not path:
        return path
    path = list(path)
    arch = detect_archetype(bias, "Jungle", mage, physical)
    aa = arch == "aa_assassin"
    seen = {x.name for x in path}

    def ok_replace(alt: ScoredItem) -> bool:
        if alt.name in seen:
            return False
        n = alt.name.lower()
        if not aa and _is_jungle_adc_toy(n):
            return False
        if mage and _canon_stat_value(alt.stats, "int") < 25 and alt.item_type != "Defensive":
            return False
        if physical and _canon_stat_value(alt.stats, "str") < 15 and item_pen_value(alt) < 5:
            if _canon_stat_value(alt.stats, "as") > 0 and not aa:
                return False
        return True

    def best_opener() -> ScoredItem | None:
        scored: list[tuple[float, ScoredItem]] = []
        for x in pool:
            n = x.name.lower()
            if mage:
                # Mage jungle: pen cores first (Deso / Magus / Obsidian)
                if any(k in n for k in ("desolat", "magus", "obsi")):
                    sc = 100 + x.role_score * 0.01
                elif item_pen_value(x) >= 8 and _canon_stat_value(x.stats, "int") >= 40:
                    sc = 80 + x.role_score * 0.01
                else:
                    continue
            else:
                if not _is_jungle_standard_opener(n):
                    continue
                if "jotunn" in n:
                    sc = 120.0
                elif "hydra" in n:
                    sc = 110.0
                elif "transcend" in n or "devourer" in n:
                    sc = 80.0
                else:
                    sc = 60.0  # heartseeker
                sc += x.role_score * 0.01
            scored.append((sc, x))
        if not scored:
            return None
        scored.sort(key=lambda t: t[0], reverse=True)
        return scored[0][1]

    def best_pen(exclude: set[str]) -> ScoredItem | None:
        cands = []
        for x in pool:
            if x.name in exclude:
                continue
            n = x.name.lower()
            # Never re-introduce opener-line items as "pen" (HS has pen but is a stack opener)
            if _is_jungle_standard_opener(n):
                continue
            if not _pen_matches_kit(x, mage=mage, physical=physical):
                continue
            if item_pen_value(x) < 8:
                continue
            if not aa and _is_jungle_adc_toy(n):
                continue
            if not aa and "executioner" in n:
                continue
            cands.append(x)
        cands.sort(key=lambda x: (item_pen_value(x), x.role_score), reverse=True)
        return cands[0] if cands else None

    def best_power(exclude: set[str]) -> ScoredItem | None:
        cands = []
        for x in pool:
            if x.name in exclude:
                continue
            n = x.name.lower()
            if _is_jungle_standard_opener(n):
                continue  # don't pile more openers as "power"
            if not aa and (_is_jungle_adc_toy(n) or "executioner" in n):
                continue
            # Never inject mid-shell as "power"
            if any(
                k in n
                for k in (
                    "shifter",
                    "breastplate",
                    "genji",
                    "spectral",
                    "midgardian",
                    "prophetic",
                    "thebes",
                    "oni hunter",
                    "leviathan",
                )
            ):
                continue
            str_v = _canon_stat_value(x.stats, "str")
            int_v = _canon_stat_value(x.stats, "int")
            if mage and int_v < 40:
                continue
            if physical and str_v < 30 and item_pen_value(x) < 8:
                continue
            if x.item_type == "Defensive" and item_pen_value(x) < 5:
                continue
            # Prefer named power cores (not Hydra — that is an opener)
            bonus = 0
            if any(
                k in n
                for k in (
                    "arondight",
                    "bloodforge",
                    "reaper",
                    "crusher",
                    "pendulum",
                    "tahuti",
                    "soul reaver",
                    "parashu",
                )
            ):
                bonus = 45
            cands.append((bonus + x.role_score, x))
        cands.sort(key=lambda t: t[0], reverse=True)
        return cands[0][1] if cands else None

    # Mid-build shell ruins gank tempo (ability + AA jungle). Strip from first 5 slots.
    shell_keys = (
        "shifter",
        "breastplate",
        "genji",
        "spectral",
        "oni hunter",
        "midgardian",
        "contagion",
        "prophetic",
        "leviathan",
        "thebes",
        "chandra",
        "gladiator",
        "mantle of discord",
        "magi's",
    )

    def is_mid_shell(it: ScoredItem) -> bool:
        n = it.name.lower()
        if any(k in n for k in shell_keys):
            return True
        if it.item_type == "Defensive" and item_pen_value(it) < 8 and (
            _canon_stat_value(it.stats, "str") + _canon_stat_value(it.stats, "int") < 35
        ):
            return True
        return False

    def best_aa_damage(exclude: set[str]) -> ScoredItem | None:
        cands = []
        for x in pool:
            if x.name in exclude:
                continue
            n = x.name.lower()
            if is_mid_shell(x):
                continue
            as_v = _canon_stat_value(x.stats, "as")
            str_v = _canon_stat_value(x.stats, "str")
            ls_v = _canon_stat_value(x.stats, "ls")
            pen = item_pen_value(x)
            if as_v < 10 and str_v < 35 and pen < 8 and ls_v < 10:
                continue
            if x.item_type == "Defensive" and pen < 8 and as_v < 15:
                continue
            bonus = 0.0
            if any(
                k in n
                for k in (
                    "riptalon",
                    "qins",
                    "odysseus",
                    "executioner",
                    "devourer",
                    "bloodforge",
                    "dominance",
                )
            ):
                bonus += 50
            if as_v >= 15:
                bonus += 25
            if ls_v >= 10:
                bonus += 15
            cands.append((bonus + x.role_score, x))
        cands.sort(key=lambda t: t[0], reverse=True)
        return cands[0][1] if cands else None

    # Strip ADC toys from ability junglers
    if not aa:
        for i, it in enumerate(path):
            n = it.name.lower()
            if _is_jungle_adc_toy(n) or "executioner" in n:
                alt = best_pen(seen) or best_power(seen)
                if alt:
                    seen.discard(it.name)
                    path[i] = alt
                    seen.add(alt.name)

    # All jungle: no Shifter/BoV/Genji in first 5 (optional last-slot shell only)
    for i, it in enumerate(path[:5]):
        if not is_mid_shell(it):
            continue
        if aa and physical:
            alt = best_aa_damage(seen) or best_power(seen) or best_pen(seen)
        else:
            alt = best_power(seen) or best_pen(seen)
        if not alt:
            # Broader fallback: any high power/pen passive not already in path
            for x in sorted(pool, key=lambda z: z.role_score, reverse=True):
                if x.name in seen or is_mid_shell(x):
                    continue
                if x.is_active_item:
                    continue
                pv = item_pen_value(x)
                pow_v = _canon_stat_value(x.stats, "str") + _canon_stat_value(x.stats, "int")
                if pv >= 8 or pow_v >= 40:
                    alt = x
                    break
        if alt:
            seen.discard(it.name)
            path[i] = alt
            seen.add(alt.name)

    # Ability physical: prefer dual openers Jotunn + Hydra (the ranked standard)
    if physical and not aa:
        has_j = any("jotunn" in x.name.lower() for x in path)
        has_h = any("hydra" in x.name.lower() for x in path)
        if has_j and not has_h:
            hyd = next(
                (x for x in pool if "hydra" in x.name.lower() and x.name not in seen),
                None,
            )
            if hyd:
                # Replace weakest non-opener non-pen
                ranked = sorted(
                    range(len(path)),
                    key=lambda i: (
                        100 if _is_jungle_standard_opener(path[i].name.lower()) else 0,
                        80
                        if _pen_matches_kit(path[i], mage=mage, physical=physical)
                        and item_pen_value(path[i]) >= 15
                        else 0,
                        path[i].role_score,
                    ),
                )
                for i in ranked:
                    if _is_jungle_standard_opener(path[i].name.lower()):
                        continue
                    seen.discard(path[i].name)
                    path[i] = hyd
                    seen.add(hyd.name)
                    break
        if has_h and not has_j:
            jot = next(
                (x for x in pool if "jotunn" in x.name.lower() and x.name not in seen),
                None,
            )
            if jot:
                ranked = sorted(
                    range(len(path)),
                    key=lambda i: (
                        100 if _is_jungle_standard_opener(path[i].name.lower()) else 0,
                        path[i].role_score,
                    ),
                )
                for i in ranked:
                    if _is_jungle_standard_opener(path[i].name.lower()):
                        continue
                    seen.discard(path[i].name)
                    path[i] = jot
                    seen.add(jot.name)
                    break

    # Ensure a standard opener is present and first after ordering
    has_opener = any(
        _is_jungle_standard_opener(x.name.lower())
        or (mage and any(k in x.name.lower() for k in ("desolat", "magus", "obsi", "focus")))
        for x in path
    )
    if not has_opener:
        op = best_opener()
        if op:
            # replace weakest non-pen item
            drop = min(
                range(len(path)),
                key=lambda i: (
                    100 if _pen_matches_kit(path[i], mage=mage, physical=physical) else 0,
                    path[i].role_score,
                ),
            )
            seen.discard(path[drop].name)
            path[drop] = op
            seen.add(op.name)

    # Cap opener-family at 2 (Jotunn+Hydra, or one gap + one stack)
    opener_idxs = [
        i for i, x in enumerate(path) if _is_jungle_standard_opener(x.name.lower())
    ]
    if len(opener_idxs) > 2:
        def op_keep_score(i: int) -> float:
            n = path[i].name.lower()
            if "jotunn" in n:
                return 100
            if "hydra" in n:
                return 90
            if "transcend" in n or "devourer" in n:
                return 70
            return 50  # heartseeker

        opener_idxs.sort(key=op_keep_score, reverse=True)
        pen_n = sum(
            1
            for x in path
            if _pen_matches_kit(x, mage=mage, physical=physical) and item_pen_value(x) >= 8
        )
        for i in opener_idxs[2:]:
            # Prefer power once pen is covered; else pen
            alt = (best_power(seen) if pen_n >= 2 else None) or best_pen(seen) or best_power(seen)
            if alt:
                seen.discard(path[i].name)
                path[i] = alt
                seen.add(alt.name)
                if item_pen_value(alt) >= 8:
                    pen_n += 1

    # Need real pen in the build
    pen_items = [
        x
        for x in path
        if _pen_matches_kit(x, mage=mage, physical=physical) and item_pen_value(x) >= 8
    ]
    if len(pen_items) < 2:
        need = 2 - len(pen_items)
        for _ in range(need):
            alt = best_pen(seen)
            if not alt:
                break
            # drop extra opener or pure power without pen
            drop = None
            for i, it in enumerate(path):
                n = it.name.lower()
                if _is_jungle_standard_opener(n) and sum(
                    1 for x in path if _is_jungle_standard_opener(x.name.lower())
                ) > 1:
                    # only drop if we still keep one opener
                    if not any(
                        j != i and _is_jungle_standard_opener(path[j].name.lower())
                        for j in range(len(path))
                    ):
                        continue
                    drop = i
                    break
            if drop is None:
                for i, it in enumerate(path):
                    if item_pen_value(it) < 5 and it.item_type != "Defensive":
                        if not _is_jungle_standard_opener(it.name.lower()) or len(
                            [x for x in path if _is_jungle_standard_opener(x.name.lower())]
                        ) > 1:
                            drop = i
                            break
            if drop is None:
                break
            seen.discard(path[drop].name)
            path[drop] = alt
            seen.add(alt.name)

    # Active budget
    while sum(1 for x in path if x.is_active_item) > max_actives:
        for i, it in enumerate(path):
            if it.is_active_item:
                alt = best_power(seen) or best_pen(seen)
                if alt and not alt.is_active_item:
                    seen.discard(it.name)
                    path[i] = alt
                    seen.add(alt.name)
                break
        else:
            break

    return path[:6]


def _ensure_inspired_cores(
    path: list[ScoredItem],
    pool: list[ScoredItem],
    role: str,
    god_name: str,
    *,
    mage: bool,
    physical: bool,
    max_actives: int,
) -> list[ScoredItem]:
    """
    Inject 1–2 high-SR openers/staples into the path when missing.
    Order is applied later by _order_buy_path — this only ensures the items exist.
    """
    from .tracker_inspire import load_inspiration

    data = load_inspiration()
    if not data or not path:
        return path
    path = list(path)
    seen = {x.name for x in path}
    want: list[str] = []

    # God-specific openers first
    gr = (data.get("by_god_role") or {}).get(f"{god_name}|{role}")
    if gr and gr.get("games", 0) >= 3:
        for name, meta in list((gr.get("openers") or {}).items())[:3]:
            if float(meta.get("rate") or 0) >= 0.18:
                want.append(name)
    # Role openers (high-SR)
    rr = (data.get("by_role") or {}).get(role) or {}
    for name, meta in list((rr.get("openers") or {}).items())[:4]:
        if float(meta.get("rate") or 0) >= 0.12 and name not in want:
            want.append(name)

    # Role hard staples from ladder snapshot (always try if legal)
    role_staples = {
        "Mid": ("Spear of Desolation", "Book of Thoth", "Obsidian Shard"),
        "Carry": ("Tyrfing", "Devourer's Gauntlet", "Titan's Bane", "The Executioner"),
        "Jungle": ("Jotunn's Revenge", "Hydra's Lament", "Titan's Bane"),
        "Solo": ("Shifter's Shield", "Genji's Guard", "Breastplate of Valor"),
        "Support": ("Gauntlet of Thebes", "Shifter's Shield", "Stampede"),
    }
    # Magical gods flexed to Jungle/Carry/Mid — Deso/Book/Obsidian, not Jotunn
    if mage and role in ("Jungle", "Carry", "Mid"):
        role_staples = {
            **role_staples,
            "Jungle": ("Spear of Desolation", "Book of Thoth", "Obsidian Shard", "Rod of Tahuti"),
            "Carry": ("Spear of Desolation", "Book of Thoth", "Obsidian Shard", "Soul Reaver"),
        }
    for name in role_staples.get(role, ()):
        if name not in want:
            want.append(name)

    # Jungle high-SR is polluted by Solo flex / bruiser games — never inspire shells
    _jungle_shell_ban = (
        "shifter",
        "breastplate",
        "genji",
        "spectral",
        "midgardian",
        "thebes",
        "prophetic",
        "oni hunter",
        "leviathan",
        "gladiator",
        "dwarven",
        "contagion",
        "mantle of discord",
        "magi's",
        "chandra",
    )

    def legal(it: ScoredItem) -> bool:
        if it.name in seen:
            return False
        if not item_allowed_for_god(it.name, god_name):
            return False
        n = it.name.lower()
        if role == "Jungle" and any(k in n for k in _jungle_shell_ban):
            return False
        if mage and _canon_stat_value(it.stats, "int") < 20 and item_pen_value(it) < 5:
            if it.item_type not in ("Defensive", "Hybrid"):
                return False
        if physical and _canon_stat_value(it.stats, "str") < 15 and item_pen_value(it) < 5:
            if _canon_stat_value(it.stats, "as") <= 0 and it.item_type not in ("Defensive", "Hybrid"):
                return False
        return True

    injected = 0
    for name in want:
        if injected >= 2:
            break
        if any(x.name == name for x in path):
            continue
        # Skip shell names before pool lookup (tracker openers often include Shifter)
        if role == "Jungle" and any(k in name.lower() for k in _jungle_shell_ban):
            continue
        cand = next((x for x in pool if x.name == name and legal(x)), None)
        if not cand:
            # fuzzy name match
            nl = name.lower()
            cand = next(
                (
                    x
                    for x in pool
                    if (nl in x.name.lower() or x.name.lower() in nl) and legal(x)
                ),
                None,
            )
        if not cand:
            continue
        # Replace weakest non-opener / non-pen late item
        drop = None
        for i, it in enumerate(path):
            n = it.name.lower()
            if item_pen_value(it) >= 15:
                continue
            if role == "Jungle" and _is_jungle_standard_opener(n):
                continue
            # Protect role openers; do NOT protect Shifter on Jungle (shell ban above)
            protect = ("desolat", "thoth", "jotunn", "hydra", "tyrfing")
            if role != "Jungle":
                protect = protect + ("shifter", "thebes")
            if any(k in n for k in protect):
                continue
            drop = i
            break
        if drop is None:
            drop = len(path) - 1
        seen.discard(path[drop].name)
        path[drop] = cand
        seen.add(cand.name)
        injected += 1

    # Active budget
    while sum(1 for x in path if x.is_active_item) > max_actives:
        for i, it in enumerate(path):
            if it.is_active_item:
                for alt in pool:
                    if alt.name not in seen and not alt.is_active_item and legal(alt):
                        seen.discard(it.name)
                        path[i] = alt
                        seen.add(alt.name)
                        break
                break
        else:
            break
    return path[:6]


def _order_buy_path(
    path: list[ScoredItem],
    role: str,
    *,
    god_name: str | None = None,
) -> list[ScoredItem]:
    """
    Buy order is half the build. High-SR Ranked Conquest order (tracker.gg):

      Mid:     Book / Deso / Chronos → flat pen → Obsidian → Tahuti/Reaver
      Carry:   Tyrfing / DG / Trans / AS → pen (Titan) → crit finishers
      Jungle:  Jotunn / Hydra / stack → Titan/Crusher → power
      Solo:    Shifter offline → bulk / Genji / BP
      Support: Shifter / Thebes / Stampede → peel shells → Spectral last

    When tracker avg_slot is available for an item, it is the primary sort key.
    Heuristics fill gaps so we never open with late % pen or luxury.
    """
    if not path:
        return path

    damage = role in DAMAGE_ROLES_NEED_PEN
    gname = god_name or ""

    def heuristic_phase(it: ScoredItem) -> tuple[int, int]:
        """(phase 0..5, sub-priority). Lower = buy sooner."""
        pen = item_pen_value(it)
        cost = it.total_cost or 2500
        nlow = it.name.lower()
        str_v = _canon_stat_value(it.stats, "str")
        int_v = _canon_stat_value(it.stats, "int")
        as_v = _canon_stat_value(it.stats, "as")
        crit_v = _canon_stat_value(it.stats, "crit")
        pure_shell = (
            it.item_type == "Defensive"
            or any(
                k in nlow
                for k in (
                    "spectral",
                    "alchemist",
                    "phoenix",
                    "midgardian",
                    "nemean",
                    "magi",
                    "contagion",
                )
            )
        ) and pen < 8 and as_v < 15 and crit_v < 15

        # --- Late finishers (never open) ---
        if any(
            k in nlow
            for k in (
                "deathbringer",
                "tahuti",
                "soul reaver",
                "rod of",
                "dreamer",
                "wish-granting",
                "parashu",
                "world stone",
                "cosmic horror",
            )
        ):
            return 5, cost
        if "soul gem" in nlow:
            return 4, cost  # mid/late luxury, not item 1 (high-SR still builds it late)

        if role == "Mid":
            # 0: stack / flat pen openers (Book, Deso, Chronos, Doom)
            if any(
                k in nlow
                for k in (
                    "book of",
                    "thoth",
                    "desolat",
                    "chronos",
                    "pendant",
                    "doom orb",
                    "transcend",
                )
            ):
                return 0, cost
            if pen >= 8 and pen < 16 and int_v >= 40:  # Magus-class flat
                return 1, cost
            if pen >= 16 or "obsi" in nlow:  # Obsidian after spike
                return 2, -pen
            if pure_shell:
                return 4, cost
            if int_v >= 50:
                return 3, cost
            return 3, cost

        if role == "Carry":
            # 0: online spike — Tyrfing, DG, Trans, AS shred
            if any(
                k in nlow
                for k in (
                    "tyrfing",
                    "devourer",
                    "transcend",
                    "lernaean",
                    "executioner",
                    "riptalon",
                    "qins",
                    "ichival",
                    "avenging",
                    "odysseus",
                )
            ):
                return 0, cost
            if any(k in nlow for k in ("bloodforge", "musashi", "demon blade", "wind demon")):
                return 1, cost
            if pen >= 12 or "titan" in nlow:  # Titan mid, not first
                return 2, -pen
            if crit_v >= 15:
                return 3, -crit_v
            if pure_shell:
                return 4, cost
            return 2, cost

        if role == "Jungle":
            if _is_jungle_standard_opener(nlow):
                if "jotunn" in nlow:
                    return 0, 0
                if "hydra" in nlow:
                    return 0, 1
                if "transcend" in nlow or "devourer" in nlow:
                    return 0, 2
                return 0, 3  # HS
            if pen >= 8:
                return 1, -pen
            if pure_shell or "shifter" in nlow:
                return 3, cost
            return 2, cost

        if role == "Solo":
            if "shifter" in nlow:
                return 0, 0
            if any(
                k in nlow
                for k in (
                    "berserker",
                    "gladiator",
                    "sanguine",
                    "runeforged",
                    "genji",
                    "breastplate",
                    "valor",
                    "dwarven",
                )
            ):
                return 1, cost
            if pure_shell or any(k in nlow for k in ("thebes", "chandra", "amanita")):
                return 2, cost
            return 2, cost

        if role == "Support":
            # High-SR opens Shifter OR Thebes/Stampede — both phase 0
            if any(
                k in nlow
                for k in (
                    "shifter",
                    "thebes",
                    "stampede",
                    "amanita",
                    "yogi",
                    "prophetic",
                )
            ):
                return 0, cost
            if any(k in nlow for k in ("genji", "breastplate", "valor", "shell of rebuke")):
                return 1, cost
            if any(k in nlow for k in ("spectral", "midgardian", "nemean")):
                return 3, cost  # counter, not opener
            if pure_shell:
                return 2, cost
            return 2, cost

        # fallback
        if pure_shell:
            return 3 if damage else 0, cost
        if pen >= 10:
            return 1, -pen
        return 2, cost

    def sort_key(it: ScoredItem) -> tuple:
        # Primary: high-SR average inventory slot when known
        avg = inspiration_buy_rank(it.name, god_name=gname, role=role)
        phase, sub = heuristic_phase(it)
        cost = it.total_cost or 2500
        if avg is not None:
            # Blend: tracker position dominates, heuristic breaks ties
            return (avg, phase, sub, cost, -it.role_score)
        return (float(phase), float(sub), cost, -it.role_score, 0.0)

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
    *,
    use_aspect: bool = False,
    aspect_id: int | None = None,
) -> dict[str, Any] | None:
    """
    Ranked Conquest path for one god × role.

    Implements docs/BUILD_ALGORITHM.md phases P0–P8.
    Returns None when the role is illegal for this kit (e.g. melee on Carry
    without an aspect that enables ranged basics).
    """
    # --- P0 Context ---
    profile = ROLE_PROFILES[role]
    bias = god_scaling_bias(conn, god["god_id"])
    if use_aspect or aspect_id is not None:
        bias = build_aspect_bias(conn, god["god_id"], bias, aspect_id=aspect_id)
    dtype = god.get("primary_damage_type")

    # Carry is duo ADC — melee basics don't work unless aspect enables ranged AA
    if role == "Carry":
        base_range = load_god_attack_range(conn, int(god["god_id"]))
        bias["attack_range"] = base_range
        native: list[str] = []
        # Prefer explicit native list if caller attached it
        for key in ("native_roles", "role_list", "roles"):
            raw = god.get(key)
            if isinstance(raw, list):
                native = [str(x) for x in raw]
                break
            if isinstance(raw, str) and raw.strip():
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        native = []
                        for rr in parsed:
                            s = str(rr)
                            m = re.search(r"Role\.([A-Za-z]+)", s)
                            native.append(m.group(1) if m else s)
                except json.JSONDecodeError:
                    native = [raw]
                break
        aspect_blob = ""
        if bias.get("is_aspect"):
            aspect_blob = " ".join(
                str(bias.get(k) or "")
                for k in ("aspect_name", "aspect_description", "ability_blob")
            )
        ok, reason = carry_role_allowed(
            base_range=base_range,
            is_aspect=bool(bias.get("is_aspect")),
            aspect_blob=aspect_blob,
            native_roles=native,
        )
        if not ok:
            return None
        bias["carry_allow_reason"] = reason
    # --- P1 Score universe + P3 God rescore (rescore_for_god includes kit + soft high-SR) ---
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

    # Shared T3 + this god's own lines (e.g. Ratatoskr acorns)
    _gname_early = str(
        bias.get("god_name") or god.get("entity_name") or god.get("name") or ""
    )
    t3 = [
        s
        for s in scored
        if is_build_pool_item(next(i for i in items if i["name"] == s.name), _gname_early)
    ]

    tags_kit = set(bias.get("tags") or [])
    aaish = "aa" in tags_kit or float(bias.get("aa_score") or 0) >= 0.5 or "as_steroid" in tags_kit

    god_name_gate = str(
        bias.get("god_name") or god.get("entity_name") or god.get("name") or ""
    )

    # --- P2 Hard gates (kit_ok) ---
    def kit_ok(s: ScoredItem) -> bool:
        str_v = _canon_stat_value(s.stats, "str")
        int_v = _canon_stat_value(s.stats, "int")
        as_v = _canon_stat_value(s.stats, "as")
        crit_v = _canon_stat_value(s.stats, "crit")
        bap = _canon_stat_value(s.stats, "bap")
        ls_v = _canon_stat_value(s.stats, "ls")
        nlow = s.name.lower()
        # Global: Asclepius / Lifebinder only on real heal kits
        if _is_heal_core_item(s.name) and not _is_true_healer(bias):
            return False
        # Bancroft / Typhon / Gluttonous only on self-sustain mage kits
        if _is_mage_ls_core_item(s.name) and not _wants_mage_lifesteal(bias):
            return False
        # Not in live shop / removed (wiki may still list them)
        if _is_removed_or_unavailable_item(s.name):
            return False
        # God-specific (acorns, mods, …): owner only (Ratatoskr acorns)
        if is_god_specific_item(s) or is_god_specific_item(s.name):
            return item_allowed_for_god(s.name, god_name_gate)
        # Cross-type hard bans
        if physical and any(
            k in nlow
            for k in (
                "bancroft",
                "typhon",
                "soul gem",
                "soul reaver",
                "gluttonous",
                "tahuti",
                "obsidian shard",
                "spear of the magus",
                "spear of desolation",
                "book of thoth",
                "doom orb",
                "chronos' pendant",
                "gem of focus",
                "divine ruin",
                "rod of asclepius",
            )
        ):
            return False
        if mage and any(
            k in nlow
            for k in (
                "titan's bane",
                "bloodforge",
                "deathbringer",
                "demon blade",
                "riptalon",
                "musashi",
                "avenging blade",
                "executioner",
                "heartseeker",
                "jotunn",
                "hydra's",
                "tekko",
            )
        ):
            return False
        if physical and int_v >= 40 and str_v < 25:
            return False
        if mage and str_v >= 40 and int_v < 25:
            return False
        if role == "Support":
            if ls_v >= 5:
                return False
            # personal AS/crit toys are not support cores
            if (as_v >= 20 or crit_v >= 15 or bap >= 15) and _slot_label(s) == "power":
                return False
            if any(
                k in nlow
                for k in (
                    "chronos",
                    "gem of focus",
                    "soul reaver",
                    "tahuti",
                    "desolat",
                    "obsidian",
                    "spear of desolation",
                    "dreamer",
                    "wish-granting",
                    "deathbringer",
                )
            ):
                return False
            # Asclepius / Lifebinder only on real heal supports
            if _is_heal_core_item(s.name) and not _is_true_healer(bias):
                return False
            if int_v >= 55 and _canon_stat_value(s.stats, "hp") < 200 and (
                _canon_stat_value(s.stats, "pprot") + _canon_stat_value(s.stats, "mprot") < 20
            ):
                return False
            return True
        if role == "Solo":
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
            if any(
                k in nlow
                for k in (
                    "spectral",
                    "midgardian",
                    "thebes",
                    "chandra",
                    "phoenix",
                    "alchemist",
                    "pridwen",
                    "contagion",
                    # Mid-shell is Solo — high-SR "jungle" games often mis-role bruisers
                    "shifter",
                    "breastplate",
                    "genji",
                    "prophetic",
                    "oni hunter",
                    "leviathan",
                    "gladiator",
                    "dwarven",
                    "mantle of discord",
                    "magi's",
                )
            ):
                return False
            # Ability jungles: no ADC crit/AS toys unless true AA assassin
            arch = detect_archetype(bias, role, mage, physical)
            if arch != "aa_assassin":
                if _is_jungle_adc_toy(nlow) or "executioner" in nlow:
                    return False
            # Eye of the Storm / pure mid hybrid actives are not jungle openers
            if "eye of the storm" in nlow:
                return False
            return True
        if role == "Carry":
            if any(k in nlow for k in ("alchemist", "spectral", "phoenix", "thebes", "midgardian", "chandra")):
                return False
            # AA ADC: no solo/jungle ability cores
            if physical and aaish and any(
                k in nlow
                for k in (
                    "jotunn",
                    "hydra",
                    "crusher",
                    "runeforged",
                    "pendulum",
                    "gladiator",
                    "berserker",
                )
            ):
                return False
        if role == "Mid" and mage:
            # No heal-support openers / frontline shells as mid cores
            if any(
                k in nlow
                for k in (
                    "lifebinder",
                    "asclepius",
                    "thebes",
                    "spectral",
                    "phoenix",
                    "stampede",
                    "chandra",
                )
            ):
                return False
            # Soul Gem / Bancroft line — only real self-sustain kits (not every mid)
            if any(k in nlow for k in ("soul gem", "gluttonous", "bancroft", "typhon")):
                if not _wants_mage_lifesteal(bias) and "self_sustain" not in tags_kit:
                    return False
            # Luxury toys never as mid "cores" from pool noise
            if any(k in nlow for k in ("world stone", "cosmic horror")):
                return False
        if role == "Carry" and mage:
            if any(k in nlow for k in ("soul gem", "gluttonous")) and not _wants_mage_lifesteal(
                bias
            ):
                if "self_sustain" not in tags_kit and "dot" not in tags_kit:
                    return False
        if mage:
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
            return str_v >= 20 or as_v > 0 or s.item_type == "Defensive" or _canon_stat_value(s.stats, "hp") >= 250
        return True

    t3 = [s for s in t3 if kit_ok(s)]
    # Human ban list from kit_overrides.json
    bans = [b.lower() for b in (bias.get("ban_items") or [])]
    if bans:
        t3 = [s for s in t3 if not any(b in s.name.lower() for b in bans)]
    max_act = max_shop_actives_for_god(role, dtype, bias)

    # --- P4 Archetype + P5 Assemble slots ---
    items_6, archetype = assemble_kit_path(
        t3, bias, role, mage=mage, physical=physical, max_actives=max_act
    )
    # --- P6 Structural repair ---
    items_6 = _ensure_pen_in_path(
        items_6, t3, role, max_act, mage=mage, physical=physical
    )
    if role == "Jungle":
        items_6 = _normalize_jungle_path(
            items_6, t3, bias, mage=mage, physical=physical, max_actives=max_act
        )
        # Light god flavor after normalize (openers protected inside flex)
        items_6 = _god_flavor_flex(
            items_6,
            t3,
            str(bias.get("god_name") or ""),
            role,
            set(bias.get("tags") or []),
            mage=mage,
            physical=physical,
            max_actives=max_act,
        )
        # Re-cap openers if flavor reintroduced a 3rd stack item
        items_6 = _normalize_jungle_path(
            items_6, t3, bias, mage=mage, physical=physical, max_actives=max_act
        )
    if role in DAMAGE_ROLES_NEED_PEN:
        items_6 = _trim_excess_defense(items_6, t3, max_defense=1, max_actives=max_act)
    elif role in ("Solo", "Support"):
        # keep frontline bulk — no trim
        pass
    god_nm = str(bias.get("god_name") or god.get("entity_name") or "")
    # Owner-only lines (Ratatoskr acorns) — after structural repair, before inspire
    items_6 = _ensure_owned_god_items(
        items_6, t3, god_nm, max_actives=max_act, role=role
    )
    items_6 = _ensure_inspired_cores(
        items_6, t3, role, god_nm, mage=mage, physical=physical, max_actives=max_act
    )
    # Inspire can reintroduce shells on AA jungle — strip again
    if role == "Jungle":
        items_6 = _normalize_jungle_path(
            items_6, t3, bias, mage=mage, physical=physical, max_actives=max_act
        )
    # --- P7 Buy order (spike timing; high-SR avg_slot when available) ---
    items_6 = _order_buy_path(items_6, role, god_name=god_nm)
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
        items_6 = _order_buy_path(items_6, role, god_name=god_nm)
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
    effects = bias.get("effects") or extract_kit_effects(bias)
    effect_labs = bias.get("effect_labels") or effect_labels(effects)
    path_cards = _path_item_cards(items_6, bias, role)
    starter_why = None
    starter_card = None
    if starters:
        starter_why = explain_item_pick(
            starters[0].name,
            bias=bias,
            role=role,
            effects=effects,
            is_starter=True,
        )
        starter_card = _item_card(starters[0], why=starter_why)
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
        "kit_effects": effect_labs,
        "kit_effect_scores": effects,
        "is_aspect": bool(bias.get("is_aspect")),
        "aspect_name": bias.get("aspect_name"),
        "aspect_description": bias.get("aspect_description"),
        "aspect_id": bias.get("aspect_id"),
        "patch_trajectory": bias.get("trajectory"),
        "avg_str_scaling": round((bias.get("str") or 0) * 100, 1),
        "avg_int_scaling": round((bias.get("int") or 0) * 100, 1),
        "starter": starter_card,
        "items": path_cards,
        "full_path": path_cards,
        "inventory_slots": 7,
        "cores": _path_item_cards(cores[:4], bias, role),
        "defense": _path_item_cards(defs[:2], bias, role),
        "relics": [_item_card(r) for r in relics[:2]],
        "max_shop_actives": max_act,
        "hard_max_actives": HARD_MAX_ACTIVE_ITEMS,
        "active_count": n_act,
        "pen_total": round(pen_total, 1),
        "min_build_pen": MIN_BUILD_PEN,
        # --- P8 Explain (+ algorithm card for UI transparency) ---
        "algorithm": _algorithm_card(),
        "why": _explain_god_build(
            god, bias, role, items_6, starters, pen_total, n_act, max_act, archetype=archetype
        ),
    }


def _algorithm_card() -> dict[str, Any]:
    from .build_pipeline import algorithm_card

    return algorithm_card()


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


def _item_card(it: ScoredItem | None, why: str | None = None) -> dict | None:
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
    card = {
        "name": it.name,
        "score": round(it.role_score, 1),
        "cost": it.total_cost,
        "type": it.item_type or it.tier,
        "slot": _slot_label(it),
        "momentum": round(it.momentum, 2),
        "ladder_tier": it.ladder_tier,
        "ladder_rank": it.ladder_rank,
        "ladder_score": round(float(it.ladder_score or 0), 1) if it.ladder_score else None,
        "stats": {k: v for k, v in ordered[:5]},
        "pen": round(pen, 1) if pen else 0,
        "damp": round(_canon_stat_value(it.stats, "damp"), 1) or 0,
        "plat": round(_canon_stat_value(it.stats, "plat"), 1) or 0,
        "ten": round(_canon_stat_value(it.stats, "ten"), 1) or 0,
        "effect": (it.passive or it.active or "")[:180],
        "is_active": bool(it.is_active_item),
    }
    if why:
        card["why"] = why
    return card


def _path_item_cards(
    path: list[ScoredItem],
    bias: dict,
    role: str,
) -> list[dict]:
    """Attach per-item kit/effect why lines."""
    effects = bias.get("effects") or extract_kit_effects(bias)
    god_name = str(bias.get("god_name") or "")
    cards = []
    for it in path:
        why = explain_item_pick(
            it.name,
            bias=bias,
            role=role,
            effects=effects,
            slot_hint=_slot_label(it),
            is_pen=is_pen_item(it),
            is_active=bool(it.is_active_item),
        )
        t_boost, t_why = inspiration_boost(it.name, god_name=god_name, role=role)
        if t_boost >= 6 and t_why:
            why = f"{why}; inspired: {t_why}" if why else f"inspired: {t_why}"
        card = _item_card(it, why=why)
        if card:
            if t_boost >= 6:
                card["inspired"] = True
            cards.append(card)
    return cards


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
    insp_n = sum(
        1
        for it in path
        if inspiration_boost(it.name, god_name=str(bias.get("god_name") or ""), role=role)[0] >= 6
    )
    insp_note = (
        f" Soft high-SR inspiration on {insp_n} item(s) (tracker.gg — not a meta copy)."
        if insp_n
        else ""
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

    effects = bias.get("effects") or extract_kit_effects(bias)
    eff_labs = bias.get("effect_labels") or effect_labels(effects)
    eff_show = ", ".join(eff_labs[:6]) if eff_labs else "general kit"

    aspect_bit = ""
    if bias.get("is_aspect") and bias.get("aspect_name"):
        aspect_bit = f" ASPECT «{bias.get('aspect_name')}»."
        ad = (bias.get("aspect_description") or "")[:140]
        if ad:
            aspect_bit += f" {ad}"
    parts = [
        f"{god['entity_name']} · {role} · archetype «{arch}» ({power_style}).{aspect_bit}",
        f"Kit effects: {eff_show}.",
        f"Tags: {tag_show}.",
        f"Style {style}; patch {traj} (net {psc:+.1f}, r5 {r5:+.1f}).",
        f"Patch axes (r5): {axis_txt}.",
        f"Scale STR {(bias.get('str') or 0)*100:.0f}% / INT {(bias.get('int') or 0)*100:.0f}%.",
    ]
    if path:
        # First item why-style summary
        top_whys = []
        for p in path[:3]:
            top_whys.append(
                f"{p.name} ({explain_item_pick(p.name, bias=bias, role=role, effects=effects, is_pen=is_pen_item(p))})"
            )
        parts.append("Path: " + "; ".join(top_whys) + ".")
    pens = [p.name for p in path if is_pen_item(p)]
    if pens:
        parts.append("Pen: " + ", ".join(pens) + ".")
    parts.append(f"Actives {n_act}/{max_act} · pen ≈ {pen_total:.0f}.")
    if insp_note:
        parts.append(insp_note.strip())
    return " ".join(parts)


def quality_gate_builds(report: dict[str, Any]) -> dict[str, Any]:
    """
    Soft QA on exported paths: uniqueness, pen on damage roles, luxury cap.
    Returns summary attached to the report (does not fail hard).
    """
    summary: dict[str, Any] = {"roles": {}, "ok": True, "warnings": []}
    for role, data in (report.get("roles") or {}).items():
        gods = data.get("recommended_gods") or []
        paths: dict[tuple, list[str]] = {}
        pen_fail = []
        lux_fail = []
        for gb in gods:
            names = tuple(it["name"] for it in (gb.get("items") or []))
            paths.setdefault(names, []).append(gb.get("god") or "?")
            pen = float(gb.get("pen_total") or 0)
            if role in DAMAGE_ROLES_NEED_PEN and pen < MIN_BUILD_PEN:
                pen_fail.append(gb.get("god"))
            lux = [
                it["name"]
                for it in (gb.get("items") or [])
                if any(
                    k in (it.get("name") or "").lower()
                    for k in ("dreamer", "wish-granting", "parashu", "tahuti")
                )
            ]
            if len(lux) > 1:
                lux_fail.append(f"{gb.get('god')}:{lux}")
        unique = len(paths)
        total = len(gods)
        shared = {", ".join(v): list(k) for k, v in paths.items() if len(v) > 1}
        role_ok = unique >= max(1, total - 1) and not pen_fail and not lux_fail
        if not role_ok:
            summary["ok"] = False
        if shared:
            summary["warnings"].append(f"{role}: shared paths {list(shared.keys())}")
        if pen_fail:
            summary["warnings"].append(f"{role}: low pen {pen_fail}")
        if lux_fail:
            summary["warnings"].append(f"{role}: multi-luxury {lux_fail}")
        summary["roles"][role] = {
            "unique": unique,
            "total": total,
            "shared_groups": len(shared),
            "pen_fail": pen_fail,
            "luxury_fail": lux_fail,
        }
    return summary


def generate_all(conn: sqlite3.Connection, gods_per_role: int = 24) -> dict[str, Any]:
    items = load_items(conn)
    from .build_pipeline import algorithm_card

    report: dict[str, Any] = {
        "game": "SMITE 2",
        "mode": "Conquest",
        "algorithm": algorithm_card(),
        "method": (
            "Multi-phase Conquest algorithm (docs/BUILD_ALGORITHM.md): "
            "hard gates → role job → buy-order spikes → kit archetype slots → "
            "ladder/patch → soft high-SR inspiration → light flex diversify. "
            "God kit (effects/tags/scaling) + items:overall ladder + optional "
            "data/tracker_inspiration.json (nudge only). "
            "Hard bans: damage type, god-only items, healer cores, removed shop. "
            f"Shop actives ≤{DEFAULT_MAX_SHOP_ACTIVES} (hard max {HARD_MAX_ACTIVE_ITEMS}). "
            f"Damage roles ≥{MIN_BUILD_PEN:.0f} matching pen. "
            "Order is first-class: Mid Book/Deso before Obsidian; Carry Tyrfing/DG before Titan's; "
            "Jungle Jotunn before late pen; Support Thebes/Shifter before Spectral."
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
        god_builds = []
        for g in gods:
            b = build_god_build(conn, items, role, g)
            if b is not None:
                god_builds.append(b)
        # Carry: backfill more ranged/native carries if melee tier noise dropped rows
        if role == "Carry" and len(god_builds) < min(12, gods_per_role):
            extra = top_gods_for_role(conn, role, limit=gods_per_role * 2)
            seen = {x.get("god") or x.get("entity_name") for x in god_builds}
            for g in extra:
                nm = g.get("entity_name") or g.get("name")
                if nm in seen:
                    continue
                b = build_god_build(conn, items, role, g)
                if b is not None:
                    god_builds.append(b)
                    seen.add(nm)
                if len(god_builds) >= gods_per_role:
                    break
        report["roles"][role] = {
            "template": template,
            "recommended_gods": god_builds,
        }
    report["quality_gate"] = quality_gate_builds(report)
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
