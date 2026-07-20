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


# Hard CC (crowd control that stops actions) vs soft (slow)
HARD_CC_RE = re.compile(
    r"\b(stun|root|silence|disarm|knock(?:\s|-)?up|knock(?:\s|-)?back|"
    r"fear|taunt|cripple|polymorph|mesmerize|tremble|grab|pull|banish|"
    r"daze|blind|intoxicate|freeze|petrif)\w*\b",
    re.I,
)
SOFT_CC_RE = re.compile(r"\bslows?\b|\bslowed\b", re.I)

# Heal: must be restorative, not "health threshold" / "max health damage"
HEAL_RE = re.compile(
    r"\b(heals?|healing|lifesteal|life steal|hp5|health regen|"
    r"restore(?:s|d)? (?:your |ally |allies[' ]|their )?health|"
    r"restor(?:e|es|ed) \d|gain(?:s|ing)? health|"
    r"heal yourself|heal(?:s|ing)? (?:you|allies|nearby))\b",
    re.I,
)
# False-positive blockers for heal
HEAL_NEG_RE = re.compile(
    r"\b(health threshold|max health damage|% of (?:the )?enemy|"
    r"based on (?:missing |max )?health|execute|low health)\b",
    re.I,
)

# Shield: actual shields/barriers — NOT enemy protection shred or "gain protections"
SHIELD_RE = re.compile(
    r"\b(shields?|barrier|absorb(?:s|ing)? (?:damage|hits)|"
    r"damage absorption|protective shield|gain a shield|gains a shield)\b",
    re.I,
)
# "gain protections" is real defensive buff but not a shield itemization cue
PROT_BUFF_RE = re.compile(
    r"\b(gain(?:s|ing)? (?:physical |magical |additional )?protections?|"
    r"increased (?:physical |magical )?protections?|"
    r"damage mitigation|mitigat(?:e|es|ion)\b)",
    re.I,
)
# Enemy shred — must NOT count as shield
SHRED_RE = re.compile(
    r"\b(reduc(?:e|es|ing) (?:their |enemy |the )?(?:physical |magical )?protections?|"
    r"protection reduction|shred|voids? their)\b",
    re.I,
)

# Mobility: true relocation / MS steroid on self
MOBILITY_RE = re.compile(
    r"\b(dash(?:es|ing)?|leap(?:s|ing)?|teleport(?:s|ing)?|blink(?:s|ing)?|"
    r"fly into|flies? |jump(?:s|ing)? (?:to|forward|back)|"
    r"charge(?:s|ing)? forward|lunge(?:s|ing)?|rush(?:es|ing)? forward|"
    r"movement speed|move speed|hasten)\b",
    re.I,
)
MOBILITY_NEG_RE = re.compile(
    r"\b(enemy|enemies|their) (?:movement|move) speed|"
    r"reduc(?:e|es|ing) (?:enemy |their )?movement\b",
    re.I,
)

DOT_RE = re.compile(
    r"\b(per tick|damage over time|every second|over \d+ seconds|"
    r"damage per tick|tick damage|poison|burn(?:ing|s)?|blight)\b",
    re.I,
)

# Stats keys that contribute flat damage (not scaling / reduction)
_DAMAGE_KEY_OK = re.compile(
    r"damage|tick damage|corpse damage|hit damage|explosion|impact damage",
    re.I,
)
_DAMAGE_KEY_BAD = re.compile(
    r"scaling|reduction|reduced|mitigation|threshold|dealt reduction|"
    r"bonus damage scaling|increase from|taken",
    re.I,
)


def is_damage_stat_key(key: str) -> bool:
    kl = (key or "").strip().lower()
    if not kl or _DAMAGE_KEY_BAD.search(kl):
        return False
    return bool(_DAMAGE_KEY_OK.search(kl))


def is_scaling_stat_key(key: str) -> bool:
    kl = (key or "").strip().lower()
    if kl in (
        "damage scaling",
        "damage scaling per tick",
        "tick damage scaling",
        "corpse damage scaling",
        "heal scaling",
        "scaling",
    ):
        return True
    return "scaling" in kl and "damage" in kl


def text_flags(blob: str) -> dict[str, bool]:
    """Boolean kit flags with tighter patterns (fewer false positives)."""
    t = blob or ""
    has_hard = bool(HARD_CC_RE.search(t))
    has_soft = bool(SOFT_CC_RE.search(t))
    has_heal = bool(HEAL_RE.search(t)) and not (
        HEAL_NEG_RE.search(t) and not HEAL_RE.search(t)
    )
    # if only health-threshold language, drop heal
    if HEAL_NEG_RE.search(t) and not re.search(
        r"\b(heals?|healing|lifesteal|restore(?:s|d)? (?:your |ally ))\b", t, re.I
    ):
        has_heal = False
    has_shield = bool(SHIELD_RE.search(t))
    # prot buff is utility but not shield for itemization
    has_prot_buff = bool(PROT_BUFF_RE.search(t)) and not SHRED_RE.search(t)
    has_mobility = bool(MOBILITY_RE.search(t))
    if has_mobility and MOBILITY_NEG_RE.search(t):
        # if only enemy MS reduction, not self mobility
        if not re.search(
            r"\b(you |your |self |dash|leap|teleport|blink|charge forward)\b", t, re.I
        ):
            has_mobility = False
    has_dot = bool(DOT_RE.search(t))
    return {
        "has_cc": has_hard or has_soft,
        "has_hard_cc": has_hard,
        "has_heal": has_heal,
        "has_shield": has_shield,
        "has_prot_buff": has_prot_buff,
        "has_mobility": has_mobility,
        "has_dot": has_dot,
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


def normalize_winsorized(values: list[float], p_lo: float = 0.05, p_hi: float = 0.95) -> list[float]:
    """
    Min-max after clipping outliers to percentile bounds.
    Stops one 4000-burst ult from pinning every other god near 0.
    """
    if not values:
        return []
    if len(values) < 8:
        return normalize_minmax(values)
    ordered = sorted(values)
    n = len(ordered)
    lo = ordered[max(0, int(n * p_lo))]
    hi = ordered[min(n - 1, int(n * p_hi))]
    if hi - lo < 1e-9:
        return normalize_minmax(values)
    clipped = [min(hi, max(lo, v)) for v in values]
    return normalize_minmax(clipped)


def _duration_seconds(stats: dict[str, str], stats_text: str) -> float | None:
    """Best-effort ability/field duration (rank 5 when ladder)."""
    for key in (
        "Duration",
        "Debuff Duration",
        "Buff Duration",
        "Field Duration",
        "Pulse Duration",
        "Lifetime",
    ):
        raw = get_stat(stats, key)
        if not raw:
            continue
        ranks = rank_values(raw)
        if ranks:
            # duration ladders often decrease with rank (Whirlwind 15|…|11)
            return ranks[-1]
        n = first_number(raw)
        if n is not None and 0 < n <= 120:
            return n
    m = re.search(
        r"(?:duration|over|for)\s+(\d+(?:\.\d+)?)\s*(?:s|sec|seconds)?",
        stats_text or "",
        re.I,
    )
    if m:
        v = float(m.group(1))
        if 0 < v <= 120:
            return v
    return None


def _tick_interval(stats: dict[str, str], stats_text: str) -> float:
    raw = get_stat(stats, "Tick Rate", "Tick Interval", "Interval")
    if raw:
        n = first_number(raw)
        if n and n > 0:
            return n
    m = re.search(r"every\s+(\d+(?:\.\d+)?)\s*(?:s|sec|seconds)?", stats_text or "", re.I)
    if m:
        n = float(m.group(1))
        if n > 0:
            return n
    return 1.0  # SMITE DoTs usually 1/s


def sum_ability_damage(stats: dict[str, str], stats_text: str) -> dict[str, Any]:
    """
    Sum multi-part damage (initial + ticks + corpse + bonus) at rank 1/5.

    DoT lines (per tick) are expanded by duration / tick interval.
    % max-health ticks get a small proxy so DoT kits aren't zeroed.
    """
    if not stats and stats_text:
        stats = {}
        for line in stats_text.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                stats[k.strip()] = v.strip()

    duration = _duration_seconds(stats, stats_text)
    interval = _tick_interval(stats, stats_text)
    # Default DoT lifetime when wiki omits Duration (some fields only list Cooldown ladders)
    default_dot_ticks = 5.0
    ticks = 1.0
    if duration and duration > 0:
        ticks = max(1.0, duration / max(interval, 0.25))
        # Cap insane channel ults (don't treat 110s as 110 full ticks at full value)
        ticks = min(ticks, 12.0)
    else:
        ticks = default_dot_ticks  # applied only to tick lines below

    total1 = 0.0
    total5 = 0.0
    parts: list[dict[str, Any]] = []
    scale_str = 0.0
    scale_int = 0.0
    scale_other = 0.0

    for key, val in stats.items():
        if is_scaling_stat_key(key):
            sc = parse_scaling(val)
            # Prefer primary damage scaling; stack all damage scalings
            scale_str += sc["str"]
            scale_int += sc["int"]
            scale_other += sc["other"]
            continue
        if not is_damage_stat_key(key):
            continue
        ranks = rank_values(val)
        if not ranks:
            continue
        d1 = ranks[0]
        d5 = ranks[-1]
        kl = key.lower()
        is_tick = "tick" in kl or "per second" in kl or "per tick" in kl
        # percent-of-health style (values like 1|2|3 %)
        is_pct_hp = "%" in (val or "") or "max health" in kl
        if is_pct_hp and d5 <= 20:
            # proxy: 1% ≈ 25 "damage units" for relative ranking
            d1, d5 = d1 * 25.0, d5 * 25.0
            is_tick = is_tick or "tick" in kl

        if is_tick:
            mult = ticks if (duration and duration > 0) else default_dot_ticks
        else:
            mult = 1.0
        # Multi-hit non-tick ("4 times") from key/value rarely present — leave mult=1
        contrib1 = d1 * mult
        contrib5 = d5 * mult
        total1 += contrib1
        total5 += contrib5
        parts.append(
            {
                "key": key,
                "d1": d1,
                "d5": d5,
                "mult": mult,
                "is_tick": is_tick,
            }
        )

    # Fallback: original single-key path
    if total5 <= 0:
        dmg_raw = get_stat(
            stats,
            "Damage",
            "Damage per Tick",
            "Damage Per Tick",
            "Tick Damage",
            "Initial Damage",
            "Explosion Damage",
            "Corpse Damage",
            "Bonus Damage",
        )
        ranks = rank_values(dmg_raw)
        if ranks:
            total1 = ranks[0]
            total5 = ranks[-1]
            if re.search(r"tick|per tick|per second", dmg_raw + get_stat(stats, "Damage"), re.I) or (
                "Damage Per Tick" in stats or "Damage per Tick" in stats or "Tick Damage" in stats
            ):
                total1 *= ticks
                total5 *= ticks

    if scale_str == 0 and scale_int == 0:
        # damage-scaling keys only, not full blob (avoids unrelated % )
        for key, val in stats.items():
            if is_scaling_stat_key(key) or (
                "scaling" in key.lower() and "heal" not in key.lower()
            ):
                sc = parse_scaling(val)
                scale_str += sc["str"]
                scale_int += sc["int"]
                scale_other += sc["other"]
        if scale_str == 0 and scale_int == 0:
            sc = parse_scaling(
                get_stat(stats, "Damage Scaling", "Damage Scaling Per Tick", "Scaling")
            )
            scale_str, scale_int, scale_other = sc["str"], sc["int"], sc["other"]

    return {
        "damage_rank1": total1 if total1 > 0 else None,
        "damage_rank5": total5 if total5 > 0 else None,
        "scaling_str": scale_str,
        "scaling_int": scale_int,
        "scaling_other": scale_other,
        "tick_mult": ticks,
        "parts": parts,
    }


def parse_ability_features(
    stats_json: dict[str, str] | None,
    stats_text: str,
    description: str,
    notes: str,
    short_label: str,
) -> dict[str, Any]:
    stats = dict(stats_json) if stats_json else {}
    if not stats and stats_text:
        for line in stats_text.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                stats[k.strip()] = v.strip()

    dmg = sum_ability_damage(stats, stats_text or "")
    dmg1 = dmg["damage_rank1"]
    dmg5 = dmg["damage_rank5"]
    scaling = {
        "str": dmg["scaling_str"],
        "int": dmg["scaling_int"],
        "other": dmg["scaling_other"],
    }

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
            [
                stats_text,
                description,
                notes,
                short_label,
                " ".join(f"{k}:{v}" for k, v in stats.items()),
            ],
        )
    )
    flags = text_flags(blob)

    # Offensive proxies — scale_factor from damage scalings only
    scale_factor = 1.0 + (scaling["str"] + scaling["int"] + scaling["other"]) / 100.0
    burst = (dmg5 or 0.0) * scale_factor
    # Ult channels with long CD: still count burst fully; dps uses real CD
    dps = safe_div(burst, cd5 or 12.0)

    utility = 0.0
    if flags.get("has_hard_cc"):
        utility += 38
    elif flags["has_cc"]:
        utility += 22  # soft CC (slow)
    if flags["has_heal"]:
        utility += 20
    if flags["has_shield"]:
        utility += 18
    elif flags.get("has_prot_buff"):
        utility += 10
    if flags["has_mobility"]:
        utility += 20
    if flags["has_dot"]:
        utility += 12
    utility = clamp(utility)

    # power score heuristic before global normalization
    power_raw = (
        burst * 0.55
        + dps * 8.0
        + (45.0 if flags.get("has_hard_cc") and (dmg5 or 0) > 0 else 0)
        + (20.0 if flags["has_dot"] and burst > 0 else 0)
    )

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
        "has_cc": int(flags["has_cc"]),
        "has_hard_cc": int(flags.get("has_hard_cc", False)),
        "has_heal": int(flags["has_heal"]),
        "has_shield": int(flags["has_shield"]),
        "has_prot_buff": int(flags.get("has_prot_buff", False)),
        "has_mobility": int(flags["has_mobility"]),
        "has_dot": int(flags["has_dot"]),
        "dps_proxy": dps,
        "burst_proxy": burst,
        "utility_score": utility,
        "power_raw": power_raw,
        "tick_mult": dmg.get("tick_mult", 1.0),
        "damage_parts": dmg.get("parts", []),
        "stats_parsed": stats,
    }
