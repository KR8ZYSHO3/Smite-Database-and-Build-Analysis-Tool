"""
Simple ability leveling priority per god (kit-heuristic).

Output is light UI text like:
  priority: 4 > 3 > 1 > 2
  order:    1/3/2/3/4/3/3/3/4/1/1/1/1/4/2/2/2/2/4/4

Rules (SMITE-style):
  - Levels 1–20, one point each level
  - Ult (4) ranks at levels 5, 9, 13, 17, 20
  - Abilities 1/2/3 max at rank 5
"""

from __future__ import annotations

import re
import sqlite3
from typing import Any

# Ult point levels (1-indexed player level)
ULT_LEVELS = (5, 9, 13, 17, 20)


def _slot_num(slot: str | None) -> int | None:
    s = (slot or "").lower()
    if "ultimate" in s or s.strip() in {"4", "ult", "r"}:
        return 4
    if "1st" in s or s.strip() == "1":
        return 1
    if "2nd" in s or s.strip() == "2":
        return 2
    if "3rd" in s or s.strip() == "3":
        return 3
    # skip basic / passive / alt forms for leveling grid
    return None


def _ability_priority_score(
    row: sqlite3.Row | dict[str, Any],
    *,
    role: str | None,
    tags: set[str],
) -> float:
    """Higher = max sooner among abilities 1/2/3."""
    get = row.__getitem__ if hasattr(row, "keys") else row.get  # type: ignore[attr-defined]
    power = float(get("power_score") or 0)
    burst = float(get("burst_proxy") or 0)
    dps = float(get("dps_proxy") or 0)
    util = float(get("utility_score") or 0)
    cd = float(get("cooldown_rank5") or 14)
    dmg = float(get("damage_rank5") or 0)
    desc = f"{get('description') or ''} {get('name') or ''}".lower()

    # Support: dampen raw burst so link/heal/CC beat pure poke
    if role == "Support":
        score = power * 0.35 + burst * 0.1 + dps * 0.1 + util * 0.45
        score += min(dmg, 800) * 0.008
    else:
        score = power * 1.0 + burst * 0.35 + dps * 0.25 + util * 0.15
        score += min(dmg, 800) * 0.02
    # Prefer spammy damage
    if cd > 0:
        score += max(0.0, (16.0 - min(cd, 20.0))) * (0.6 if role == "Support" else 1.2)

    # Role / kit nudges
    if role == "Support":
        if get("has_heal"):
            score += 40
        if get("has_shield"):
            score += 18
        if "kiss" in desc or "link" in desc or "soul mate" in desc or "beloved" in desc:
            score += 80  # Aphro-style link — usually max before poke
        if get("has_cc"):
            score += 10
    elif role in ("Carry", "Jungle"):
        if any(k in desc for k in ("attack speed", "basic attack damage", "attack damage")):
            score += 24  # AA steroids matter even if power_score is low
        if "aa" in tags or "as_steroid" in tags:
            if any(k in desc for k in ("attack speed", "movement speed", "steroid")):
                score += 16
        # Hunter 2 often is the AS steroid with low power_score — max 2nd
        if "attack speed" in desc and power <= 5:
            score += 55

    elif role == "Mid":
        if get("has_dot"):
            score += 6
        if dmg >= 250:
            score += 8
    elif role == "Solo":
        if get("has_heal") or "self" in desc and "heal" in desc:
            score += 12
        if get("has_cc"):
            score += 6

    # Clear / wave tools slightly preferred early for 1st ability if close
    if get("slot") and "1st" in str(get("slot")).lower():
        score += 3

    # Pure utility with no damage/heal ranks lower unless steroid/heal/cc already boosted
    if power <= 0 and dmg <= 0 and not get("has_heal") and not get("has_shield"):
        if any(k in desc for k in ("attack speed", "movement speed", "immune", "protections")):
            score += 18
        else:
            score -= 8

    return score


def _load_levelable_abilities(
    conn: sqlite3.Connection, god_id: int
) -> dict[int, dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT a.slot, a.slot_order, a.name, a.description,
               m.damage_rank5, m.scaling_str_pct, m.scaling_int_pct,
               m.cooldown_rank5, m.power_score, m.burst_proxy, m.dps_proxy,
               m.utility_score, m.has_cc, m.has_heal, m.has_shield,
               m.has_mobility, m.has_dot
        FROM abilities a
        LEFT JOIN ability_metrics m ON m.ability_id = a.id
        WHERE a.god_id = ?
        ORDER BY a.slot_order
        """,
        (int(god_id),),
    ).fetchall()
    out: dict[int, dict[str, Any]] = {}
    for r in rows:
        n = _slot_num(r["slot"])
        if n is None:
            continue
        # Prefer primary form over Alt (higher slot_order alts skipped if primary exists)
        if n in out and int(r["slot_order"] or 0) >= 900:
            continue
        out[n] = dict(r)
        out[n]["_num"] = n
    return out


def build_level_sequence(max_order: list[int]) -> list[int]:
    """
    max_order: priority among [1,2,3] highest first, e.g. [3,1,2].
    Ult (4) is always taken at ULT_LEVELS.
    Returns 20 ability numbers for levels 1..20.
    """
    avail = [n for n in max_order if n in (1, 2, 3)]
    for n in (1, 2, 3):
        if n not in avail:
            avail.append(n)
    ranks = {1: 0, 2: 0, 3: 0, 4: 0}
    seq: list[int] = []

    for lvl in range(1, 21):
        if lvl in ULT_LEVELS and ranks[4] < 5:
            ranks[4] += 1
            seq.append(4)
            continue
        unlocked = sum(1 for a in (1, 2, 3) if ranks[a] > 0)
        # Levels 1–3: unlock top priority first, then the other two
        if unlocked < 3 and lvl <= 3:
            for ab in avail:
                if ranks[ab] == 0:
                    ranks[ab] = 1
                    seq.append(ab)
                    break
            continue
        # Otherwise max in priority order
        placed = False
        for ab in avail:
            if ranks[ab] < 5:
                ranks[ab] += 1
                seq.append(ab)
                placed = True
                break
        if not placed:
            for ab in (1, 2, 3, 4):
                if ranks[ab] < 5:
                    ranks[ab] += 1
                    seq.append(ab)
                    break
    return seq

def compute_skill_order(
    conn: sqlite3.Connection,
    god_id: int,
    *,
    role: str | None = None,
    tags: list[str] | set[str] | None = None,
) -> dict[str, Any] | None:
    abs_map = _load_levelable_abilities(conn, god_id)
    if not all(n in abs_map for n in (1, 2, 3, 4)):
        # Incomplete kit scrape — skip rather than invent
        present = sorted(abs_map)
        if len(present) < 3:
            return None

    tagset = {str(t).lower() for t in (tags or [])}
    scored: list[tuple[float, int, str]] = []
    for n in (1, 2, 3):
        if n not in abs_map:
            continue
        sc = _ability_priority_score(abs_map[n], role=role, tags=tagset)
        scored.append((sc, n, abs_map[n].get("name") or f"Ability {n}"))
    if not scored:
        return None
    scored.sort(key=lambda x: (-x[0], x[1]))
    max_order = [n for _, n, _ in scored]
    # Ensure all three appear
    for n in (1, 2, 3):
        if n in abs_map and n not in max_order:
            max_order.append(n)

    seq = build_level_sequence(max_order)
    # Compact display: 1/3/2/3/4/3/3/3/4/...
    order_str = "/".join(str(x) for x in seq)
    # Priority line always leads with ult
    priority = "4 > " + " > ".join(str(n) for n in max_order)
    top = scored[0]
    names = {n: abs_map[n].get("name") for n in abs_map}
    note = f"Max {top[1]} ({top[2]}) first; take ult at 5/9/13/17/20."

    return {
        "skill_priority": priority,
        "skill_order": order_str,
        "skill_order_list": seq,
        "skill_max_order": max_order,
        "skill_note": note,
        "skill_names": {
            "1": names.get(1),
            "2": names.get(2),
            "3": names.get(3),
            "4": names.get(4),
        },
    }


def format_skill_order_light(data: dict[str, Any] | None) -> str:
    if not data:
        return ""
    return str(data.get("skill_order") or "")
