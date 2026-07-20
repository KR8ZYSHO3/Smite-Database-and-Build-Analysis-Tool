"""
God Aspect kit profiles for itemization.

Base builds use normal ability metrics. Aspect builds re-tag the kit from the
aspect summary + enhanced ability text so itemization can shift playstyle
(e.g. Geb Calamity → AA/crit, Ra Thermotherapy → heal support, Kali → ranged AA).
"""

from __future__ import annotations

import re
import sqlite3
from typing import Any

from .kit_effects import (
    apply_kit_overrides,
    effect_labels,
    extract_kit_effects,
)


# (regex on aspect description + enhanced kit text) → tags to force on / off
ASPECT_TAG_RULES: list[tuple[re.Pattern[str], set[str], set[str]]] = [
    # add_tags, remove_tags
    (
        re.compile(
            r"basics? are ranged|basic attacks? are ranged|ranged\.|fire a projectile|"
            r"throw a piercing projectile|attacks are ranged",
            re.I,
        ),
        {"aa", "as_steroid"},
        set(),
    ),
    (
        re.compile(r"\bcrits?\b|critical strike|on-hits?|triggers on-hits", re.I),
        {"aa", "as_steroid"},
        set(),
    ),
    (
        re.compile(r"attack speed|attack damage from intelligence|extra attack damage", re.I),
        {"aa", "as_steroid"},
        set(),
    ),
    (
        re.compile(
            r"only deal base damage with no scaling|no scaling|base damage with no scaling",
            re.I,
        ),
        {"heal", "team_buff", "aspect_utility"},
        {"burst", "ult_nuke"},
    ),
    (
        re.compile(r"heals? allied|heal(?:s|ing)? allies|attach(?:es|ing)? to them", re.I),
        {"heal", "team_buff", "heavy_heal"},
        set(),
    ),
    (
        re.compile(r"permanent cooldown|cooldown rate|reduced cooldown", re.I),
        {"spam"},
        {"long_cd"},
    ),
    (
        re.compile(r"self-only|only heals? (?:you|baron|himself|herself)", re.I),
        {"self_sustain"},
        {"team_buff", "heavy_heal"},
    ),
    (
        re.compile(r"random stance|random (?:primary )?abilities|elemental mastery", re.I),
        {"burst", "spam", "ult_nuke"},
        set(),
    ),
    (
        re.compile(r"does not (?:stun|mesmerize|silence)|no longer (?:stun|stealth|silence)", re.I),
        set(),
        {"hard_cc"},
    ),
    (
        re.compile(r"knockback|knocks? back", re.I),
        {"hard_cc"},
        set(),
    ),
    (
        re.compile(r"damage over time|\bdot\b|hysteria|per tick", re.I),
        {"dot", "heavy_dot"},
        set(),
    ),
    (
        re.compile(r"lifesteal|heal her|heals? (?:you|yourself|baron)", re.I),
        {"self_sustain", "heal"},
        set(),
    ),
    (
        re.compile(r"-[\d.]+%\s*base health|reduced health|less health", re.I),
        {"aa", "burst"},  # glassier → more damage lean
        {"immobile"},
    ),
    (
        re.compile(r"swap positions|clone|decoy", re.I),
        {"mobile", "gap_close"},
        set(),
    ),
    (
        re.compile(r"protections? rather than|scaling with your health and protections", re.I),
        {"hybrid_bulk", "shield"},
        set(),
    ),
]


def list_god_aspects(conn: sqlite3.Connection, god_id: int) -> list[dict[str, Any]]:
    try:
        rows = conn.execute(
            """
            SELECT id, god_id, name, description, image
            FROM god_aspects WHERE god_id = ? ORDER BY id
            """,
            (god_id,),
        ).fetchall()
    except sqlite3.OperationalError:
        return []
    return [dict(r) for r in rows]


def load_aspect_abilities(conn: sqlite3.Connection, aspect_id: int) -> list[dict[str, Any]]:
    try:
        rows = conn.execute(
            """
            SELECT slot, slot_order, name, short_label, description, stats_text, notes_text
            FROM god_aspect_abilities WHERE aspect_id = ? ORDER BY slot_order, id
            """,
            (aspect_id,),
        ).fetchall()
    except sqlite3.OperationalError:
        return []
    return [dict(r) for r in rows]


def _aspect_kit_blob(aspect: dict[str, Any], abilities: list[dict[str, Any]]) -> str:
    parts = [aspect.get("name") or "", aspect.get("description") or ""]
    for a in abilities:
        parts.append(
            f"{a.get('slot') or ''} {a.get('name') or ''} {a.get('short_label') or ''} "
            f"{a.get('description') or ''} {a.get('stats_text') or ''} {a.get('notes_text') or ''}"
        )
    return " ".join(parts).lower()


def apply_aspect_tag_rules(tags: set[str], blob: str) -> set[str]:
    tags = set(tags)
    for cre, add, remove in ASPECT_TAG_RULES:
        if cre.search(blob):
            tags |= add
            tags -= remove
    return tags


def aspect_playstyle_hints(blob: str) -> dict[str, Any]:
    """Numeric style nudges for item scoring."""
    hints: dict[str, Any] = {
        "aa_boost": 0.0,
        "power_penalty": 0.0,
        "cdr_boost": 0.0,
        "heal_boost": 0.0,
        "bulk_boost": 0.0,
        "prefer_items": [],
        "ban_items": [],
        "force_archetype": None,
    }
    if re.search(r"no scaling|only deal base damage", blob, re.I):
        hints["power_penalty"] = 0.35
        hints["heal_boost"] = 0.4
        hints["prefer_items"].extend(["asclepius", "thebes", "chandra", "genji", "chronos"])
        hints["ban_items"].extend(["tahuti", "dreamer", "obsidian", "soul reaver"])
        hints["force_archetype"] = None  # role decides; tags drive heal_support etc.
    if re.search(r"basics? are ranged|attacks are ranged|on-hits?|crits?", blob, re.I):
        hints["aa_boost"] = 0.45
        hints["prefer_items"].extend(
            ["deathbringer", "demon", "riptalon", "avenging", "qins", "ichival", "musashi"]
        )
    if re.search(r"attack speed", blob, re.I):
        hints["aa_boost"] = max(hints["aa_boost"], 0.35)
        hints["prefer_items"].extend(["riptalon", "ichival", "wind"])
    if re.search(r"cooldown rate|reduced cooldown|permanent cooldown", blob, re.I):
        hints["cdr_boost"] = 0.4
        hints["prefer_items"].extend(["chronos", "breastplate", "genji", "valor"])
    if re.search(r"health and protections|protections rather than", blob, re.I):
        hints["bulk_boost"] = 0.3
        hints["prefer_items"].extend(["shifter", "gladiator", "ancile"])
    if re.search(r"-[\d.]+%\s*base health", blob, re.I):
        hints["bulk_boost"] = max(0.0, hints["bulk_boost"] - 0.1)
        hints["aa_boost"] = max(hints["aa_boost"], 0.2)
    return hints


def build_aspect_bias(
    conn: sqlite3.Connection,
    god_id: int,
    base_bias: dict[str, Any],
    aspect_id: int | None = None,
) -> dict[str, Any]:
    """
    Clone base god bias and rewrite tags/effects/preferences for the aspect kit.
    """
    aspects = list_god_aspects(conn, god_id)
    if not aspects:
        return base_bias
    aspect = None
    if aspect_id is not None:
        aspect = next((a for a in aspects if a["id"] == aspect_id), None)
    if aspect is None:
        aspect = aspects[0]

    abilities = load_aspect_abilities(conn, aspect["id"])
    blob = _aspect_kit_blob(aspect, abilities)

    bias = dict(base_bias)
    tags = set(bias.get("tags") or [])
    tags = apply_aspect_tag_rules(tags, blob)
    # Aspect text is authoritative for identity — re-scan key words
    if re.search(r"\bheal", blob, re.I):
        tags.add("heal")
    if re.search(r"\bchannel", blob, re.I):
        tags.add("channel")
    if re.search(r"basic attack|basics?", blob, re.I) and re.search(
        r"ranged|projectile|attack speed|crit", blob, re.I
    ):
        tags.add("aa")
        tags.add("as_steroid")

    hints = aspect_playstyle_hints(blob)
    aa = float(bias.get("aa_score") or 0)
    aa = min(1.0, aa + hints["aa_boost"])
    if hints["aa_boost"] >= 0.3:
        aa = max(aa, 0.7)
        tags.add("aa")
    bias["aa_score"] = aa

    sb = float(bias.get("style_burst") or 0.5)
    sd = float(bias.get("style_dps") or 0.5)
    if hints["aa_boost"] >= 0.3:
        sd = min(0.85, sd + 0.2)
        sb = max(0.2, sb - 0.1)
        tags.add("sustained")
    if hints["power_penalty"] >= 0.2:
        sb = max(0.15, sb - 0.2)
        tags.discard("burst")
        tags.discard("ult_nuke")
    if hints["cdr_boost"] >= 0.2:
        tags.add("spam")
        tags.discard("long_cd")
        bias["avg_cd"] = min(float(bias.get("avg_cd") or 12), 7.5)

    bias["style_burst"] = sb
    bias["style_dps"] = sd
    bias["tags"] = tags
    bias["ability_blob"] = (blob + " " + str(bias.get("ability_blob") or ""))[:5000]
    bias["aspect_id"] = aspect["id"]
    bias["aspect_name"] = aspect["name"]
    bias["aspect_description"] = aspect.get("description") or ""
    bias["is_aspect"] = True

    # Prefer/ban from aspect rules (merged with overrides later)
    prefer = list(bias.get("prefer_items") or [])
    ban = list(bias.get("ban_items") or [])
    for p in hints["prefer_items"]:
        if p not in prefer:
            prefer.append(p)
    for b in hints["ban_items"]:
        if b not in ban:
            ban.append(b)
    bias["prefer_items"] = prefer
    bias["ban_items"] = ban
    if hints.get("force_archetype"):
        bias["force_archetype"] = hints["force_archetype"]

    # Aspect-specific archetype nudges by role-agnostic tags
    if "aa" in tags and hints["aa_boost"] >= 0.3:
        # Carry will pick crit_adc; mid aa_mage — detect_archetype handles role
        pass
    if hints["power_penalty"] >= 0.2 and "heal" in tags:
        # Support/Mid heal mages
        pass

    bias = apply_kit_overrides(bias, str(bias.get("god_name") or ""))
    # Also allow overrides keyed by aspect name
    bias = apply_kit_overrides(bias, str(aspect["name"] or ""))
    effects = extract_kit_effects(bias)
    bias["effects"] = effects
    bias["effect_labels"] = effect_labels(effects)
    # Store scoring nudges for rescore
    bias["aspect_power_penalty"] = hints["power_penalty"]
    bias["aspect_cdr_boost"] = hints["cdr_boost"]
    bias["aspect_heal_boost"] = hints["heal_boost"]
    bias["aspect_bulk_boost"] = hints["bulk_boost"]
    return bias


def aspect_item_score_delta(item_name: str, bias: dict[str, Any]) -> float:
    """Extra score from aspect playstyle hints."""
    if not bias.get("is_aspect"):
        return 0.0
    n = (item_name or "").lower()
    s = 0.0
    pen = float(bias.get("aspect_power_penalty") or 0)
    if pen >= 0.2:
        if any(k in n for k in ("tahuti", "dreamer", "soul reaver", "obsidian", "desolat")):
            s -= 45 * pen
        if any(k in n for k in ("asclepius", "thebes", "chandra", "chronos", "genji", "breastplate")):
            s += 35 * pen
    if float(bias.get("aspect_cdr_boost") or 0) >= 0.2:
        if any(k in n for k in ("chronos", "genji", "breastplate", "valor", "pendant")):
            s += 30
    if float(bias.get("aspect_heal_boost") or 0) >= 0.2:
        if any(k in n for k in ("asclepius", "lifebinder", "bancroft", "soul gem", "thebes")):
            s += 32
    if float(bias.get("aa_score") or 0) >= 0.65 and bias.get("is_aspect"):
        if any(
            k in n
            for k in (
                "deathbringer",
                "demon",
                "riptalon",
                "avenging",
                "qins",
                "musashi",
                "ichival",
                "wind",
            )
        ):
            s += 40
    return s
