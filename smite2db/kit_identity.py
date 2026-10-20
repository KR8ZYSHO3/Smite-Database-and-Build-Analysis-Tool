"""
Kit identity hooks — character-unique itemization from ability/aspect text.

Detects scaling/conversion hooks (item-HP scale, base-damage-only, permanent
Max HP, Plating/Dampening stacks, ally shield/heal, haunt shred, …) and
produces prefer/ban lists + numeric boosts so builds amplify the hook instead
of cloning role staples.

Used by base kits (god_scaling_bias) and aspects (build_aspect_bias).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

IDENTITY_LOCK_THRESHOLD = 0.55


@dataclass
class IdentityProfile:
    hooks: set[str] = field(default_factory=set)
    strength: float = 0.0
    prefer_items: list[str] = field(default_factory=list)
    ban_items: list[str] = field(default_factory=list)
    tags_add: set[str] = field(default_factory=set)
    tags_remove: set[str] = field(default_factory=set)
    power_penalty: float = 0.0
    bulk_boost: float = 0.0
    heal_boost: float = 0.0
    cdr_boost: float = 0.0
    hp_stack_boost: float = 0.0
    mid_enchanter: bool = False
    force_archetype: str | None = None

    @property
    def identity_lock(self) -> bool:
        return self.strength >= IDENTITY_LOCK_THRESHOLD


# (hook_id, regex, strength_add) — tight patterns; require conversion/scaling language
_HOOK_PATTERNS: list[tuple[str, re.Pattern[str], float]] = [
    (
        "base_damage_only",
        re.compile(
            r"only deal base damage with no scaling|no scaling|"
            r"base damage with no scaling|only deal base damage|"
            r"deal(?:s)? only base damage",
            re.I,
        ),
        0.85,
    ),
    (
        "item_hp_scale",
        re.compile(
            r"(?:damage )?scaling:\s*[\d.]+%\s*health from items|"
            r"scales? with item health|health from items|"
            r"% health from items|item health",
            re.I,
        ),
        0.8,
    ),
    (
        "max_hp_scale",
        re.compile(
            r"(?:bonus )?damage scaling:\s*[\d.]+%\s*(?:of )?(?:your )?max health|"
            r"(?:heal|bonus heal) scaling:\s*[\d.]+%\s*(?:of )?(?:your )?max health|"
            r"scaling with (?:your )?max health|"
            r"[\d.]+%\s*(?:of )?(?:your )?max health|"
            r"based on (?:your )?max health|"
            r"zombie damage scaling:\s*[\d.]+%\s*max health|"
            # Kuzenbo Water Bowl: mitigation stacks from Max HP taken
            r"[\d.]+%\s*per\s*[\d.]+%\s*of\s*max\s*hp|"
            r"max\s*hp\s*taken|"
            r"portion of (?:your )?(?:maximum|max) health as damage",
            re.I,
        ),
        0.75,
    ),
    (
        # Shell Spikes / thorns / reflect % of damage taken
        "damage_reflect",
        re.compile(
            r"damage reflected:\s*[\d.]+%|"
            r"reflect(?:ing|s)? a portion of damage|"
            r"reflect(?:s|ed)?\s*[\d.]+%\s*of\s*(?:damage|pre-mitigated)|"
            r"reflect(?:s|ing)? damage taken",
            re.I,
        ),
        0.7,
    ),
    (
        "permanent_max_hp",
        re.compile(
            r"permanent max health|provides permanent max health|"
            r"god kill health gain|npc kill health gain|"
            r"no longer heals?\s+\w+\s+but provides permanent",
            re.I,
        ),
        0.8,
    ),
    (
        "plat_damp_stack",
        re.compile(
            r"plating and dampening|plating.{0,40}dampening|"
            r"dampening.{0,40}plating|"
            r"0\.2 per combo.*(?:plat|damp)|per combo.{0,30}(?:plating|dampening)",
            re.I,
        ),
        0.85,
    ),
    (
        "ally_shield",
        re.compile(
            r"shields? (?:allied|ally|nearby allies)|"
            r"provide(?:s)? (?:yourself )?a health shield|"  # self-only handled separately
            r"shield(?:s)? allied gods|ally shield|"
            r"nearby allies gain a health shield|"
            r"shield health scaling:\s*[\d.]+%\s*intelligence",
            re.I,
        ),
        0.55,
    ),
    (
        "ally_heal",
        re.compile(
            r"heals? (?:all )?alli(?:es|ed)|heal all allied|"
            r"healing allies|heals allies|"
            r"attaching to them|"  # Ra Solar Blessing attach
            r"searing pain heals? allies|"
            r"greatly increased healing",
            re.I,
        ),
        0.6,
    ),
    (
        "haunt_shred",
        re.compile(
            r"\bhaunt(?:ed|s)?\b|wraith call|"
            r"strength and intelligence reduction|"
            r"protections? reduction",
            re.I,
        ),
        0.7,
    ),
    (
        "prot_shred_stack",
        re.compile(
            r"stacking (?:strength|intelligence|protections?).{0,40}reduction|"
            r"protections? reduction:\s*[\d.]+",
            re.I,
        ),
        0.55,
    ),
]

# Self-only shield language — do not treat as ally_shield enchanter
_SELF_SHIELD_ONLY = re.compile(
    r"provide yourself a health shield|self-only|stone shield is self-only",
    re.I,
)

_HOOK_PREFER: dict[str, list[str]] = {
    "base_damage_only": [
        "chronos",
        "asclepius",
        "lotus sickle",
        "thebes",
        "isolation",
        "heartwood",
        "genji",
        "breastplate",
    ],
    "item_hp_scale": [
        "ethereal",
        "contagion",
        "thebes",
        "isolation",
        "spectral",
        "prophetic",
        "gauntlet of thebes",
    ],
    "max_hp_scale": [
        "ethereal",
        "contagion",
        "thebes",
        "prophetic",
        "gladiator",
        "leviathan",
        "hide",
        "soul reaver",
        "shifter",
    ],
    "damage_reflect": [
        "hide of the nemean",
        "mystical",
        "contagion",
        "thebes",
        "midgardian",
        "prophetic",
        "shifter",
        "gladiator",
    ],
    "permanent_max_hp": [
        "contagion",
        "gladiator",
        "leviathan",
        "hide",
        "shifter",
        "mystical",
        "bloodforge",
    ],
    "plat_damp_stack": [
        "shifter",
        "mystical",
        "spectral",
        "alchemist",
        "breastplate",
        "runeforged",
        "radiant bulwark",
        "mantle",
    ],
    "ally_shield": [
        "lotus sickle",
        "asclepius",
        "phoenix",
        "pridwen",
        "thebes",
        "heartwood",
        "chronos",
    ],
    "ally_heal": [
        "lotus sickle",
        "asclepius",
        "heartwood",
        "chronos",
        "thebes",
        "isolation",
    ],
    "haunt_shred": [
        "binding",
        "isolation",
        "ethereal",
        "thebes",
        "contagion",
        "prophetic",
        "chronos",
        "soul reaver",
    ],
    "prot_shred_stack": [
        "binding",
        "isolation",
        "magus",
        "void",
        "ethereal",
    ],
}

_HOOK_BAN: dict[str, list[str]] = {
    "base_damage_only": [
        "tahuti",
        "dreamer",
        "thoth",
        "doom orb",
        "soul reaver",
        "obsidian",
        "polynomicon",
    ],
    "item_hp_scale": [
        "deathbringer",
        "tyrfing",
        "riptalon",
        "demon blade",
    ],
    "max_hp_scale": [
        "tahuti",
        "dreamer",
        "polynomicon",
        "lotus sickle",
        "asclepius",
    ],
    "damage_reflect": [
        "tahuti",
        "dreamer",
        "thoth",
        "doom orb",
        "polynomicon",
        "deathbringer",
        "riptalon",
    ],
    "permanent_max_hp": [
        "lotus sickle",
        "asclepius",
        "chandra",
    ],
    "plat_damp_stack": [
        "tahuti",
        "deathbringer",
        "tyrfing",
        "obsidian shard",
        "titan's bane",
    ],
    "ally_shield": [
        "tahuti",
        "desolat",
        "doom orb",
        "thoth",
    ],
    "ally_heal": [
        "tahuti",
        "dreamer",
        "thoth",
        "doom orb",
        "obsidian",
    ],
    "haunt_shred": [
        "lotus sickle",
        "asclepius",
        "chandra",
        "polynomicon",
        "deathbringer",
        "riptalon",
        "tahuti",
        "dreamer",
        "obsidian",
    ],
    "prot_shred_stack": [
        "lotus sickle",
        "asclepius",
    ],
}

_HOOK_TAGS_ADD: dict[str, set[str]] = {
    "base_damage_only": {"heal", "team_buff", "aspect_utility", "spam"},
    "item_hp_scale": {"hybrid_bulk", "aa", "team_buff"},
    "max_hp_scale": {"hybrid_bulk", "self_sustain"},
    "damage_reflect": {"hybrid_bulk", "self_sustain", "anti_cc"},
    "permanent_max_hp": {"hybrid_bulk", "self_sustain", "execute"},
    "plat_damp_stack": {"hybrid_bulk", "self_sustain", "anti_cc"},
    "ally_shield": {"heal", "team_buff", "shield", "heavy_heal"},
    "ally_heal": {"heal", "team_buff", "heavy_heal"},
    "haunt_shred": {"hybrid_bulk", "prot_shred", "spam", "dot", "hard_cc"},
    "prot_shred_stack": {"prot_shred", "dot"},
}

_HOOK_TAGS_REMOVE: dict[str, set[str]] = {
    "base_damage_only": {"burst", "ult_nuke", "mana_stack"},
    "item_hp_scale": {"burst"},
    "max_hp_scale": {"burst", "ult_nuke"},
    "damage_reflect": {"burst", "ult_nuke", "aa", "as_steroid"},
    "haunt_shred": {"burst", "ult_nuke", "aa", "as_steroid", "heal", "team_buff", "heavy_heal"},
}


def detect_identity_hooks(blob: str, *, is_aspect: bool = False) -> IdentityProfile:
    """Scan kit/aspect text for identity hooks."""
    text = blob or ""
    prof = IdentityProfile()
    if not text.strip():
        return prof

    for hook_id, cre, strength_add in _HOOK_PATTERNS:
        if not cre.search(text):
            continue
        # Ally shield: ignore pure self-only Stone Shield style unless also ally language
        if hook_id == "ally_shield" and _SELF_SHIELD_ONLY.search(text):
            if not re.search(r"allied|allies|nearby allies", text, re.I):
                continue
        prof.hooks.add(hook_id)
        prof.strength = min(1.0, prof.strength + strength_add)

    # Base kits: dampen strength so weak text matches don't lock every god
    if not is_aspect and prof.strength > 0:
        prof.strength *= 0.72

    for h in prof.hooks:
        for p in _HOOK_PREFER.get(h, []):
            if p not in prof.prefer_items:
                prof.prefer_items.append(p)
        for b in _HOOK_BAN.get(h, []):
            if b not in prof.ban_items:
                prof.ban_items.append(b)
        prof.tags_add |= _HOOK_TAGS_ADD.get(h, set())
        prof.tags_remove |= _HOOK_TAGS_REMOVE.get(h, set())

    if "base_damage_only" in prof.hooks:
        prof.power_penalty = max(prof.power_penalty, 0.4)
        prof.heal_boost = max(prof.heal_boost, 0.45)
        prof.cdr_boost = max(prof.cdr_boost, 0.35)
        prof.mid_enchanter = True
    if "ally_heal" in prof.hooks and (
        "base_damage_only" in prof.hooks
        or "ally_shield" in prof.hooks
        or re.search(r"no longer deal damage|no longer deals? damage", text, re.I)
    ):
        prof.mid_enchanter = True
        prof.heal_boost = max(prof.heal_boost, 0.4)
        prof.power_penalty = max(prof.power_penalty, 0.3)
    if "ally_shield" in prof.hooks and re.search(
        r"no longer deal damage|shields? allied|80%\s*intelligence", text, re.I
    ):
        prof.mid_enchanter = True
        prof.heal_boost = max(prof.heal_boost, 0.35)
        prof.power_penalty = max(prof.power_penalty, 0.25)
    if "item_hp_scale" in prof.hooks:
        prof.hp_stack_boost = max(prof.hp_stack_boost, 0.55)
        prof.bulk_boost = max(prof.bulk_boost, 0.35)
        prof.power_penalty = max(prof.power_penalty, 0.15)
    if "max_hp_scale" in prof.hooks or "permanent_max_hp" in prof.hooks:
        prof.hp_stack_boost = max(prof.hp_stack_boost, 0.5)
        prof.bulk_boost = max(prof.bulk_boost, 0.4)
    if "damage_reflect" in prof.hooks:
        prof.hp_stack_boost = max(prof.hp_stack_boost, 0.45)
        prof.bulk_boost = max(prof.bulk_boost, 0.45)
        prof.power_penalty = max(prof.power_penalty, 0.2)
    if "plat_damp_stack" in prof.hooks:
        prof.bulk_boost = max(prof.bulk_boost, 0.45)
        prof.hp_stack_boost = max(prof.hp_stack_boost, 0.25)
    if "haunt_shred" in prof.hooks or "prot_shred_stack" in prof.hooks:
        prof.bulk_boost = max(prof.bulk_boost, 0.4)
        prof.power_penalty = max(prof.power_penalty, 0.25)
        prof.cdr_boost = max(prof.cdr_boost, 0.25)
        # shred kits are NOT enchanters
        prof.mid_enchanter = False
        for b in ("lotus sickle", "asclepius", "chandra"):
            if b not in prof.ban_items:
                prof.ban_items.append(b)

    # Mid enchanter requires enough strength
    if prof.mid_enchanter and prof.strength < 0.5:
        prof.mid_enchanter = False

    return prof


# Base-kit AA noise that steals prefer-inject slots under HP identity
_AA_PREFER_NOISE = (
    "riptalon",
    "ichival",
    "wind",
    "deathbringer",
    "musashi",
    "avenging",
    "eros",
    "demon blade",
    "death metal",
)


def apply_identity_to_bias(bias: dict[str, Any], prof: IdentityProfile) -> dict[str, Any]:
    """Merge IdentityProfile into a kit bias dict."""
    out = dict(bias)
    tags = set(out.get("tags") or [])
    tags |= prof.tags_add
    tags -= prof.tags_remove
    out["tags"] = tags

    ban = list(out.get("ban_items") or [])
    for b in prof.ban_items:
        if b not in ban:
            ban.append(b)

    existing = list(out.get("prefer_items") or [])
    identity_prefers = list(prof.prefer_items)

    def _banned_prefer(p: str) -> bool:
        pl = (p or "").lower()
        return any(b and b in pl for b in (x.lower() for x in ban))

    def _aa_noise(p: str) -> bool:
        pl = (p or "").lower()
        return any(k in pl for k in _AA_PREFER_NOISE)

    # Identity lock: identity prefers FIRST so inject slots are not eaten by
    # base AA staples (riptalon/wind) before Ethereal/Contagion/Thebes.
    if prof.identity_lock and identity_prefers:
        prefer: list[str] = []
        for p in identity_prefers + existing:
            if _banned_prefer(p):
                continue
            if "item_hp_scale" in prof.hooks and _aa_noise(p):
                continue
            if p not in prefer:
                prefer.append(p)
    else:
        prefer = list(existing)
        for p in identity_prefers:
            if p not in prefer and not _banned_prefer(p):
                prefer.append(p)

    out["prefer_items"] = prefer
    out["ban_items"] = ban

    out["identity_hooks"] = sorted(prof.hooks)
    out["identity_lock"] = bool(prof.identity_lock)
    out["identity_strength"] = float(prof.strength)
    out["mid_enchanter"] = bool(prof.mid_enchanter)

    # Numeric boosts — take max with any existing aspect_* fields
    out["aspect_power_penalty"] = max(
        float(out.get("aspect_power_penalty") or 0), prof.power_penalty
    )
    out["aspect_bulk_boost"] = max(float(out.get("aspect_bulk_boost") or 0), prof.bulk_boost)
    out["aspect_heal_boost"] = max(float(out.get("aspect_heal_boost") or 0), prof.heal_boost)
    out["aspect_cdr_boost"] = max(float(out.get("aspect_cdr_boost") or 0), prof.cdr_boost)
    out["identity_hp_stack"] = max(float(out.get("identity_hp_stack") or 0), prof.hp_stack_boost)

    if prof.power_penalty >= 0.2:
        sb = float(out.get("style_burst") or 0.5)
        out["style_burst"] = max(0.15, sb - 0.2)
        tags.discard("burst")
        tags.discard("ult_nuke")
        out["tags"] = tags
    if prof.cdr_boost >= 0.2:
        tags.add("spam")
        tags.discard("long_cd")
        out["tags"] = tags
        out["avg_cd"] = min(float(out.get("avg_cd") or 12), 7.5)

    if prof.force_archetype and not out.get("force_archetype"):
        out["force_archetype"] = prof.force_archetype

    return out


def identity_item_score_delta(item_name: str, bias: dict[str, Any]) -> float:
    """Extra score from identity hooks (works for base + aspect)."""
    hooks = set(bias.get("identity_hooks") or [])
    if not hooks and not bias.get("identity_lock"):
        # Still apply numeric boosts if set without hook list
        if not any(
            float(bias.get(k) or 0) > 0
            for k in (
                "aspect_power_penalty",
                "aspect_bulk_boost",
                "aspect_heal_boost",
                "identity_hp_stack",
            )
        ):
            return 0.0

    n = (item_name or "").lower()
    s = 0.0
    pen = float(bias.get("aspect_power_penalty") or 0)
    bulk = float(bias.get("aspect_bulk_boost") or 0)
    heal = float(bias.get("aspect_heal_boost") or 0)
    cdr = float(bias.get("aspect_cdr_boost") or 0)
    hp_stack = float(bias.get("identity_hp_stack") or 0)
    lock = bool(bias.get("identity_lock"))

    if pen >= 0.2:
        glass = ("tahuti", "dreamer", "obsidian", "desolat", "polynomicon", "thoth", "doom orb")
        if bulk < 0.3 and "haunt_shred" not in hooks and "max_hp_scale" not in hooks:
            glass = glass + ("soul reaver",)
        if any(k in n for k in glass):
            s -= (55 if lock else 40) * pen
        if any(k in n for k in ("asclepius", "lotus sickle", "thebes", "chronos", "heartwood", "isolation")):
            s += (40 if lock else 30) * pen

    if cdr >= 0.2:
        if any(k in n for k in ("chronos", "genji", "breastplate", "valor", "pendant", "heartwood")):
            s += 32 if lock else 24

    if heal >= 0.2:
        if any(k in n for k in ("asclepius", "lotus sickle", "heartwood", "thebes", "lifebinder")):
            s += 40 if lock else 28

    if bulk >= 0.3 or hp_stack >= 0.3:
        if any(
            k in n
            for k in (
                "ethereal",
                "shifter",
                "thebes",
                "prophetic",
                "isolation",
                "binding",
                "contagion",
                "gladiator",
                "leviathan",
                "mystical",
                "spectral",
                "alchemist",
                "soul reaver",
                "hide",
                "radiant bulwark",
                "runeforged",
            )
        ):
            s += 38 if lock else 28
        if any(k in n for k in ("tahuti", "dreamer", "obsidian", "polynomicon", "deathbringer", "tyrfing")):
            s -= 30 if lock else 20

    if hp_stack >= 0.4:
        # Prefer raw HP / Ethereal-class; soft-penalize pure crit openers
        if any(k in n for k in ("ethereal", "contagion", "thebes", "isolation")):
            s += 22
        if any(k in n for k in ("deathbringer", "riptalon", "tyrfing", "demon blade")):
            s -= 35

    if "plat_damp_stack" in hooks:
        if any(k in n for k in ("spectral", "alchemist", "radiant bulwark", "mystical", "mantle")):
            s += 42
        if any(k in n for k in ("tahuti", "obsidian", "titan")):
            s -= 35

    if "permanent_max_hp" in hooks:
        if any(k in n for k in ("contagion", "gladiator", "leviathan", "hide", "mystical")):
            s += 40
        if any(k in n for k in ("tyrfing", "hydras", "jotunn")) and "bloodforge" not in n:
            # Keep gap tools but don't let them erase HP identity as sole cores
            s -= 8

    if bias.get("mid_enchanter"):
        if any(k in n for k in ("lotus sickle", "asclepius", "heartwood", "chronos", "thebes")):
            s += 48
        if any(k in n for k in ("thoth", "doom orb", "tahuti", "dreamer", "desolat")):
            s -= 50

    return s


def identity_fights_item(item_name: str, bias: dict[str, Any]) -> bool:
    """True when an inspired staple should be skipped under identity_lock."""
    if not bias.get("identity_lock"):
        return False
    n = (item_name or "").lower()
    for b in bias.get("ban_items") or []:
        if str(b).lower() in n:
            return True
    hooks = set(bias.get("identity_hooks") or [])
    if "base_damage_only" in hooks or bias.get("mid_enchanter"):
        if any(k in n for k in ("thoth", "doom orb", "tahuti", "dreamer", "desolat", "obsidian")):
            return True
    if "item_hp_scale" in hooks:
        if any(k in n for k in ("deathbringer", "tyrfing", "riptalon", "demon blade")):
            return True
    if "haunt_shred" in hooks or "max_hp_scale" in hooks:
        if any(k in n for k in ("tahuti", "dreamer", "obsidian", "lotus sickle", "asclepius")):
            return True
    if "plat_damp_stack" in hooks:
        if any(k in n for k in ("tahuti", "tyrfing", "deathbringer", "obsidian", "titan")):
            return True
    return False
