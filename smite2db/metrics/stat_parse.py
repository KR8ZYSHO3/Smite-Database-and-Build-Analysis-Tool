"""Parse ability/item stat strings into numeric features."""

from __future__ import annotations

import re
from typing import Any


def rank_values(text: str) -> list[float]:
    """Extract '70 | 115 | 160 | 205 | 250' or '70/115/160/205/250' style lists."""
    if not text:
        return []
    # Prefer pipe-separated rank ladders
    if "|" in text:
        parts = [p.strip() for p in text.split("|")]
    elif re.search(r"\d\s*/\s*\d", text):
        parts = [p.strip() for p in text.split("/")]
    else:
        m = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
        return [float(m.group())] if m else []
    out: list[float] = []
    for p in parts:
        m = re.search(r"-?\d+(?:\.\d+)?", p.replace(",", ""))
        if m:
            out.append(float(m.group()))
    return out


def first_number(text: str) -> float | None:
    if not text:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
    return float(m.group()) if m else None


def parse_scaling(text: str) -> dict[str, float]:
    """
    Parse scaling like:
      '60% Intelligence'
      '100% Strength + 20% Intelligence + 100% Attack Damage'
      '30% per tick'
    """
    result = {"str": 0.0, "int": 0.0, "other": 0.0}
    if not text:
        return result
    t = text.lower()
    for m in re.finditer(
        r"(\d+(?:\.\d+)?)\s*%\s*(strength|str|intelligence|int|attack damage|power|max health|max mana|protections?)",
        t,
    ):
        val = float(m.group(1))
        kind = m.group(2)
        if kind in ("strength", "str"):
            result["str"] += val
        elif kind in ("intelligence", "int"):
            result["int"] += val
        else:
            result["other"] += val
    # bare "60% INT" style
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*%\s*int\b", t):
        result["int"] += float(m.group(1))
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*%\s*str\b", t):
        result["str"] += float(m.group(1))
    return result


def get_stat(stats: dict[str, str] | None, *keys: str) -> str:
    if not stats:
        return ""
    lower_map = {k.lower(): v for k, v in stats.items()}
    for key in keys:
        if key.lower() in lower_map:
            return lower_map[key.lower()]
    # partial match
    for key in keys:
        for k, v in lower_map.items():
            if key.lower() in k:
                return v
    return ""


CC_KEYWORDS = (
    "stun",
    "root",
    "slow",
    "silence",
    "disarm",
    "knockup",
    "knock up",
    "knockback",
    "knock back",
    "fear",
    "taunt",
    "cripple",
    "polymorph",
    "mesmerize",
    "tremble",
    "grab",
    "pull",
    "banish",
    "daze",
    "blind",
    "intoxicate",
)
HEAL_KEYWORDS = ("heal", "lifesteal", "hp5", "health regen", "restore health")
SHIELD_KEYWORDS = ("shield", "protections", "damage mitigation", "damage reduction")
MOBILITY_KEYWORDS = (
    "dash",
    "leap",
    "teleport",
    "blink",
    "movement speed",
    "hasten",
    "jump",
    "fly",
    "deploy",
    "charge forward",
    "charges forward",
    "lunges",
    "rushes",
)
DOT_KEYWORDS = ("per tick", "over time", "every second", "damage over time", "dot")


def text_flags(blob: str) -> dict[str, bool]:
    t = (blob or "").lower()
    return {
        "has_cc": any(k in t for k in CC_KEYWORDS),
        "has_heal": any(k in t for k in HEAL_KEYWORDS),
        "has_shield": any(k in t for k in SHIELD_KEYWORDS),
        "has_mobility": any(k in t for k in MOBILITY_KEYWORDS),
        "has_dot": any(k in t for k in DOT_KEYWORDS),
    }


def extract_from_to(text: str) -> tuple[float, float] | None:
    """Detect 'from X to Y' numeric changes for magnitude estimation."""
    m = re.search(
        r"from\s+(-?\d+(?:\.\d+)?)\s*(?:%|s|seconds?)?\s+to\s+(-?\d+(?:\.\d+)?)",
        text,
        re.I,
    )
    if m:
        return float(m.group(1)), float(m.group(2))
    # multi-rank: take first numbers of each ladder
    m = re.search(
        r"from\s+([\d./| ]+?)\s+to\s+([\d./| ]+)",
        text,
        re.I,
    )
    if m:
        a = rank_values(m.group(1))
        b = rank_values(m.group(2))
        if a and b:
            return a[-1], b[-1]
    return None


def clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    if not b:
        return default
    return a / b


def normalize_minmax(values: list[float]) -> list[float]:
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi - lo < 1e-9:
        return [50.0 for _ in values]
    return [100.0 * (v - lo) / (hi - lo) for v in values]


def parse_ability_features(
    stats_json: dict[str, str] | None,
    stats_text: str,
    description: str,
    notes: str,
    short_label: str,
) -> dict[str, Any]:
    stats = stats_json or {}
    if not stats and stats_text:
        stats = {}
        for line in stats_text.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                stats[k.strip()] = v.strip()

    dmg_raw = get_stat(stats, "Damage", "Damage per Tick", "Initial Damage", "Explosion Damage")
    ranks = rank_values(dmg_raw)
    dmg1 = ranks[0] if ranks else None
    dmg5 = ranks[-1] if ranks else None

    scaling_raw = get_stat(stats, "Damage Scaling", "Scaling", "Heal Scaling")
    scaling = parse_scaling(scaling_raw)
    # also scan full stats text for scaling mentions
    if scaling["str"] == 0 and scaling["int"] == 0:
        scaling = parse_scaling(stats_text or "")

    cd_raw = get_stat(stats, "Cooldown")
    cd_ranks = rank_values(cd_raw)
    cd1 = cd_ranks[0] if cd_ranks else first_number(cd_raw)
    cd5 = cd_ranks[-1] if cd_ranks else cd1

    cost_raw = get_stat(stats, "Cost", "Mana Cost")
    cost_ranks = rank_values(cost_raw)
    cost5 = cost_ranks[-1] if cost_ranks else first_number(cost_raw)

    range_m = first_number(get_stat(stats, "Range"))
    radius_m = first_number(get_stat(stats, "Radius", "Area"))

    blob = " ".join(
        filter(
            None,
            [stats_text, description, notes, short_label, " ".join(f"{k}:{v}" for k, v in stats.items())],
        )
    )
    flags = text_flags(blob)

    # Offensive proxies
    scale_factor = 1.0 + (scaling["str"] + scaling["int"] + scaling["other"]) / 100.0
    burst = (dmg5 or 0.0) * scale_factor
    dps = safe_div(burst, cd5 or 12.0)

    utility = 0.0
    if flags["has_cc"]:
        utility += 35
    if flags["has_heal"]:
        utility += 20
    if flags["has_shield"]:
        utility += 15
    if flags["has_mobility"]:
        utility += 20
    if flags["has_dot"]:
        utility += 10
    utility = clamp(utility)

    # power score heuristic before global normalization
    power_raw = burst * 0.6 + dps * 8.0 + (50.0 if flags["has_cc"] and (dmg5 or 0) > 0 else 0)

    return {
        "damage_rank1": dmg1,
        "damage_rank5": dmg5,
        "scaling_str_pct": scaling["str"],
        "scaling_int_pct": scaling["int"],
        "scaling_other_pct": scaling["other"],
        "cooldown_rank1": cd1,
        "cooldown_rank5": cd5,
        "mana_cost_rank5": cost5,
        "range_m": range_m,
        "radius_m": radius_m,
        **{k: int(v) for k, v in flags.items()},
        "dps_proxy": dps,
        "burst_proxy": burst,
        "utility_score": utility,
        "power_raw": power_raw,
        "stats_parsed": stats,
    }
