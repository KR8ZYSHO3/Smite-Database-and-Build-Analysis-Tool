"""
Sample-weighted ladder/kit blend + build confidence (algorithm 1.5.0).

Policy:
  - Role constraints always apply (hard gates elsewhere).
  - Kit identity wins when locked, especially if ladder sample is tiny.
  - Ladder / high-SR inspire only earn weight when god×role games are large enough.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

# Games at which ladder weight reaches 1.0
LADDER_N0 = 100
# Below this, confidence cannot be "high"
CONF_HIGH_MIN_GAMES = 80
CONF_MED_MIN_GAMES = 25

# Aspect / hook mechanics that remove old item families — hard-ban substrings
ASPECT_REMOVED_BANS: dict[str, tuple[str, ...]] = {
    # Reflect gone → Contagion/Nemean/Mystical identity package is wrong
    "spirit_lifesteal": (
        "hide of the nemean",
        "contagion",
        "mystical",
    ),
}


def ladder_sample_weight(n_games: int | float | None, n0: int = LADDER_N0) -> float:
    """Map god×role match count → [0, 1] ladder trust."""
    try:
        n = float(n_games or 0)
    except (TypeError, ValueError):
        n = 0.0
    if n <= 0 or n0 <= 0:
        return 0.0
    return max(0.0, min(1.0, n / float(n0)))


def blend_weights(
    *,
    n_games: int | float | None,
    identity_lock: bool = False,
    n0: int = LADDER_N0,
) -> dict[str, float]:
    """
    Relative weights for kit vs ladder influence.

    When sample is empty, kit (and role base) carry the vote.
    When identity_lock, ladder share is halved again so staples cannot erase hooks.
    """
    w_ladder = ladder_sample_weight(n_games, n0=n0)
    if identity_lock:
        w_ladder *= 0.5
    w_kit = 1.0 - 0.5 * w_ladder
    return {
        "w_ladder": round(w_ladder, 4),
        "w_kit": round(w_kit, 4),
        "n_games": int(n_games or 0),
        "n0": n0,
    }


def inspire_sample_scale(n_games: int | float | None, *, identity_lock: bool = False) -> float:
    """Extra dampener on tracker inspiration when god×role sample is thin."""
    w = ladder_sample_weight(n_games, n0=LADDER_N0)
    # Inspiration already has its own games/8 curve; this gates by overall sample.
    scale = 0.25 + 0.75 * w
    if identity_lock:
        scale *= 0.85
    return max(0.0, min(1.0, scale))


def aspect_hard_ban_substrings(hooks: set[str] | list[str] | None) -> tuple[str, ...]:
    """Item name substrings hard-banned when a hook removes a mechanic."""
    hs = set(hooks or [])
    out: list[str] = []
    for hook, bans in ASPECT_REMOVED_BANS.items():
        if hook in hs:
            out.extend(bans)
    # Preserve order, unique
    seen: set[str] = set()
    uniq: list[str] = []
    for b in out:
        if b not in seen:
            seen.add(b)
            uniq.append(b)
    return tuple(uniq)


def item_hits_aspect_hard_ban(item_name: str, hooks: set[str] | list[str] | None) -> bool:
    n = (item_name or "").lower()
    return any(b in n for b in aspect_hard_ban_substrings(hooks))


@lru_cache(maxsize=1)
def _load_ladder_wr() -> dict[str, Any]:
    path = Path(__file__).resolve().parent.parent / "data" / "ladder_winrates.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def clear_blend_caches() -> None:
    _load_ladder_wr.cache_clear()


def god_role_ladder_games(god_name: str | None, role: str | None) -> int:
    """
    Best available god×role match count for sample weighting.

    Prefers SmiteSource Masters+ role rows, then tracker inspiration games,
    then blended overall games as a weak fallback (not role-specific).
    """
    god = (god_name or "").strip()
    role_s = (role or "").strip()
    if not god or not role_s:
        return 0
    n = 0
    lw = _load_ladder_wr()
    masters = (lw.get("smitesource_masters_gods") or {}).get(god) or {}
    roles = masters.get("roles") or {}
    # keys often lowercase
    for key in (role_s, role_s.lower(), role_s.title()):
        row = roles.get(key)
        if isinstance(row, dict) and row.get("games") is not None:
            try:
                n = max(n, int(row["games"]))
            except (TypeError, ValueError):
                pass
    # Tracker inspiration (god×role only — never overall god WR)
    try:
        from .tracker_inspire import load_inspiration

        insp = load_inspiration() or {}
        gr = (insp.get("by_god_role") or {}).get(f"{god}|{role_s}")
        if gr and gr.get("games") is not None:
            n = max(n, int(gr["games"]))
    except Exception:  # noqa: BLE001
        pass
    # No overall-god fallback: Support-heavy gods must not inflate Jungle/Mid sample.
    return max(0, n)


def compute_build_confidence(
    *,
    n_games: int | float | None,
    identity_lock: bool = False,
    identity_hooks: list[str] | set[str] | None = None,
    items: list[str] | None = None,
) -> dict[str, Any]:
    """
    Exportable confidence card for a finished build.

    high   — large sample and (if locked) identity cores present
    medium — moderate sample or locked kit with thin ladder
    low    — tiny/no sample (kit theory)
    """
    n = int(n_games or 0)
    weights = blend_weights(n_games=n, identity_lock=identity_lock)
    hooks = set(identity_hooks or [])
    item_names = [str(x) for x in (items or [])]
    hard_bans = aspect_hard_ban_substrings(hooks)
    ban_hits = [nm for nm in item_names if any(b in nm.lower() for b in hard_bans)]

    if n >= CONF_HIGH_MIN_GAMES and not ban_hits:
        label = "high"
    elif n >= CONF_MED_MIN_GAMES or (identity_lock and n >= 8):
        label = "medium"
    else:
        label = "low"

    # Locked kit with almost no games stays low even if we have hooks
    if identity_lock and n < CONF_MED_MIN_GAMES:
        label = "low" if n < 8 else "medium"

    score = weights["w_ladder"]
    if identity_lock:
        score = 0.35 * score + 0.65 * (1.0 if not ban_hits else 0.2)
    else:
        score = 0.7 * score + 0.3 * (1.0 if n >= CONF_MED_MIN_GAMES else 0.4)

    rationale_bits = [
        f"{n} god×role games → ladder weight {weights['w_ladder']:.2f}",
    ]
    if identity_lock:
        rationale_bits.append("identity_lock on — kit cores outrank thin ladder")
    if label == "low":
        rationale_bits.append("treat as kit/role theory until sample grows")
    if ban_hits:
        rationale_bits.append(f"aspect hard-ban leak: {', '.join(ban_hits[:3])}")
        label = "low"

    return {
        "confidence": label,
        "confidence_score": round(max(0.0, min(1.0, score)), 3),
        "ladder_games": n,
        "ladder_weight": weights["w_ladder"],
        "kit_weight": weights["w_kit"],
        "identity_lock": bool(identity_lock),
        "identity_hooks": sorted(hooks),
        "aspect_hard_ban_hits": ban_hits,
        "rationale": "; ".join(rationale_bits),
    }


def summarize_path_breakdown(items: list[Any]) -> dict[str, float]:
    """Aggregate ScoredItem.score_breakdown keys into kit/role/ladder buckets."""
    kit = 0.0
    role = 0.0
    ladder = 0.0
    inspire = 0.0
    other = 0.0
    for it in items or []:
        bd = getattr(it, "score_breakdown", None) or {}
        if not isinstance(bd, dict):
            continue
        # Prefer sample-weighted ladder when present (avoid double-count with raw)
        if "ladder_weighted" in bd:
            try:
                ladder += float(bd["ladder_weighted"])
            except (TypeError, ValueError):
                pass
        elif "ladder" in bd:
            try:
                ladder += float(bd["ladder"])
            except (TypeError, ValueError):
                pass
        for k, v in bd.items():
            try:
                fv = float(v)
            except (TypeError, ValueError):
                continue
            kl = str(k).lower()
            if kl in ("ladder", "ladder_weighted", "ladder_sample_w"):
                continue
            if kl.startswith("stat:") or kl in ("kit", "identity", "signature"):
                kit += fv
            elif kl in ("inspire", "inspiration", "tracker"):
                inspire += fv
            elif kl in ("tag", "util", "momentum", "cost", "align", "active_tax", "item_axes"):
                role += fv
            else:
                other += fv
    return {
        "kit": round(kit, 1),
        "role": round(role, 1),
        "ladder": round(ladder, 1),
        "inspire": round(inspire, 1),
        "other": round(other, 1),
    }
