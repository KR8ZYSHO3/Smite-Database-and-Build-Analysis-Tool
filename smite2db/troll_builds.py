"""
Troll / anti-fun Conquest builds.

Not "worst items" and not ranked advice. A troll path is kit-true but off-meta:
it exploits the god's abilities to maximize frustration (unkillable, peel prison,
antiheal tax, infinite poke, AA clown, aura tax, active toybox).
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sqlite3
from typing import Any

from .aspect_kit import build_aspect_bias, list_god_aspects
from .conquest_builds import (
    HARD_MAX_ACTIVE_ITEMS,
    ROLE_PROFILES,
    ScoredItem,
    _canon_stat_value,
    _order_buy_path,
    god_scaling_bias,
    is_base_relic,
    is_pen_item,
    is_t1_starter,
    is_t3_core,
    item_pen_value,
    load_items,
    max_shop_actives_for_god,
    pick_god_starter,
    rescore_for_god,
    score_item_for_role,
    score_relic,
    score_starter,
    _item_card,
)
from .counter_builds import resolve_god
from .kit_effects import effect_labels, explain_item_pick, extract_kit_effects, item_family

# Primary frustration axes
TROLL_AXES = (
    "unkillable",      # never dies, soft damage
    "peel_prison",     # CC / slows / peel forever
    "antiheal_tax",    # their sustain feels useless
    "infinite_poke",   # CDR zone spam
    "aa_clown",        # AA/on-hit on "wrong" gods
    "aura_tax",        # free stats for existing
    "active_toybox",   # expensive On-Use memes
)

# Axis → preferred item name keys (substring match)
AXIS_ITEM_KEYS: dict[str, list[str]] = {
    "unkillable": [
        "shifter", "hussar", "freya", "spectral", "magi", "mantle", "alchemist",
        "phoenix", "pridwen", "gladiator", "sanguine", "bancroft", "typhon",
        "asclepius", "lifebinder", "heartwood", "draconic", "oni hunter",
    ],
    "peel_prison": [
        "stygian", "binding", "isolation", "midgardian", "spectral", "magi",
        "mantle", "witchblade", "contagion", "genji", "breastplate", "chronos",
    ],
    "antiheal_tax": [
        "contagion", "divine ruin", "pestilence", "brawler", "toxic", "desolat",
    ],
    "infinite_poke": [
        "chronos", "pendant", "gem of focus", "breastplate", "genji", "book of",
        "thoth", "doom orb", "isolation", "magus", "soul gem", "myrddin",
    ],
    "aa_clown": [
        "deathbringer", "demon", "riptalon", "avenging", "musashi", "qins",
        "ichival", "wind", "executioner", "bloodforge", "devourer", "odysseus",
    ],
    "aura_tax": [
        "thebes", "chandra", "sovereign", "heartward", "providence", "contagion",
        "spectral", "midgardian",
    ],
    "active_toybox": [
        "dreamer", "wish-granting", "parashu", "arondight", "pridwen", "erebus",
    ],
}

# Items that are "correct tryhard" — downrank on troll unless axis wants them
TRYHARD_PENALTY_KEYS = (
    "soul reaver", "tahuti", "titan's bane", "obsidian shard", "deathbringer",
    "heartseeker", "arondight",
)

# Forced archetype slot recipes for troll axes (role-agnostic enough)
TROLL_SLOTS: dict[str, list[str]] = {
    "unkillable": ["sustain", "defense", "mitigate", "hybrid_bulk", "cdr_def", "aura"],
    "peel_prison": ["mitigate", "counter", "aura", "cdr_def", "defense", "tenacity"],
    "antiheal_tax": ["antiheal", "flat_pen", "defense", "mitigate", "cdr", "hybrid_bulk"],
    "infinite_poke": ["cdr", "mana_stack", "zone_core", "flat_pen", "sustain", "defense"],
    "aa_clown": ["as_core", "onhit", "crit_core", "ls_core", "power", "defense"],
    "aura_tax": ["aura", "mitigate", "defense", "cdr_def", "counter", "heal_aura"],
    "active_toybox": ["luxury", "power", "flat_pen", "defense", "cdr", "sustain"],
}

TROLL_TITLES: dict[str, list[str]] = {
    "unkillable": [
        "Please Report Simulator",
        "Unkillable Clown Fiesta",
        "I Am A Raid Boss",
        "Your Ult Was A Suggestion",
    ],
    "peel_prison": [
        "Nobody Gets To Hit Anything",
        "Peel Prison Warden",
        "ADC Timeout Corner",
        "Crowd Control Tax Office",
    ],
    "antiheal_tax": [
        "Healing? In THIS Economy?",
        "Contagion Enjoyer",
        "Your Bancroft Is Decorative",
        "Anti-Fun Pharmacy",
    ],
    "infinite_poke": [
        "Death By A Thousand Ticks",
        "Cooldown Rate Menace",
        "Zone Tax Forever",
        "We Do Not Fight — We Annoy",
    ],
    "aa_clown": [
        "Basics Were A Mistake",
        "On-Hit Menace",
        "This God Shouldn't Auto Like This",
        "Crit Is A Lifestyle",
    ],
    "aura_tax": [
        "I Get Paid To Exist",
        "Aura Farmer Supreme",
        "Free Stats For Standing",
        "Thebes And Chill",
    ],
    "active_toybox": [
        "Button Mashing Menace",
        "On-Use Toybox",
        "Ultimate? We Have Actives At Home",
        "Cooldown For Chaos",
    ],
}

AXIS_BLURBS: dict[str, str] = {
    "unkillable": "Maximize time-on-screen and soft sustain. You are not here to win lane — you are here to waste their cooldowns.",
    "peel_prison": "Deny free hits. Slow, shred setup, anti-crit, and bulk so their backline feels trapped.",
    "antiheal_tax": "If they heal, they tilt. Stack reduction and sit on their face.",
    "infinite_poke": "CDR + zone/tick pressure. Never commit to a fair fight; only chip and leave.",
    "aa_clown": "Lean into basic-attack or on-hit identity the ranked path ignores. Wrong, but sticky.",
    "aura_tax": "Bodyblock, auras, and free team value for existing in the fight.",
    "active_toybox": "Splashy On-Use and meme power spikes within the active budget. Chaos is the point.",
}


def detect_troll_axes(
    bias: dict[str, Any],
    role: str,
    *,
    use_aspect: bool = False,
) -> list[tuple[str, float]]:
    """
    Rank frustration axes for this kit. Returns [(axis, score), ...] best first.
    """
    tags = set(bias.get("tags") or [])
    effects = bias.get("effects") or extract_kit_effects(bias)
    blob = str(bias.get("ability_blob") or "") + " " + str(bias.get("aspect_description") or "")
    blob = blob.lower()
    scores: dict[str, float] = {a: 0.0 for a in TROLL_AXES}

    # Role priors
    if role in ("Support", "Solo"):
        scores["unkillable"] += 1.2
        scores["peel_prison"] += 1.4
        scores["aura_tax"] += 1.3
        scores["antiheal_tax"] += 0.6
    if role in ("Mid", "Carry"):
        scores["infinite_poke"] += 1.0
        scores["aa_clown"] += 0.5
        scores["active_toybox"] += 0.4
    if role == "Jungle":
        scores["peel_prison"] += 0.5
        scores["antiheal_tax"] += 0.7
        scores["aa_clown"] += 0.6
        scores["unkillable"] += 0.4

    # Tag / effect driven
    if tags & {"heal", "heavy_heal", "self_sustain"} or effects.get("heal", 0) >= 0.6:
        scores["unkillable"] += 1.5
        scores["antiheal_tax"] += 0.4  # they heal; also can deny
    if tags & {"hard_cc", "high_cc"} or effects.get("hard_cc", 0) >= 0.7:
        scores["peel_prison"] += 1.8
    if tags & {"dot", "heavy_dot", "zone", "pet_zone", "channel"} or effects.get("dot", 0) >= 0.6:
        scores["infinite_poke"] += 1.6
    if tags & {"aa", "as_steroid"} or float(bias.get("aa_score") or 0) >= 0.55:
        scores["aa_clown"] += 1.7
    if tags & {"spam"} or float(bias.get("avg_cd") or 12) <= 8.5:
        scores["infinite_poke"] += 1.0
    if tags & {"team_buff"} or role == "Support":
        scores["aura_tax"] += 1.2
    if tags & {"shield", "heavy_shield", "immobile"}:
        scores["unkillable"] += 1.0
    if tags & {"execute", "burst", "ult_nuke"}:
        scores["active_toybox"] += 0.8
        # still can unkillable if tank role
    if use_aspect or bias.get("is_aspect"):
        scores["aa_clown"] += 0.5  # aspects often enable weird modes
        if re.search(r"no scaling|base damage with no scaling", blob):
            scores["unkillable"] += 1.2
            scores["aura_tax"] += 0.8
            scores["infinite_poke"] -= 0.5
        if re.search(r"ranged|on-hit|crit|attack speed", blob):
            scores["aa_clown"] += 1.5
        if re.search(r"cooldown rate|reduced cooldown", blob):
            scores["infinite_poke"] += 1.0

    # Mage guardians doing AA is maximum troll
    if (bias.get("primary") == "Intelligence" or "magical" in str(bias.get("god_name") or "").lower()) and (
        "aa" in tags or scores["aa_clown"] >= 2
    ):
        if role in ("Support", "Solo", "Mid"):
            scores["aa_clown"] += 0.8

    ranked = sorted(scores.items(), key=lambda x: -x[1])
    # Keep axes with meaningful score
    out = [(a, s) for a, s in ranked if s >= 0.8]
    if not out:
        out = [("unkillable", 1.0), ("peel_prison", 0.9)]
    return out


def pick_troll_identity(
    bias: dict[str, Any],
    role: str,
    *,
    use_aspect: bool = False,
    rng: random.Random | None = None,
) -> dict[str, Any]:
    """Primary + secondary axis, title, blurb."""
    rng = rng or random.Random(
        sum(ord(c) for c in f"{bias.get('god_name')}|{role}|{bias.get('aspect_name') or ''}")
    )
    ranked = detect_troll_axes(bias, role, use_aspect=use_aspect)
    primary = ranked[0][0]
    secondary = ranked[1][0] if len(ranked) > 1 else primary
    # Slight god-salted swap if top two are close
    if len(ranked) > 1 and ranked[0][1] - ranked[1][1] < 0.35:
        if rng.random() < 0.35:
            primary, secondary = secondary, primary
    titles = TROLL_TITLES.get(primary) or ["Certified Troll Path"]
    title = titles[rng.randrange(len(titles))]
    return {
        "primary_axis": primary,
        "secondary_axis": secondary,
        "axes_ranked": ranked[:4],
        "title": title,
        "blurb": AXIS_BLURBS.get(primary, "Be annoying on purpose."),
        "disclaimer": "TROLL / MEME — not ranked advice. Legal items, illegal vibes.",
    }


def troll_score_delta(
    item: ScoredItem,
    identity: dict[str, Any],
    bias: dict[str, Any],
    role: str,
) -> tuple[float, list[str]]:
    """Score boost for troll identity + reasons."""
    n = item.name.lower()
    fam = item_family(item.name) or ""
    primary = identity["primary_axis"]
    secondary = identity["secondary_axis"]
    delta = 0.0
    why: list[str] = []

    def hit_keys(keys: list[str]) -> bool:
        return any(k in n for k in keys)

    for axis, weight in ((primary, 1.0), (secondary, 0.55)):
        keys = AXIS_ITEM_KEYS.get(axis) or []
        if hit_keys(keys):
            delta += 55 * weight
            if weight >= 0.9:
                why.append(f"troll {axis.replace('_', ' ')}")

    # Tryhard penalty unless axis wants that item
    primary_keys = AXIS_ITEM_KEYS.get(primary) or []
    for k in TRYHARD_PENALTY_KEYS:
        if k in n and not any(pk in n for pk in primary_keys if len(pk) > 3):
            # Deathbringer OK for aa_clown
            if primary == "aa_clown" and k == "deathbringer":
                continue
            if primary == "active_toybox" and k in ("dreamer", "parashu"):
                continue
            if primary == "infinite_poke" and "obsidian" in k:
                continue
            delta -= 35
            break

    # Axis-specific stat lean
    hp = _canon_stat_value(item.stats, "hp")
    mprot = _canon_stat_value(item.stats, "mprot")
    pprot = _canon_stat_value(item.stats, "pprot")
    cdr = _canon_stat_value(item.stats, "cdr")
    as_v = _canon_stat_value(item.stats, "as")
    crit = _canon_stat_value(item.stats, "crit")
    pen = item_pen_value(item)

    if primary == "unkillable":
        if item.item_type == "Defensive" or hp >= 250:
            delta += 28
        if item.item_type == "Offensive" and pen >= 15 and hp < 150:
            delta -= 40
    if primary == "peel_prison":
        if fam in ("anti_crit", "anti_as", "magi", "tenacity", "binding", "peel"):
            delta += 30
        if cdr >= 10:
            delta += 12
    if primary == "antiheal_tax":
        if fam in ("antiheal", "divine", "contagion"):
            delta += 45
    if primary == "infinite_poke":
        if cdr >= 10 or fam in ("chronos", "focus", "mana", "zone", "magus"):
            delta += 32
        if (item.total_cost or 0) >= 3400 and item.is_active_item:
            delta -= 15  # less pure luxury, more CDR
    if primary == "aa_clown":
        if as_v >= 10 or crit >= 15 or fam in ("as_crit", "onhit", "ls"):
            delta += 40
        if role in ("Support", "Solo") and item.item_type == "Offensive":
            delta += 15  # wrong and proud
    if primary == "aura_tax":
        if fam == "aura" or any(k in n for k in ("thebes", "chandra", "sovereign")):
            delta += 45
    if primary == "active_toybox":
        if item.is_active_item and (item.total_cost or 0) >= 2800:
            delta += 38
            why.append("active toy")

    # Prefer items already preferred by aspect/kit troll lean
    for p in bias.get("prefer_items") or []:
        if p in n:
            delta += 12

    if not why and delta > 20:
        why.append(f"{primary.replace('_', ' ')} core")
    return delta, why[:2]


def build_troll_build(
    conn: sqlite3.Connection,
    items: list[dict] | None,
    role: str,
    god: dict,
    *,
    use_aspect: bool = False,
    aspect_id: int | None = None,
    chaos: bool = False,
) -> dict[str, Any]:
    """
    Assemble a kit-true troll path for god × role.
    chaos=True amplifies secondary axis and active toys.
    """
    if items is None:
        items = load_items(conn)
    profile = ROLE_PROFILES.get(role) or ROLE_PROFILES["Mid"]
    bias = god_scaling_bias(conn, god["god_id"])
    if use_aspect or aspect_id is not None:
        aspects = list_god_aspects(conn, god["god_id"])
        if aspects:
            bias = build_aspect_bias(conn, god["god_id"], bias, aspect_id=aspect_id)
            use_aspect = True

    identity = pick_troll_identity(bias, role, use_aspect=use_aspect)
    if chaos and identity["secondary_axis"] != identity["primary_axis"]:
        # Swap weight: lean harder into secondary meme
        identity = dict(identity)
        identity["primary_axis"], identity["secondary_axis"] = (
            identity["secondary_axis"],
            identity["primary_axis"],
        )
        identity["title"] = (TROLL_TITLES.get(identity["primary_axis"]) or ["Chaos Path"])[0]
        identity["blurb"] = AXIS_BLURBS.get(identity["primary_axis"], identity["blurb"])

    bias = dict(bias)
    bias["troll_mode"] = True
    bias["troll_identity"] = identity
    # Soft tag inject so assemble prefers matching slots
    tags = set(bias.get("tags") or [])
    ax = identity["primary_axis"]
    if ax == "aa_clown":
        tags |= {"aa", "as_steroid", "sustained"}
        bias["aa_score"] = max(float(bias.get("aa_score") or 0), 0.75)
    if ax == "infinite_poke":
        tags |= {"spam", "dot", "zone"}
        bias["avg_cd"] = min(float(bias.get("avg_cd") or 12), 7.0)
    if ax == "unkillable":
        tags |= {"self_sustain", "shield"}
    if ax == "peel_prison":
        tags |= {"hard_cc", "high_cc"}
    if ax == "antiheal_tax":
        tags |= {"prot_shred"}
    if ax == "aura_tax":
        tags |= {"team_buff"}
    bias["tags"] = tags
    effects = extract_kit_effects(bias)
    bias["effects"] = effects
    bias["effect_labels"] = effect_labels(effects)

    dtype = god.get("primary_damage_type")
    primary = bias.get("primary") or ""
    mage = primary == "Intelligence" or (dtype or "").lower() == "magical"
    physical = (primary == "Strength" or (dtype or "").lower() == "physical") and not mage

    scored: list[ScoredItem] = []
    troll_whys: dict[str, list[str]] = {}
    for it in items:
        base = score_item_for_role(it, role, profile)
        base.role_score = rescore_for_god(base, bias, role, damage_type=dtype)
        # Shrink "optimal" signal, inflate troll
        base.role_score = base.role_score * 0.45
        td, tw = troll_score_delta(base, identity, bias, role)
        base.role_score += td
        if tw:
            troll_whys[base.name] = tw
        scored.append(base)
    scored.sort(key=lambda x: x.role_score, reverse=True)

    starters = [s for s in scored if is_t1_starter(next(i for i in items if i["name"] == s.name))]
    starter_pick = pick_god_starter(starters, items, profile, bias, role, dtype)
    for s in starters:
        raw = next(i for i in items if i["name"] == s.name)
        s.role_score = score_starter(raw, profile, role=role)
    starters.sort(key=lambda x: x.role_score, reverse=True)
    if starter_pick:
        starters = [starter_pick] + [s for s in starters if s.name != starter_pick.name]

    t3 = [s for s in scored if is_t3_core(next(i for i in items if i["name"] == s.name))]
    max_act = max_shop_actives_for_god(role, dtype, bias)
    if identity["primary_axis"] == "active_toybox":
        max_act = min(HARD_MAX_ACTIVE_ITEMS, max(max_act, 2))

    # Slot recipe from troll axis (override archetype assembly)
    slots = list(TROLL_SLOTS.get(identity["primary_axis"]) or TROLL_SLOTS["unkillable"])
    # Mage AA clown: ensure power type ok
    path: list[ScoredItem] = []
    seen: set[str] = set()
    actives = 0
    dkey = str(bias.get("god_name") or "") + "|troll|" + identity["primary_axis"]

    from .conquest_builds import _pick_slot_item

    for slot in slots:
        if len(path) >= 6:
            break
        pick = _pick_slot_item(
            t3,
            slot,
            seen,
            mage=mage,
            physical=physical,
            role=role,
            max_actives=max_act,
            active_count=actives,
            diversify_key=dkey,
            tags=tags,
            luxury_actives=sum(1 for x in path if x.is_active_item and (x.total_cost or 0) >= 3200),
            max_luxury_actives=2 if identity["primary_axis"] == "active_toybox" else 1,
        )
        if not pick:
            continue
        path.append(pick)
        seen.add(pick.name)
        if pick.is_active_item:
            actives += 1

    # Force inject top axis keys
    path = _inject_troll_cores(path, t3, identity, max_act, seen_actives=actives)
    path = list(path)[:6]
    seen = {x.name for x in path}
    actives = sum(1 for x in path if x.is_active_item)

    # Fill remaining by pure troll score
    if len(path) < 6:
        rest = [x for x in t3 if x.name not in seen]
        rest.sort(key=lambda x: x.role_score, reverse=True)
        for x in rest:
            if len(path) >= 6:
                break
            if x.is_active_item and actives >= max_act:
                continue
            path.append(x)
            seen.add(x.name)
            if x.is_active_item:
                actives += 1

    path = _order_buy_path(path, role)

    # Cards
    path_cards = []
    for it in path:
        base_why = explain_item_pick(
            it.name,
            bias=bias,
            role=role,
            effects=effects,
            is_pen=is_pen_item(it),
            is_active=bool(it.is_active_item),
        )
        tw = troll_whys.get(it.name) or []
        if not tw:
            _, tw = troll_score_delta(it, identity, bias, role)
        if tw:
            why = f"😈 {tw[0]}" + (f" — {base_why}" if base_why else "")
        else:
            why = f"😈 troll flex — {base_why}" if base_why else "😈 troll flex"
        card = _item_card(it, why=why[:180])
        if card:
            card["troll"] = True
            path_cards.append(card)

    starter_card = None
    if starters:
        sw = explain_item_pick(
            starters[0].name, bias=bias, role=role, effects=effects, is_starter=True
        )
        starter_card = _item_card(starters[0], why=f"😈 {sw}")

    relics = [s for s in scored if is_base_relic(next(i for i in items if i["name"] == s.name))]
    for r in relics:
        r.role_score = score_relic(next(i for i in items if i["name"] == r.name), profile)
        rn = r.name.lower()
        if identity["primary_axis"] in ("unkillable", "peel_prison") and "aegis" in rn:
            r.role_score += 25
        if identity["primary_axis"] == "peel_prison" and "bead" in rn:
            r.role_score += 20
        if "blink" in rn and role in ("Jungle", "Support"):
            r.role_score += 8
    relics.sort(key=lambda x: x.role_score, reverse=True)

    pen_total = sum(item_pen_value(x) for x in path)
    n_act = sum(1 for x in path if x.is_active_item)
    gname = god.get("entity_name") or god.get("name")

    monologue = (
        f"{identity['title']}. {identity['blurb']} "
        f"Primary annoyance: {identity['primary_axis'].replace('_', ' ')}; "
        f"backup bit: {identity['secondary_axis'].replace('_', ' ')}."
    )
    if bias.get("aspect_name"):
        monologue += f" Running {bias['aspect_name']} because the bit is better."

    return {
        "god": gname,
        "role": role,
        "mode": "troll",
        "disclaimer": identity["disclaimer"],
        "troll_title": identity["title"],
        "troll_blurb": identity["blurb"],
        "primary_axis": identity["primary_axis"],
        "secondary_axis": identity["secondary_axis"],
        "axes": [
            {"axis": a, "score": round(s, 2)} for a, s in identity.get("axes_ranked") or []
        ],
        "is_aspect": bool(bias.get("is_aspect")),
        "aspect_name": bias.get("aspect_name"),
        "aspect_description": bias.get("aspect_description"),
        "kit_tags": sorted(bias.get("tags") or []),
        "kit_effects": bias.get("effect_labels") or effect_labels(effects),
        "damage_type": dtype,
        "scaling": bias.get("primary"),
        "starter": starter_card,
        "items": path_cards,
        "full_path": path_cards,
        "relics": [_item_card(r) for r in relics[:2]],
        "max_shop_actives": max_act,
        "hard_max_actives": HARD_MAX_ACTIVE_ITEMS,
        "active_count": n_act,
        "pen_total": round(pen_total, 1),
        "chaos": chaos,
        "why": monologue,
        "monologue": monologue,
    }


def _inject_troll_cores(
    path: list[ScoredItem],
    pool: list[ScoredItem],
    identity: dict[str, Any],
    max_actives: int,
    *,
    seen_actives: int,
) -> list[ScoredItem]:
    path = list(path)
    seen = {x.name for x in path}
    actives = seen_actives
    keys = list(AXIS_ITEM_KEYS.get(identity["primary_axis"]) or [])[:6]
    # Also sprinkle secondary
    for k in (AXIS_ITEM_KEYS.get(identity["secondary_axis"]) or [])[:3]:
        if k not in keys:
            keys.append(k)

    injected = 0
    for key in keys:
        if injected >= 3:
            break
        if any(key in x.name.lower() for x in path):
            continue
        cands = [
            x
            for x in pool
            if x.name not in seen
            and key in x.name.lower()
            and not (x.is_active_item and actives >= max_actives)
        ]
        if not cands:
            continue
        cands.sort(key=lambda x: x.role_score, reverse=True)
        pick = cands[0]
        # Replace lowest score non-core
        if len(path) >= 6:
            drop = min(range(len(path)), key=lambda i: path[i].role_score)
            # don't drop if already a primary key hit
            nlow = path[drop].name.lower()
            if any(k in nlow for k in keys[:4]):
                # find another drop
                ranked = sorted(range(len(path)), key=lambda i: path[i].role_score)
                drop = None
                for i in ranked:
                    if not any(k in path[i].name.lower() for k in keys[:4]):
                        drop = i
                        break
                if drop is None:
                    continue
            seen.discard(path[drop].name)
            if path[drop].is_active_item:
                actives = max(0, actives - 1)
            path[drop] = pick
        else:
            path.append(pick)
        seen.add(pick.name)
        if pick.is_active_item:
            actives += 1
        injected += 1
    return path


def troll_cli(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="SMITE 2 troll / anti-fun build generator")
    p.add_argument("god", help="God name")
    p.add_argument(
        "role",
        nargs="?",
        default="Support",
        choices=["Carry", "Mid", "Jungle", "Solo", "Support"],
    )
    p.add_argument("--aspect", action="store_true", help="Use god aspect kit if available")
    p.add_argument("--chaos", action="store_true", help="Lean into secondary meme harder")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    from .db import connect

    conn = connect()
    items = load_items(conn)
    god = resolve_god(conn, args.god)
    if not god:
        print(f"God not found: {args.god}")
        return 1
    result = build_troll_build(
        conn,
        items,
        args.role,
        god,
        use_aspect=args.aspect,
        chaos=args.chaos,
    )
    conn.close()

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print(f"=== 😈 {result['troll_title']} ===")
    print(f"{result['god']} · {result['role']} · {result['disclaimer']}")
    if result.get("aspect_name"):
        print(f"Aspect: {result['aspect_name']}")
    print(result.get("monologue") or result.get("why"))
    print(f"Axes: {result['primary_axis']} (+ {result['secondary_axis']})")
    print()
    print("Starter:", result["starter"]["name"] if result.get("starter") else "—")
    for i, it in enumerate(result.get("items") or [], 1):
        print(f"  {i}. {it['name']:28}  {it.get('why', '')}")
    print("Relics:", ", ".join(r["name"] for r in result.get("relics") or []))
    return 0


if __name__ == "__main__":
    raise SystemExit(troll_cli())
