"""
Enemy-team counter builds for Conquest.

Given your god + role + up to 5 enemy god names, analyze damage mix / CC / heal /
crit pressure and re-assemble a kit path with counter cores (Spectral, Genji,
Magi's, Contagion, etc.).
"""

from __future__ import annotations

import re
import sqlite3
from typing import Any

from .conquest_builds import (
    DAMAGE_ROLES_NEED_PEN,
    HARD_MAX_ACTIVE_ITEMS,
    ROLE_PROFILES,
    ScoredItem,
    _canon_stat_value,
    _ensure_pen_in_path,
    _order_buy_path,
    _trim_excess_defense,
    assemble_kit_path,
    build_god_build,
    god_scaling_bias,
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
    is_base_relic,
    _item_card,
)
from .kit_effects import (
    effect_labels,
    explain_item_pick,
    extract_kit_effects,
    item_family,
)


def resolve_god(conn: sqlite3.Connection, name: str) -> dict[str, Any] | None:
    """Fuzzy match god by name (case-insensitive, substring)."""
    n = (name or "").strip()
    if not n:
        return None
    row = conn.execute(
        "SELECT id AS god_id, name AS entity_name, primary_damage_type, pantheon FROM gods WHERE lower(name)=lower(?)",
        (n,),
    ).fetchone()
    if row:
        return dict(row)
    row = conn.execute(
        """
        SELECT id AS god_id, name AS entity_name, primary_damage_type, pantheon
        FROM gods WHERE lower(name) LIKE lower(?)
        ORDER BY length(name) ASC LIMIT 1
        """,
        (f"%{n}%",),
    ).fetchone()
    return dict(row) if row else None


def analyze_ally_team(
    conn: sqlite3.Connection,
    ally_names: list[str],
) -> dict[str, Any]:
    """
    Optional allies — shapes Support/Solo peel priorities (protect ADC/mid).
    """
    gods: list[dict[str, Any]] = []
    missing: list[str] = []
    peel_adc: list[str] = []
    peel_mage: list[str] = []
    for raw in ally_names or []:
        g = resolve_god(conn, raw)
        if not g:
            missing.append(raw)
            continue
        bias = god_scaling_bias(conn, g["god_id"])
        dtype = (g.get("primary_damage_type") or "").lower()
        tags = set(bias.get("tags") or [])
        name = g["entity_name"]
        gods.append(
            {
                "name": name,
                "damage_type": g.get("primary_damage_type"),
                "tags": sorted(tags),
                "scaling": bias.get("primary"),
            }
        )
        is_mage = dtype == "magical" or bias.get("primary") == "Intelligence"
        is_phys = (not is_mage) and (dtype == "physical" or bias.get("primary") == "Strength")
        aaish = bool(tags & {"aa", "as_steroid", "sustained"}) or float(bias.get("aa_score") or 0) >= 0.45
        if is_phys and aaish:
            peel_adc.append(name)
        if is_mage:
            peel_mage.append(name)
        # Role-list hint from wiki roles string if present
        if not peel_adc and is_phys and "carry" in str(g).lower():
            peel_adc.append(name)

    reasons: list[str] = []
    if peel_adc:
        reasons.append(f"Peel for ADC ({', '.join(peel_adc)}): prioritize Spectral / Midgardian")
    if peel_mage:
        reasons.append(f"Peel for mage ({', '.join(peel_mage)}): keep them alive vs divers / magic")
    if not reasons and gods:
        reasons.append("Allies noted — light peel flex")

    return {
        "allies": gods,
        "missing": missing,
        "peel_adc": peel_adc,
        "peel_mage": peel_mage,
        "need_peel_adc": len(peel_adc) >= 1,
        "need_peel_mage": len(peel_mage) >= 1,
        "reasons": reasons,
        "summary": " · ".join(reasons[:3]) if reasons else "",
    }


def analyze_enemy_team(
    conn: sqlite3.Connection,
    enemy_names: list[str],
) -> dict[str, Any]:
    """
    Build a threat profile from enemy god names.
    """
    gods: list[dict[str, Any]] = []
    missing: list[str] = []
    magical = 0
    physical = 0
    tags_all: set[str] = set()
    effects_all: dict[str, float] = {}
    healers: list[str] = []
    cc_gods: list[str] = []
    crit_gods: list[str] = []  # AA / ADC pressure
    mage_names: list[str] = []
    phys_names: list[str] = []

    for raw in enemy_names:
        g = resolve_god(conn, raw)
        if not g:
            missing.append(raw)
            continue
        bias = god_scaling_bias(conn, g["god_id"])
        dtype = (g.get("primary_damage_type") or "").lower()
        tags = set(bias.get("tags") or [])
        effects = bias.get("effects") or extract_kit_effects(bias)
        entry = {
            "name": g["entity_name"],
            "damage_type": g.get("primary_damage_type"),
            "tags": sorted(tags),
            "effects": effects,
            "scaling": bias.get("primary"),
        }
        gods.append(entry)
        tags_all |= tags
        for k, v in effects.items():
            effects_all[k] = max(effects_all.get(k, 0.0), float(v))

        is_mage = dtype == "magical" or bias.get("primary") == "Intelligence"
        is_phys = (not is_mage) and (dtype == "physical" or bias.get("primary") == "Strength")
        if is_mage:
            magical += 1
            mage_names.append(g["entity_name"])
        elif is_phys:
            physical += 1
            phys_names.append(g["entity_name"])
        else:
            # hybrid / unknown — count as both light
            magical += 0.5
            physical += 0.5

        if tags & {"heal", "heavy_heal", "self_sustain"} or effects.get("heal", 0) >= 0.6:
            healers.append(g["entity_name"])
        if tags & {"hard_cc", "high_cc"} or effects.get("hard_cc", 0) >= 0.7:
            cc_gods.append(g["entity_name"])
        # Crit/AA threat: physical AA carries primarily
        if is_phys and (tags & {"aa", "as_steroid", "sustained"} or float(bias.get("aa_score") or 0) >= 0.5):
            crit_gods.append(g["entity_name"])
        if is_mage and tags & {"aa", "as_steroid"}:
            # AA mages still poke; less Spectral, more midgardian optional
            pass

    total = max(len(gods), 1)
    need_mprot = magical >= 2 or magical > physical
    need_pprot = physical >= 2 or (physical >= 1 and magical <= 1)
    need_anti_crit = len(crit_gods) >= 1
    need_antiheal = len(healers) >= 1
    need_magi = len(cc_gods) >= 2 or (len(cc_gods) >= 1 and magical >= 2)
    need_anti_as = need_anti_crit  # Midgardian when ADC present
    # Dive / frontline pressure — shell before antiheal greed (Achilles-class)
    divers = [
        e["name"]
        for e in gods
        if set(e.get("tags") or []) & {"gap_close", "mobile", "execute", "heavy_shield"}
        and (e.get("damage_type") or "").lower() == "physical"
    ]
    need_dive_shell = len(divers) >= 1 and physical >= 2

    reasons: list[str] = []
    if magical >= 3:
        reasons.append(f"Heavy magic ({int(magical)}): Genji / Oni / mprot stack")
    elif magical >= 2:
        reasons.append(f"Magic pressure ({int(magical)}): prioritize magical defense")
    if physical >= 2:
        reasons.append(f"Physical front ({int(physical)}): Breastplate / Spectral / pprot")
    if need_dive_shell:
        reasons.append(
            f"Dive pressure ({', '.join(divers)}): shell first (Breastplate / Midgardian) before antiheal greed"
        )
    if crit_gods:
        reasons.append(f"Crit/AA threat ({', '.join(crit_gods)}): Spectral (+ Midgardian)")
    if healers:
        reasons.append(f"Healing ({', '.join(healers)}): Contagion / Divine Ruin (after shell if diving)")
    if cc_gods:
        reasons.append(f"CC setup ({', '.join(cc_gods)}): Magi's / Mantle / Beads")
    if not reasons:
        reasons.append("Balanced lobby — kit path with light defense flex")

    return {
        "enemies": gods,
        "missing": missing,
        "magical_count": magical,
        "physical_count": physical,
        "mage_names": mage_names,
        "phys_names": phys_names,
        "healers": healers,
        "cc_gods": cc_gods,
        "crit_gods": crit_gods,
        "divers": divers,
        "need_mprot": need_mprot,
        "need_pprot": need_pprot,
        "need_anti_crit": need_anti_crit,
        "need_antiheal": need_antiheal,
        "need_magi": need_magi,
        "need_anti_as": need_anti_as,
        "need_dive_shell": need_dive_shell,
        "magic_ratio": round(magical / total, 2),
        "phys_ratio": round(physical / total, 2),
        "tags_union": sorted(tags_all),
        "top_effects": sorted(effects_all.items(), key=lambda x: -x[1])[:8],
        "reasons": reasons,
        "summary": " · ".join(reasons[:4]),
    }


def counter_score_delta(
    item: ScoredItem,
    threat: dict[str, Any],
    role: str,
    allies: dict[str, Any] | None = None,
) -> tuple[float, list[str]]:
    """Score bonus (and why fragments) for countering the enemy team (+ optional allies)."""
    n = item.name.lower()
    fam = item_family(item.name) or ""
    blob = f"{item.passive} {item.active}".lower()
    delta = 0.0
    why: list[str] = []
    mprot = _canon_stat_value(item.stats, "mprot")
    pprot = _canon_stat_value(item.stats, "pprot")
    pen = item_pen_value(item)
    allies = allies or {}

    def has_key(*keys: str) -> bool:
        return any(k in n for k in keys)

    if threat.get("need_mprot"):
        if fam in ("defense_cdr", "mprot") or has_key("genji", "oni hunter"):
            delta += 72
            why.append("vs magic damage — Genji/Oni line")
        elif mprot >= 40:
            delta += 45
            why.append("high magical protection")
        elif mprot >= 25:
            delta += 22
        if threat.get("magical_count", 0) >= 3 and mprot >= 30:
            delta += 18

    if threat.get("need_pprot"):
        boost = 70 if threat.get("need_dive_shell") else 55
        if fam in ("cdr_def",) or has_key("breastplate", "valor"):
            delta += boost
            why.append("vs physical — Breastplate line")
        elif pprot >= 40:
            delta += 40 + (15 if threat.get("need_dive_shell") else 0)
            why.append("high physical protection")
        elif pprot >= 25:
            delta += 18

    if threat.get("need_anti_crit"):
        if fam == "anti_crit" or has_key("spectral", "nemean"):
            delta += 85
            why.append("anti-crit vs enemy ADC")
        if fam == "anti_as" or has_key("midgardian", "fixblade"):
            # Stronger when divers are autoing you down
            delta += 62 if threat.get("need_dive_shell") else 48
            why.append("cut enemy attack speed")

    if threat.get("need_antiheal"):
        # Soften antiheal priority when dive shell is required — survive first
        ah = 52 if threat.get("need_dive_shell") and role in ("Support", "Solo") else 78
        if fam in ("antiheal", "divine", "contagion") or has_key(
            "contagion", "divine ruin", "pestilence", "brawler", "toxic"
        ):
            delta += ah
            why.append("anti-heal vs enemy sustain")
        elif "heal" in blob and any(k in blob for k in ("reduc", "anti", "curse")):
            delta += 50 if not threat.get("need_dive_shell") else 28
            why.append("healing reduction passive")

    if threat.get("need_magi"):
        if fam in ("magi", "tenacity") or has_key("magi's", "magi ", "mantle of discord"):
            delta += 70
            why.append("anti-CC vs freeze/lockdown")
        elif has_key("mantle"):
            delta += 55
            why.append("anti-CC / mantle")
        ten = _canon_stat_value(item.stats, "ten")
        if ten >= 5:
            delta += 25
            if "tenacity" not in " ".join(why).lower():
                why.append("tenacity")

    # Ally peel: protect YOUR ADC / mid (Support & Solo primarily)
    if role in ("Support", "Solo") and allies:
        if allies.get("need_peel_adc"):
            if fam == "anti_crit" or has_key("spectral", "nemean"):
                delta += 38
                why.append("peel for ally ADC — anti-crit aura")
            if fam == "anti_as" or has_key("midgardian"):
                delta += 32
                why.append("peel for ally ADC — cut enemy AS")
            if has_key("chandra", "thebes", "sovereign", "heartward") or (
                "ally" in blob or "allies" in blob or "aura" in blob
            ):
                delta += 18
        if allies.get("need_peel_mage"):
            if fam in ("defense_cdr", "mprot") or has_key("genji", "oni"):
                delta += 22
            if threat.get("need_dive_shell") and (
                fam in ("cdr_def",) or has_key("breastplate", "midgardian")
            ):
                delta += 16
                if "peel" not in " ".join(why).lower():
                    why.append("peel shell so ally mage freecasts")

    # Support/Solo: lean harder into pure counter defense
    if role in ("Support", "Solo"):
        if item.item_type == "Defensive":
            delta += 12
        # Don't greed glass when countering
        if item.is_active_item and (item.total_cost or 0) >= 3400:
            delta -= 40
    else:
        # Damage roles: counter items as flex, keep pen viable
        if pen >= 8 and (threat.get("need_antiheal") and fam in ("divine", "desolation")):
            delta += 15
        if item.item_type == "Defensive" and pen < 5 and role in DAMAGE_ROLES_NEED_PEN:
            # allow one counter defense but don't flood
            delta -= 8

    return delta, why[:2]


def build_counter_build(
    conn: sqlite3.Connection,
    items: list[dict] | None,
    role: str,
    god: dict,
    enemy_names: list[str],
    ally_names: list[str] | None = None,
) -> dict[str, Any]:
    """
    Full god build re-scored and assembled against an enemy team (+ optional allies).
    """
    if items is None:
        items = load_items(conn)
    threat = analyze_enemy_team(conn, enemy_names)
    allies = analyze_ally_team(conn, ally_names or [])
    # Peel allies amplify anti-crit / AS needs even if enemy ADC is soft-flagged
    if allies.get("need_peel_adc") and role in ("Support", "Solo"):
        threat = dict(threat)
        threat["need_anti_crit"] = True
        threat["need_anti_as"] = True
        extra = list(threat.get("reasons") or [])
        extra.extend(allies.get("reasons") or [])
        threat["reasons"] = extra
        threat["summary"] = " · ".join(extra[:4])
        threat["allies"] = allies
    else:
        threat = dict(threat)
        threat["allies"] = allies
        if allies.get("summary"):
            threat["reasons"] = list(threat.get("reasons") or []) + list(allies.get("reasons") or [])
            threat["summary"] = " · ".join(threat["reasons"][:4])

    profile = ROLE_PROFILES[role]
    bias = god_scaling_bias(conn, god["god_id"])
    dtype = god.get("primary_damage_type")
    primary = bias.get("primary") or ""
    mage = primary == "Intelligence" or (dtype or "").lower() == "magical"
    physical = (primary == "Strength" or (dtype or "").lower() == "physical") and not mage

    # Stash counter reasons on bias for item why lines
    bias = dict(bias)
    bias["counter_threat"] = threat
    bias["counter_allies"] = allies
    bias["counter_mode"] = True

    scored: list[ScoredItem] = []
    counter_whys: dict[str, list[str]] = {}
    for it in items:
        base = score_item_for_role(it, role, profile)
        base.role_score = rescore_for_god(base, bias, role, damage_type=dtype)
        cdelta, cwhy = counter_score_delta(base, threat, role, allies=allies)
        base.role_score += cdelta
        if cwhy:
            counter_whys[base.name] = cwhy
        scored.append(base)
    scored.sort(key=lambda x: x.role_score, reverse=True)

    starters = [s for s in scored if is_t1_starter(next(i for i in items if i["name"] == s.name))]
    starter_pick = pick_god_starter(starters, items, profile, bias, role, dtype)
    # High-CC lobby: auto-attack LS starters (Death's Toll / Leather / Vamp) get
    # shut down — can't free-hit. Prefer Warrior's Axe / Conduit / shell starters.
    heavy_cc = bool(threat.get("need_magi")) or len(threat.get("cc_gods") or []) >= 2
    for s in starters:
        raw = next(i for i in items if i["name"] == s.name)
        s.role_score = score_starter(raw, profile, role=role)
        nlow = s.name.lower()
        if heavy_cc and any(k in nlow for k in ("death", "leather", "vampiric", "shroud", "gilded")):
            s.role_score -= 55
        if heavy_cc and role == "Solo" and any(k in nlow for k in ("warrior", "axe", "bluestone")):
            s.role_score += 35
        if heavy_cc and role in ("Mid", "Carry") and any(
            k in nlow for k in ("conduit", "sands", "bluestone")
        ):
            s.role_score += 20
    starters.sort(key=lambda x: x.role_score, reverse=True)
    if heavy_cc and starters:
        starter_pick = starters[0]
    if starter_pick:
        starters = [starter_pick] + [s for s in starters if s.name != starter_pick.name]

    t3 = [s for s in scored if is_t3_core(next(i for i in items if i["name"] == s.name))]
    # Soft kit filter via building normal then counter-inject is simpler: reuse assemble
    # but first strip banned glass on support counter
    if role == "Support":
        t3 = [
            s
            for s in t3
            if not any(k in s.name.lower() for k in ("deathbringer", "dreamer", "parashu"))
        ]

    max_act = max_shop_actives_for_god(role, dtype, bias)
    path, archetype = assemble_kit_path(
        t3, bias, role, mage=mage, physical=physical, max_actives=max_act
    )
    path = _inject_counter_cores(
        path, t3, threat, role, max_act, mage=mage, physical=physical, allies=allies
    )
    path = _ensure_pen_in_path(path, t3, role, max_act, mage=mage, physical=physical)
    if role in DAMAGE_ROLES_NEED_PEN:
        # allow 2 defense when hard-countering ADC+mages
        max_def = 2 if (threat.get("need_anti_crit") and threat.get("need_mprot")) else 1
        path = _trim_excess_defense(path, t3, max_defense=max_def, max_actives=max_act)
    path = _order_buy_path(path, role)

    pen_total = sum(item_pen_value(x) for x in path)
    n_act = sum(1 for x in path if x.is_active_item)
    effects = bias.get("effects") or extract_kit_effects(bias)

    # Cards with kit why + counter why
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
        cbits = counter_whys.get(it.name) or []
        # Recompute counter why if missing (injected items)
        if not cbits:
            _, cbits = counter_score_delta(it, threat, role, allies=allies)
        if cbits:
            why = f"{cbits[0]}" + (f"; {base_why}" if base_why and cbits[0] not in base_why else "")
        else:
            why = base_why
        card = _item_card(it, why=why[:180])
        if card:
            card["counter"] = bool(cbits)
            path_cards.append(card)

    starter_card = None
    if starters:
        sw = explain_item_pick(
            starters[0].name, bias=bias, role=role, effects=effects, is_starter=True
        )
        if heavy_cc and any(
            k in starters[0].name.lower() for k in ("warrior", "axe", "conduit", "bluestone", "sands")
        ):
            sw = "vs heavy CC — shell starter (LS starters get locked out)"
        elif heavy_cc and any(
            k in starters[0].name.lower() for k in ("death", "leather", "vampiric")
        ):
            sw = "⚠ LS starter is weak into this CC lobby"
        starter_card = _item_card(starters[0], why=sw)

    relics = [s for s in scored if is_base_relic(next(i for i in items if i["name"] == s.name))]
    for r in relics:
        r.role_score = score_relic(next(i for i in items if i["name"] == r.name), profile)
        # Counter relic bias
        if threat.get("need_magi") and "bead" in r.name.lower():
            r.role_score += 40
        if threat.get("need_anti_crit") and "aegis" in r.name.lower():
            r.role_score += 28
        if bias.get("mobility", 0) == 0 and "blink" in r.name.lower():
            r.role_score += 10
    relics.sort(key=lambda x: x.role_score, reverse=True)

    # Baseline for comparison
    baseline = build_god_build(conn, items, role, god)

    return {
        "god": god.get("entity_name") or god.get("name"),
        "role": role,
        "mode": "counter",
        "archetype": archetype,
        "kit_tags": sorted(bias.get("tags") or []),
        "kit_effects": bias.get("effect_labels") or effect_labels(effects),
        "damage_type": dtype,
        "scaling": bias.get("primary"),
        "threat": threat,
        "allies": allies,
        "starter": starter_card,
        "items": path_cards,
        "full_path": path_cards,
        "relics": [_item_card(r) for r in relics[:2]],
        "max_shop_actives": max_act,
        "hard_max_actives": HARD_MAX_ACTIVE_ITEMS,
        "active_count": n_act,
        "pen_total": round(pen_total, 1),
        "baseline_items": [it["name"] for it in (baseline.get("items") or [])],
        "why": (
            f"Counter path for {god.get('entity_name') or god.get('name')} {role}. "
            f"{threat.get('summary', '')}. "
            f"Enemies: {', '.join(e['name'] for e in threat.get('enemies') or []) or '—'}."
        ),
    }


def _inject_counter_cores(
    path: list[ScoredItem],
    pool: list[ScoredItem],
    threat: dict[str, Any],
    role: str,
    max_actives: int,
    *,
    mage: bool,
    physical: bool,
    allies: dict[str, Any] | None = None,
) -> list[ScoredItem]:
    """Force 1–3 highest-priority counter items into the path."""
    path = list(path)
    seen = {x.name for x in path}
    actives = sum(1 for x in path if x.is_active_item)
    allies = allies or threat.get("allies") or {}

    # Priority order: survive dive + turret poke BEFORE antiheal greed.
    # Lesson: Contagion-first loses to Achilles dive + Vulcan turrets.
    wanted: list[str] = []  # family or name keys in priority order
    dive = bool(threat.get("need_dive_shell"))
    peel_adc = bool(allies.get("need_peel_adc"))
    if threat.get("need_pprot") and role in ("Support", "Solo", "Jungle"):
        wanted.append("breastplate")
    if threat.get("need_mprot") and threat.get("magical_count", 0) >= 2:
        wanted.append("genji")
        if threat.get("magical_count", 0) >= 3:
            wanted.append("oni")
    if (dive or peel_adc) and role in ("Support", "Solo"):
        wanted.append("midgardian")
    if threat.get("need_anti_crit") or peel_adc:
        wanted.append("spectral")
    if threat.get("need_anti_as") and role in ("Support", "Solo") and "midgardian" not in wanted:
        wanted.append("midgardian")
    if threat.get("need_antiheal"):
        wanted.append("contagion" if role in ("Support", "Solo") else "divine")
    if threat.get("need_magi"):
        wanted.append("magi")

    # Deduplicate keys
    seen_keys: list[str] = []
    for k in wanted:
        if k not in seen_keys:
            seen_keys.append(k)

    # Frontline can take more counter cores when diving + magic
    max_inject = 4 if role in ("Support", "Solo") and dive else (3 if role in ("Support", "Solo") else 2)
    injected = 0
    for key in seen_keys:
        if injected >= max_inject:
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
        # Drop lowest priority non-pen (damage) or luxury
        drop_idx = None
        pen_idxs = [i for i, it in enumerate(path) if is_pen_item(it)]
        for i, it in enumerate(path):
            if it.is_active_item and (it.total_cost or 0) >= 3200:
                drop_idx = i
                break
        if drop_idx is None:
            ranked = sorted(range(len(path)), key=lambda i: path[i].role_score)
            for i in ranked:
                if role in DAMAGE_ROLES_NEED_PEN and len(pen_idxs) <= 1 and i in pen_idxs:
                    continue
                # don't drop another counter core we just care about
                nlow = path[i].name.lower()
                if any(k in nlow for k in ("spectral", "genji", "contagion", "magi", "divine")):
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

    return path[:6]


def counter_cli(argv: list[str] | None = None) -> int:
    """python -m smite2db.counter_builds Charon Support Discordia Merlin Ymir Artemis Ganesha --allies Medusa Poseidon"""
    import argparse
    import json
    from .db import connect

    p = argparse.ArgumentParser(description="SMITE 2 counter build")
    p.add_argument("god", help="Your god name")
    p.add_argument("role", choices=["Carry", "Mid", "Jungle", "Solo", "Support"])
    p.add_argument("enemies", nargs="+", help="Enemy god names (up to 5)")
    p.add_argument(
        "--allies",
        nargs="*",
        default=[],
        help="Optional ally god names (peel priorities for Support/Solo)",
    )
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    conn = connect()
    items = load_items(conn)
    god = resolve_god(conn, args.god)
    if not god:
        print(f"God not found: {args.god}")
        return 1
    enemies = args.enemies[:5]
    result = build_counter_build(
        conn, items, args.role, god, enemies, ally_names=list(args.allies or [])
    )
    conn.close()

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print(f"=== {result['god']} {result['role']} COUNTER ===")
    print(result["why"])
    print()
    th = result["threat"]
    print("Threat:", th.get("summary"))
    for r in th.get("reasons") or []:
        print("  -", r)
    if th.get("missing"):
        print("  (missing names:", ", ".join(th["missing"]), ")")
    print()
    print("Starter:", result["starter"]["name"] if result.get("starter") else "—")
    for i, it in enumerate(result.get("items") or [], 1):
        flag = "★" if it.get("counter") else " "
        print(f"  {i}. {flag} {it['name']:28}  {it.get('why', '')}")
    print("Relics:", ", ".join(r["name"] for r in result.get("relics") or []))
    base = result.get("baseline_items") or []
    if base:
        print("Baseline (no counter):", " → ".join(base))
    return 0


if __name__ == "__main__":
    raise SystemExit(counter_cli())
