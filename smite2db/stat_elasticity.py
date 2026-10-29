"""
Stat elasticity — kit payoff axes without named hooks.

Parses ability/aspect text (+ known identity hooks) into a small map of
which stats move fight value. Items are scored by how much of those axes
they deliver. Role staples are softened by identity_strength so Thebes-style
meta bonuses cannot outvote a locked axis.

Used by conquest_builds.rescore_for_god and slot meta bonuses.
"""

from __future__ import annotations

import re
from typing import Any

# Axes the optimizer understands
ELASTIC_AXES = (
    "max_mana",
    "max_hp",
    "item_hp",
    "item_prot",
    "int_power",
    "str_power",
    "cdr",
    "lifesteal",
    "pen",
    "heal_amp",
)

# Hook → default elasticity (merged with text parse)
_HOOK_ELASTICITY: dict[str, dict[str, float]] = {
    "max_mana_scale": {"max_mana": 1.0, "int_power": 0.35, "cdr": 0.15},
    "item_hp_scale": {"item_hp": 1.0, "max_hp": 0.55, "item_prot": 0.25},
    "max_hp_scale": {"max_hp": 1.0, "item_hp": 0.45, "item_prot": 0.2},
    "permanent_max_hp": {"max_hp": 0.9, "item_hp": 0.5, "item_prot": 0.25},
    "damage_reflect": {"max_hp": 0.7, "item_prot": 0.55, "item_hp": 0.35, "cdr": 0.2},
    "item_prot_cc": {"item_prot": 1.0, "max_hp": 0.35, "cdr": 0.25},
    "plat_damp_stack": {"item_prot": 0.7, "max_hp": 0.4, "cdr": 0.15},
    "spirit_lifesteal": {"lifesteal": 1.0, "int_power": 0.45, "item_prot": 0.35, "cdr": 0.2},
    "base_damage_only": {"heal_amp": 0.9, "cdr": 0.55, "item_prot": 0.35},
    "ally_heal": {"heal_amp": 0.85, "cdr": 0.35, "max_hp": 0.2},
    "ally_shield": {"heal_amp": 0.7, "item_prot": 0.35, "cdr": 0.25},
    "haunt_shred": {"max_hp": 0.55, "item_prot": 0.4, "pen": 0.35, "cdr": 0.25},
    "prot_shred_stack": {"pen": 0.7, "int_power": 0.3},
}

# Text patterns that add elasticity even without a named hook
_TEXT_AXIS_PATTERNS: list[tuple[str, re.Pattern[str], float]] = [
    (
        "max_mana",
        re.compile(
            r"scales? (?:from|with) (?:your )?max mana|"
            r"sclaes with max mana|"
            r"[\d.]+%\s*(?:of )?(?:your )?max mana|"
            r"based on (?:your )?max mana|"
            r"immediately provide(?:s)? max mana",
            re.I,
        ),
        0.9,
    ),
    (
        "max_hp",
        re.compile(
            r"scales? (?:from|with) (?:your )?max health|"
            r"[\d.]+%\s*(?:of )?(?:your )?max health|"
            r"based on (?:your )?max health|"
            r"portion of (?:your )?(?:maximum|max) health",
            re.I,
        ),
        0.85,
    ),
    (
        "item_hp",
        re.compile(
            r"health from items|item health|%\s*health from items|"
            r"scaling:\s*[\d.]+%\s*health from items",
            re.I,
        ),
        0.9,
    ),
    (
        "item_prot",
        re.compile(
            r"per\s*[\d.]+\s*item\s*protections?|"
            r"item protections?",
            re.I,
        ),
        0.8,
    ),
    (
        "lifesteal",
        re.compile(
            r"lifesteal for each|gain [\d.]+%\s*lifesteal|"
            r"orbiting kappa|spawn orbiting kappa",
            re.I,
        ),
        0.85,
    ),
    (
        "heal_amp",
        re.compile(
            r"increased healing|healing allies|heals? (?:all )?alli|"
            r"only deal base damage|no scaling",
            re.I,
        ),
        0.7,
    ),
    (
        "pen",
        re.compile(
            r"protections? reduction|penetrat|haunt|"
            r"strength and intelligence reduction",
            re.I,
        ),
        0.55,
    ),
]


def detect_stat_elasticity(
    blob: str,
    *,
    hooks: set[str] | list[str] | None = None,
) -> dict[str, float]:
    """Return axis → weight in [0, 1+]. Empty when no signal."""
    out: dict[str, float] = {}
    text = blob or ""
    hs = set(hooks or [])

    for h in hs:
        for axis, w in _HOOK_ELASTICITY.get(h, {}).items():
            out[axis] = max(out.get(axis, 0.0), float(w))

    for axis, cre, w in _TEXT_AXIS_PATTERNS:
        if cre.search(text):
            out[axis] = max(out.get(axis, 0.0), float(w))

    # Normalize so the top axis is 1.0 (keeps score scale stable)
    if not out:
        return {}
    peak = max(out.values()) or 1.0
    return {k: round(v / peak, 4) for k, v in out.items() if v > 0.05}


def staple_soft_factor(identity_strength: float | None, *, locked: bool = False) -> float:
    """
    Multiply role-meta bonuses (Thebes +160 etc.).

    At identity_strength 0 → 1.0 (full meta).
    At 0.85 lock → ~0.15 so staples cannot erase the kit axis.
    """
    s = float(identity_strength or 0.0)
    if locked and s < 0.55:
        s = 0.55
    if s <= 0:
        return 1.0
    return max(0.12, 1.0 - s)


def ladder_identity_factor(identity_strength: float | None, *, locked: bool = False) -> float:
    """Extra ladder mute under identity (on top of sample weight)."""
    return staple_soft_factor(identity_strength, locked=locked)


def inspire_identity_factor(identity_strength: float | None, *, locked: bool = False) -> float:
    """Mute tracker inspire under strong identity."""
    base = staple_soft_factor(identity_strength, locked=locked)
    # Inspire is already soft — keep a little room for agreeing openers
    return max(0.08, base * 0.85)


def item_elasticity_score(
    *,
    item_name: str,
    stats: dict[str, Any] | None,
    elasticity: dict[str, float] | None,
    identity_lock: bool = False,
) -> float:
    """
    Score an item by how well its stats match kit elasticity.

    stats keys use conquest canonical names (mp, hp, int, str, …) when available.
    """
    el = elasticity or {}
    if not el:
        return 0.0

    n = (item_name or "").lower()
    st = stats or {}

    def _stat(*keys: str) -> float:
        for k in keys:
            v = st.get(k)
            if v is None:
                continue
            try:
                return float(v)
            except (TypeError, ValueError):
                continue
        return 0.0

    mp = _stat("mp", "max mana", "mana")
    hp = _stat("hp", "max health", "health")
    pprot = _stat("pprot", "physical protection")
    mprot = _stat("mprot", "magical protection")
    int_v = _stat("int", "intelligence")
    str_v = _stat("str", "strength")
    cdr = _stat("cdr", "cooldown")
    ls = _stat("ls", "lifesteal")
    pen = _stat("pen", "penetration")
    prots = pprot + mprot

    # Named packages that are pure axis carriers
    name_bonus = 0.0
    if el.get("max_mana", 0) >= 0.4 and any(k in n for k in ("thoth", "doom orb", "transcend", "yogi")):
        name_bonus += 28 * el["max_mana"]
    if el.get("item_hp", 0) >= 0.4 or el.get("max_hp", 0) >= 0.4:
        if any(k in n for k in ("ethereal", "contagion", "thebes", "gladiator", "leviathan", "hide")):
            name_bonus += 24 * max(el.get("item_hp", 0), el.get("max_hp", 0))
    if el.get("item_prot", 0) >= 0.4 and any(
        k in n for k in ("thebes", "breastplate", "genji", "contagion", "spectral", "prophetic", "binding")
    ):
        name_bonus += 22 * el["item_prot"]
    if el.get("lifesteal", 0) >= 0.4 and any(
        k in n for k in ("gluttonous", "bancroft", "soul gem", "umbral", "typhon")
    ):
        name_bonus += 26 * el["lifesteal"]
    if el.get("heal_amp", 0) >= 0.4 and any(
        k in n for k in ("asclepius", "lotus sickle", "heartwood", "lifebinder")
    ):
        name_bonus += 26 * el["heal_amp"]

    # Continuous stat contribution (normalized roughly to T3 item ranges)
    s = 0.0
    s += el.get("max_mana", 0) * (mp / 50.0) * 4.5
    s += el.get("max_hp", 0) * (hp / 50.0) * 3.5
    s += el.get("item_hp", 0) * (hp / 50.0) * 4.0
    s += el.get("item_prot", 0) * (prots / 20.0) * 4.0
    s += el.get("int_power", 0) * (int_v / 15.0) * 3.0
    s += el.get("str_power", 0) * (str_v / 15.0) * 3.0
    s += el.get("cdr", 0) * (cdr / 5.0) * 3.5
    s += el.get("lifesteal", 0) * (ls / 5.0) * 4.0
    s += el.get("pen", 0) * (pen / 5.0) * 3.5
    # Heal amp has no direct stat — name_bonus carries it
    s += name_bonus

    if identity_lock and el:
        s *= 1.15

    # Soft-penalize pure glass when elasticity is bulk/mana/prot
    bulk_el = max(el.get("max_hp", 0), el.get("item_hp", 0), el.get("item_prot", 0), el.get("max_mana", 0))
    if bulk_el >= 0.5 and any(k in n for k in ("tahuti", "dreamer", "wish-granting", "deathbringer")):
        if "max_mana" not in el or el.get("max_mana", 0) < 0.4:
            s -= 35 * bulk_el
        elif any(k in n for k in ("tahuti", "dreamer", "wish-granting")):
            s -= 40 * bulk_el

    return round(s, 2)


def apply_elasticity_to_bias(bias: dict[str, Any], blob: str = "") -> dict[str, Any]:
    """Attach / merge stat_elasticity onto a kit bias dict."""
    out = dict(bias)
    hooks = set(out.get("identity_hooks") or [])
    text = blob or str(out.get("ability_blob") or "") + " " + str(out.get("full_blob") or "")
    # Prefer aspect description when present
    text = (
        str(out.get("aspect_description") or "")
        + " "
        + text
        + " "
        + str(out.get("kit_text") or "")
    )
    el = detect_stat_elasticity(text, hooks=hooks)
    prev = dict(out.get("stat_elasticity") or {})
    for k, v in el.items():
        prev[k] = max(float(prev.get(k) or 0), float(v))
    if prev:
        peak = max(prev.values()) or 1.0
        out["stat_elasticity"] = {k: round(v / peak, 4) for k, v in prev.items()}
    return out
