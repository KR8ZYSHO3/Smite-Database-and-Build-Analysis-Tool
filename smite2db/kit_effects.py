"""
Structured kit effects → item family matching + per-item "why" lines.

Builds on god_scaling_bias tags/metrics; does not re-scrape. Used by
conquest_builds for scoring boosts and explainability.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

# Effect id → human label + how we detect it from tags/metrics/text
EFFECT_META: dict[str, dict[str, Any]] = {
    "multi_hit": {"label": "multi-hit / ticks", "families": ["magus", "isolation", "desolation"]},
    "dot": {"label": "damage over time", "families": ["magus", "isolation", "divine", "contagion"]},
    "prot_shred": {"label": "protection shred", "families": ["magus", "executioner", "desolation", "void"]},
    "channel": {"label": "channel / cast time", "families": ["chronos", "focus", "desolation", "myrddin"]},
    "ult_nuke": {"label": "big ult spike", "families": ["obsidian", "titan", "soul_reaver", "tahuti", "desolation"]},
    "burst": {"label": "burst combos", "families": ["desolation", "obsidian", "titan", "soul_reaver", "heartseeker"]},
    "spam": {"label": "low cooldowns", "families": ["chronos", "cdr_def", "focus", "pendant"]},
    "aa": {"label": "basic-attack kit", "families": ["as_crit", "onhit", "ls"]},
    "as_steroid": {"label": "attack-speed steroid", "families": ["as_crit", "onhit"]},
    "mana_stack": {"label": "mana → power passive", "families": ["mana"]},
    "self_sustain": {"label": "self heal / drain", "families": ["lifesteal", "bancroft"]},
    "heal": {"label": "healing in kit", "families": ["heal_item", "lifesteal", "antiheal"]},
    "heavy_heal": {"label": "heavy healing", "families": ["heal_item", "antiheal"]},
    "execute": {"label": "execute / threshold", "families": ["soul_reaver", "bloodforge", "obsidian"]},
    "shield": {"label": "shields", "families": ["shield_item", "hybrid_bulk"]},
    "zone": {"label": "zones / linger", "families": ["isolation", "magus", "soul_gem"]},
    "pet_zone": {"label": "pet / deployable", "families": ["isolation", "magus", "soul_gem"]},
    "hard_cc": {"label": "hard crowd control", "families": ["isolation", "binding", "cdr_def"]},
    "high_cc": {"label": "lots of CC", "families": ["isolation", "binding", "cdr_def"]},
    "immobile": {"label": "low mobility", "families": ["bulk", "magi", "defense_cdr"]},
    "mobile": {"label": "high mobility", "families": ["gap", "pen"]},
    "gap_close": {"label": "dash / leap engage", "families": ["gap", "pen"]},
    # team_buff alone must NOT pull heal amp (Asclepius/Lifebinder) — only real heal kits do
    "team_buff": {"label": "ally buffs / auras", "families": ["aura"]},
    "anti_cc": {"label": "CC immunity in kit", "families": ["magi", "tenacity"]},
    "sustained": {"label": "sustained DPS", "families": ["cdr_def", "chronos", "ls"]},
    "long_cd": {"label": "long cooldowns", "families": ["power", "pen", "ult_finisher"]},
}

# Item name substrings → family id (first match wins when scoring)
ITEM_TO_FAMILY: list[tuple[str, str]] = [
    ("magus", "magus"),
    ("isolation", "isolation"),
    ("divine ruin", "divine"),
    ("divine", "divine"),
    ("contagion", "contagion"),
    ("desolat", "desolation"),
    ("obsidian", "obsidian"),
    ("titan", "titan"),
    ("soul reaver", "soul_reaver"),
    ("tahuti", "tahuti"),
    ("dreamer", "luxury_active"),
    ("wish-granting", "luxury_passive"),
    ("parashu", "luxury_active"),
    ("chronos", "chronos"),
    ("gem of focus", "focus"),
    ("myrddin", "myrddin"),
    ("book of thoth", "mana"),
    ("doom orb", "mana"),
    ("transcend", "mana"),
    ("pendant of the", "pendant"),
    ("bancroft", "bancroft"),
    ("typhon", "bancroft"),
    ("gluttonous", "lifesteal"),
    ("bloodforge", "bloodforge"),
    ("devourer", "ls"),
    ("soul gem", "soul_gem"),
    ("asclepius", "heal_item"),
    ("lifebinder", "heal_item"),
    ("executioner", "executioner"),
    ("riptalon", "as_crit"),
    ("deathbringer", "as_crit"),
    ("demon blade", "as_crit"),
    ("avenging", "as_crit"),
    ("musashi", "as_crit"),
    ("wind demon", "as_crit"),
    ("qins", "onhit"),
    ("ichival", "as_crit"),
    ("jotunn", "gap"),
    ("hydra", "gap"),
    ("arondight", "gap"),
    ("heartseeker", "heartseeker"),
    ("thebes", "aura"),
    ("chandra", "aura"),
    ("sovereign", "aura"),
    ("heartward", "aura"),
    ("providence", "aura"),
    ("spectral", "anti_crit"),
    ("midgardian", "anti_as"),
    ("nemean", "anti_crit"),
    ("genji", "defense_cdr"),
    ("breastplate", "cdr_def"),
    ("valor", "cdr_def"),
    ("magi", "magi"),
    ("mantle", "tenacity"),
    ("alchemist", "tenacity"),
    ("prophetic", "tenacity"),
    ("stygian", "peel"),
    ("pridwen", "shield_item"),
    ("phoenix", "shield_item"),
    ("shifter", "hybrid_bulk"),
    ("binding", "binding"),
    ("freya", "bulk"),
    ("hussar", "bulk"),
    ("oni hunter", "mprot"),
    ("pestilence", "antiheal"),
    ("brawler", "antiheal"),
    ("void shield", "void"),
    ("void", "void"),
]

# Family → default why fragment when matched via kit effect
FAMILY_WHY: dict[str, str] = {
    "magus": "multi-hit / shred — stacks Magus passive",
    "isolation": "zones & CC — Isolation slow/shred value",
    "divine": "anti-heal + pen for healing/sustain kits",
    "contagion": "team anti-heal aura",
    "desolation": "flat pen + CDR for ability burst",
    "obsidian": "% pen for magical tanks / late fights",
    "titan": "% pen for physical tanks / late fights",
    "soul_reaver": "big ability hits / execute spikes",
    "tahuti": "late INT power spike",
    "luxury_active": "On-Use power finisher (active budget)",
    "luxury_passive": "expensive hybrid power/HP finisher",
    "chronos": "CDR core for spam / channel kits",
    "focus": "ability CDR / focus passive",
    "myrddin": "double-cast / high INT ability core",
    "mana": "mana stack → power scaling",
    "pendant": "mana + CDR hybrid",
    "bancroft": "self-sustain power (missing HP)",
    "lifesteal": "sustain / omnivamp line",
    "bloodforge": "lifesteal + power for execute/bruiser",
    "ls": "lifesteal stacking",
    "soul_gem": "ability heal/proc for mages",
    "heal_item": "heal amp / team sustain",
    "executioner": "AA prot shred",
    "as_crit": "attack speed / crit carry core",
    "onhit": "on-hit / AS hybrid",
    "gap": "CDR + pen for gank/engage",
    "heartseeker": "stacking pen power for assassins",
    "aura": "team aura / support core",
    "anti_crit": "mitigate enemy crit (Spectral line)",
    "anti_as": "cut enemy attack speed",
    "defense_cdr": "magic prot + CDR for mages",
    "cdr_def": "physical CDR defense",
    "magi": "absorb CC (Magi's)",
    "tenacity": "tenacity / anti-CC bulk",
    "peel": "peel / anti-dive anchor",
    "shield_item": "shield / phoenix-style bulk",
    "hybrid_bulk": "offline hybrid tank",
    "binding": "Stone of Binding — CC setup shred",
    "bulk": "raw protections / HP",
    "mprot": "pure magical defense",
    "antiheal": "healing reduction",
    "void": "void shred line",
    "power": "raw power",
    "pen": "penetration",
    "ult_finisher": "ult-oriented finisher",
}

# Tag → effect strength when present
TAG_TO_EFFECT: dict[str, tuple[str, float]] = {
    "heavy_dot": ("dot", 1.0),
    "dot": ("dot", 0.75),
    "prot_shred": ("prot_shred", 1.0),
    "channel": ("channel", 1.0),
    "ult_nuke": ("ult_nuke", 1.0),
    "burst": ("burst", 0.85),
    "spam": ("spam", 1.0),
    "aa": ("aa", 1.0),
    "as_steroid": ("as_steroid", 1.0),
    "mana_stack": ("mana_stack", 1.0),
    "self_sustain": ("self_sustain", 1.0),
    "heal": ("heal", 0.7),
    "heavy_heal": ("heavy_heal", 1.0),
    "execute": ("execute", 1.0),
    "shield": ("shield", 0.8),
    "heavy_shield": ("shield", 1.0),
    "zone": ("zone", 0.8),
    "pet_zone": ("pet_zone", 1.0),
    "hard_cc": ("hard_cc", 1.0),
    "high_cc": ("high_cc", 0.9),
    "immobile": ("immobile", 1.0),
    "mobile": ("mobile", 0.9),
    "gap_close": ("gap_close", 1.0),
    "team_buff": ("team_buff", 1.0),
    "anti_cc": ("anti_cc", 1.0),
    "sustained": ("sustained", 0.85),
    "long_cd": ("long_cd", 0.7),
}

# Extra text cues → effects (kit ability blob)
TEXT_EFFECT_RES: list[tuple[re.Pattern[str], str, float]] = [
    (re.compile(r"per tick|every (?:\d+\s*)?s(?:ec(?:ond)?s?)?|multi(?:ple)? hit|hits? up to \d|up to \d+ (?:times|enemies|gods)", re.I), "multi_hit", 0.9),
    (re.compile(r"damage over time|poison|burn(?:ing)?|blight", re.I), "dot", 0.7),
    (re.compile(r"reduc(?:e|es|ing).{0,24}protection|protection reduction|shred", re.I), "prot_shred", 0.85),
    (re.compile(r"\bchannel\b|channeling", re.I), "channel", 0.9),
    (re.compile(r"execut|below \d+%|low health|threshold", re.I), "execute", 0.8),
    (re.compile(r"basic attacks? deal|empowered basic|next basic|while active.{0,30}basic", re.I), "aa", 0.75),
]


def item_family(name: str) -> str | None:
    n = (name or "").lower()
    for key, fam in ITEM_TO_FAMILY:
        if key in n:
            return fam
    return None


def extract_kit_effects(bias: dict[str, Any]) -> dict[str, float]:
    """
    Effect id → strength 0..1 from tags, metrics, and ability text blob.
    """
    effects: dict[str, float] = {}

    def bump(eid: str, val: float) -> None:
        effects[eid] = min(1.0, max(effects.get(eid, 0.0), val))

    tags = set(bias.get("tags") or [])
    for tag, (eid, w) in TAG_TO_EFFECT.items():
        if tag in tags:
            bump(eid, w)

    # Metrics
    dots = int(bias.get("dots") or 0)
    if dots >= 1:
        bump("dot", 0.7)
        bump("multi_hit", 0.55)
    if dots >= 2:
        bump("dot", 1.0)
        bump("multi_hit", 0.85)
    if int(bias.get("shields") or 0) >= 1:
        bump("shield", 0.75)
    if float(bias.get("avg_cd") or 12) <= 8.0:
        bump("spam", 1.0)
    if float(bias.get("ult_scale") or 0) >= 100:
        bump("ult_nuke", 0.9)
    if float(bias.get("aa_score") or 0) >= 0.55:
        bump("aa", 0.9)
    if float(bias.get("style_burst") or 0) >= 0.55:
        bump("burst", max(0.7, float(bias.get("style_burst") or 0)))
    if float(bias.get("style_dps") or 0) >= 0.55:
        bump("sustained", max(0.7, float(bias.get("style_dps") or 0)))

    blob = str(bias.get("ability_blob") or "")
    for cre, eid, w in TEXT_EFFECT_RES:
        if cre.search(blob):
            bump(eid, w)

    # Derived: DoT / zone kits are multi-hit friendly
    if effects.get("dot", 0) >= 0.7 or effects.get("zone", 0) >= 0.7:
        bump("multi_hit", max(0.6, effects.get("multi_hit", 0)))
    if effects.get("pet_zone", 0) >= 0.7:
        bump("zone", max(0.65, effects.get("zone", 0)))

    return {k: round(v, 3) for k, v in effects.items() if v >= 0.45}


def effect_labels(effects: dict[str, float], limit: int = 8) -> list[str]:
    ranked = sorted(effects.items(), key=lambda x: -x[1])
    out = []
    for eid, _ in ranked[:limit]:
        lab = EFFECT_META.get(eid, {}).get("label", eid)
        out.append(lab)
    return out


def family_score_boost(item_name: str, effects: dict[str, float]) -> tuple[float, list[str]]:
    """
    Score boost + matched reason fragments for an item given kit effects.
    """
    fam = item_family(item_name)
    if not fam or not effects:
        return 0.0, []
    boost = 0.0
    reasons: list[str] = []
    for eid, strength in effects.items():
        meta = EFFECT_META.get(eid) or {}
        families = meta.get("families") or []
        if fam in families:
            boost += 28.0 * strength
            why = FAMILY_WHY.get(fam) or meta.get("label") or fam
            if why not in reasons:
                reasons.append(why)
    return boost, reasons[:2]


def explain_item_pick(
    item_name: str,
    *,
    bias: dict[str, Any],
    role: str,
    effects: dict[str, float] | None = None,
    slot_hint: str | None = None,
    is_pen: bool = False,
    is_active: bool = False,
    is_starter: bool = False,
) -> str:
    """One short line: why this item is on this god's path."""
    effects = effects if effects is not None else extract_kit_effects(bias)
    tags = set(bias.get("tags") or [])
    fam = item_family(item_name)
    bits: list[str] = []

    if is_starter:
        if role == "Support":
            return "Support starter — aura gold & early bulk"
        if role == "Jungle":
            return "Jungle starter — clear / camp sustain"
        if role == "Solo":
            return "Solo starter — lane pressure & sustain"
        if role == "Carry":
            return "Carry starter — early AS / sustain"
        return "Lane starter — early stats for this role"

    _, fam_reasons = family_score_boost(item_name, effects)
    if fam_reasons:
        bits.append(fam_reasons[0])
    elif fam and FAMILY_WHY.get(fam):
        # Generic family with weak effect match
        if any(eid in effects for eid in ("burst", "ult_nuke", "spam", "aa", "dot")):
            bits.append(FAMILY_WHY[fam])

    # Role / slot fallbacks
    if is_pen and not bits:
        if role in ("Mid", "Carry", "Jungle"):
            bits.append("penetration required for damage role")
        else:
            bits.append("penetration / hybrid offline")

    if slot_hint == "defense" and not bits:
        bits.append(f"{role} defensive slot — survive focus")
    if slot_hint == "mitigate" and not bits:
        bits.append("mitigation vs enemy damage types")
    if slot_hint == "aura" and not bits:
        bits.append("team aura core for support/frontline")
    if is_active and not bits:
        bits.append("On-Use active within shop budget")

    # Patch cue
    traj = (bias.get("trajectory") or "").lower()
    r5 = float(bias.get("recent_patch") or 0)
    axes = bias.get("patch_axes_r5") or bias.get("patch_axes") or {}
    if traj == "rising" or r5 >= 0.8:
        if fam in ("desolation", "obsidian", "titan", "tahuti", "soul_reaver", "as_crit"):
            bits.append("patch rising — lean damage")
    if traj == "falling" or r5 <= -0.8:
        if fam in ("bulk", "defense_cdr", "cdr_def", "magi", "hybrid_bulk"):
            bits.append("patch falling — extra bulk/CDR")
    cd_ax = float(axes.get("cooldown", 0) or 0)
    if cd_ax <= -0.25 and fam in ("chronos", "cdr_def", "defense_cdr", "focus"):
        bits.append("kit CD nerfed — buy CDR")
    dmg_ax = float(axes.get("damage", 0) or 0)
    if dmg_ax >= 0.25 and fam in ("desolation", "obsidian", "titan", "power", "tahuti"):
        bits.append("damage buffed — power/pen")

    # Tag leftovers
    if not bits and "mana_stack" in tags and fam == "mana":
        bits.append("mana stack passive")
    if not bits:
        primary = bias.get("primary") or ""
        if primary == "Intelligence" and fam in ("desolation", "obsidian", "tahuti", "soul_reaver"):
            bits.append("INT scaling core")
        elif primary == "Strength" and fam in ("titan", "desolation", "gap", "as_crit"):
            bits.append("STR scaling core")
        else:
            bits.append(f"{role} path fit for kit profile")

    # Keep one crisp sentence
    line = bits[0]
    if len(bits) > 1 and bits[1] not in line:
        line = f"{line}; {bits[1]}"
    return line[:160]


def load_kit_overrides(path: Path | None = None) -> dict[str, Any]:
    """Optional human overrides: force tags, prefer/ban items."""
    if path is None:
        path = Path(__file__).resolve().parent.parent / "data" / "kit_overrides.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def apply_kit_overrides(bias: dict[str, Any], god_name: str) -> dict[str, Any]:
    """Mutate a copy of bias with force_tags / ban list stored for assembly."""
    overrides = load_kit_overrides()
    entry = overrides.get(god_name) or overrides.get((god_name or "").strip())
    if not entry or not isinstance(entry, dict):
        return bias
    out = dict(bias)
    tags = set(out.get("tags") or [])
    for t in entry.get("force_tags") or []:
        tags.add(str(t))
    for t in entry.get("remove_tags") or []:
        tags.discard(str(t))
    out["tags"] = tags
    if entry.get("prefer_items"):
        out["prefer_items"] = [str(x).lower() for x in entry["prefer_items"]]
    if entry.get("ban_items"):
        out["ban_items"] = [str(x).lower() for x in entry["ban_items"]]
    if entry.get("archetype"):
        out["force_archetype"] = str(entry["archetype"])
    return out


def prefer_ban_adjust(item_name: str, bias: dict[str, Any]) -> float:
    """Score delta from override prefer/ban lists."""
    n = (item_name or "").lower()
    delta = 0.0
    for p in bias.get("prefer_items") or []:
        if p in n:
            delta += 55.0
    for b in bias.get("ban_items") or []:
        if b in n:
            delta -= 120.0
    return delta
