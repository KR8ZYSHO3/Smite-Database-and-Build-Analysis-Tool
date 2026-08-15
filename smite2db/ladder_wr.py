"""
Ranked win-rate ladder for tier lists.

Sources
-------
1. **SmiteBrain** (primary full roster) — top ranked Conquest matches for the
   current OB window via ``https://smitebrain.com/gods/__data.json``.
2. **tracker.gg high-SR sample** (secondary) — aggregate wins from
   ``data/tracker_inspiration.json`` (high Skill Rating Ranked Conquest matches).

Tracker.gg has no public global god-meta WR API (insights/leaderboard endpoints
return 403). Player-level god stats and match wins still work, so the high-SR
inspiration scrape is the honest tracker signal.

Usage:
  python -m smite2db.ladder_wr              # scrape + save snapshot
  python -m smite2db.ladder_wr --no-fetch   # re-load saved snapshot only
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "data" / "ladder_winrates.json"
INSPIRATION_PATH = ROOT / "data" / "tracker_inspiration.json"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Display-name aliases → our wiki god names
NAME_ALIASES = {
    "morrigan": "The Morrigan",
    "the morrigan": "The Morrigan",
    "mulan": "Hua Mulan",
    "hua mulan": "Hua Mulan",
    "cu chulainn": "Cu Chulainn",
    "cuchulainn": "Cu Chulainn",
    "xing tian": "Xing Tian",
    "xingtian": "Xing Tian",
    "sun wukong": "Sun Wukong",
    "baron samedi": "Baron Samedi",
    "princess bari": "Princess Bari",
    "morgan le fay": "Morgan Le Fay",
    "nu wa": "Nu Wa",
    "nuwa": "Nu Wa",
    "ne zha": "Ne Zha",
    "nezha": "Ne Zha",
    "hou yi": "Hou Yi",
    "houyi": "Hou Yi",
    "hun batz": "Hun Batz",
    "da ji": "Da Ji",
    "daji": "Da Ji",
    "ah puch": "Ah Puch",
    "ahpuch": "Ah Puch",
    "change": "Change",
    "chang'e": "Change",
}


def _http(url: str, *, accept: str = "application/json", timeout: float = 30.0) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": accept,
            "Referer": "https://smitebrain.com/gods",
            "Origin": "https://smitebrain.com",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def normalize_god_name(name: str, known: set[str] | None = None) -> str:
    raw = (name or "").strip()
    if not raw:
        return raw
    if known and raw in known:
        return raw
    key = raw.lower().strip()
    if key in NAME_ALIASES:
        aliased = NAME_ALIASES[key]
        if not known or aliased in known:
            return aliased
    # fuzzy: case-insensitive exact against known
    if known:
        for k in known:
            if k.lower() == key:
                return k
        # collapse spaces/hyphens
        compact = re.sub(r"[\s\-']+", "", key)
        for k in known:
            if re.sub(r"[\s\-']+", "", k.lower()) == compact:
                return k
    return raw


def scrape_smitebrain_gods() -> dict[str, Any]:
    """Full-roster ranked WR from SmiteBrain SvelteKit data."""
    url = "https://smitebrain.com/gods/__data.json"
    raw = json.loads(_http(url))
    nodes = raw.get("nodes") or []
    arr = None
    for node in nodes:
        if isinstance(node, dict) and isinstance(node.get("data"), list):
            # Prefer the node that holds win_rate schema dicts
            if any(
                isinstance(x, dict) and "win_rate" in x and "god" in x
                for x in node["data"]
            ):
                arr = node["data"]
                break
    if not arr:
        raise RuntimeError("SmiteBrain payload missing god stats node")

    gods: list[dict[str, Any]] = []
    for item in arr:
        if not isinstance(item, dict):
            continue
        if "win_rate" not in item or "god" not in item:
            continue
        try:
            god = arr[item["god"]]
            wr = arr[item["win_rate"]]
            pr = arr[item["pick_rate"]]
            wins = arr[item["matches_won"]]
            played = arr[item["matches_played"]]
            tier = arr[item.get("tier")] if item.get("tier") is not None else None
            aspect = arr[item["aspect"]] if item.get("aspect") is not None else None
            score = arr[item["score"]] if item.get("score") is not None else None
        except (IndexError, KeyError, TypeError):
            continue
        if not isinstance(god, str) or not isinstance(wr, (int, float)):
            continue
        # Skip pure aspect rows when aspect is a real name (keep "None")
        aspect_s = None if aspect in (None, "None", "", False) else str(aspect)
        gods.append(
            {
                "god": god,
                "win_rate": float(wr),
                "pick_rate": float(pr) if isinstance(pr, (int, float)) else None,
                "wins": int(wins) if isinstance(wins, (int, float)) else None,
                "matches": int(played) if isinstance(played, (int, float)) else None,
                "tier_label": tier if isinstance(tier, str) else None,
                "aspect": aspect_s,
                "score": float(score) if isinstance(score, (int, float)) else None,
            }
        )

    # Prefer base-kit rows (no aspect); if only aspect exists, keep highest matches
    by_god: dict[str, dict[str, Any]] = {}
    for g in gods:
        name = g["god"]
        prev = by_god.get(name)
        if prev is None:
            by_god[name] = g
            continue
        # Prefer non-aspect
        if prev.get("aspect") and not g.get("aspect"):
            by_god[name] = g
            continue
        if g.get("aspect") and not prev.get("aspect"):
            continue
        # Prefer more matches
        if (g.get("matches") or 0) > (prev.get("matches") or 0):
            by_god[name] = g

    return {
        "source": "https://smitebrain.com/gods",
        "source_api": url,
        "mode": "conquest-ranked-top",
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "gods": by_god,
        "row_count_raw": len(gods),
        "god_count": len(by_god),
    }


def tracker_high_sr_wr(
    path: Path | None = None,
    *,
    prior: float = 20.0,
) -> dict[str, Any]:
    """Aggregate god WR from tracker.gg high-SR inspiration snapshot."""
    p = path or INSPIRATION_PATH
    if not p.exists():
        return {
            "source": "tracker.gg high-SR (missing snapshot)",
            "gods": {},
            "note": f"No file at {p}",
        }
    data = json.loads(p.read_text(encoding="utf-8"))
    by_gr = data.get("by_god_role") or {}
    agg: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for key, v in by_gr.items():
        god = key.split("|", 1)[0]
        agg[god][0] += int(v.get("games") or 0)
        agg[god][1] += int(v.get("wins") or 0)

    gods: dict[str, dict[str, Any]] = {}
    for god, (games, wins) in agg.items():
        if games <= 0:
            continue
        raw = wins / games
        bayes = (wins + 0.5 * prior) / (games + prior)
        gods[god] = {
            "god": god,
            "games": games,
            "wins": wins,
            "win_rate": raw,
            "bayesian_wr": bayes,
        }
    return {
        "source": data.get("source") or "https://tracker.gg/smite2/leaderboards",
        "mode": data.get("mode") or "conquest-ranked",
        "season": data.get("season"),
        "scraped_at": data.get("scraped_at"),
        "builds_extracted": data.get("builds_extracted"),
        "players_with_builds": data.get("players_with_builds"),
        "gods": gods,
        "god_count": len(gods),
        "note": (
            "Sampled high-SR Ranked Conquest matches (not global ladder). "
            "Bayesian shrink prior=%g toward 50%%." % prior
        ),
    }


def blend_ladder_scores(
    smitebrain: dict[str, Any],
    tracker: dict[str, Any],
    *,
    known_gods: set[str] | None = None,
    min_matches_sb: int = 80,
    min_games_trn: int = 15,
) -> dict[str, dict[str, Any]]:
    """
    Per-god ladder strength 0–100.

    Primary: SmiteBrain WR (matches-weighted confidence).
    Secondary: tracker high-SR Bayesian WR when sample is large enough.
    Blend when both present; single-source otherwise; neutral 50 if neither.
    """
    sb_gods = smitebrain.get("gods") or {}
    tr_gods = tracker.get("gods") or {}

    names: set[str] = set()
    for n in list(sb_gods) + list(tr_gods):
        names.add(normalize_god_name(n, known_gods))
    if known_gods:
        names |= set(known_gods)

    out: dict[str, dict[str, Any]] = {}
    for name in sorted(names):
        # resolve source rows under aliases
        sb = None
        for k, v in sb_gods.items():
            if normalize_god_name(k, known_gods) == name:
                sb = v
                break
        tr = None
        for k, v in tr_gods.items():
            if normalize_god_name(k, known_gods) == name:
                tr = v
                break

        sb_wr = None
        sb_n = 0
        sb_conf = 0.0
        if sb and (sb.get("matches") or 0) >= min_matches_sb:
            sb_wr = float(sb["win_rate"])
            sb_n = int(sb.get("matches") or 0)
            # confidence rises with sample, caps ~1 at ~600 games
            sb_conf = min(1.0, (sb_n / 600.0) ** 0.5)

        tr_wr = None
        tr_n = 0
        tr_conf = 0.0
        if tr and (tr.get("games") or 0) >= min_games_trn:
            tr_wr = float(tr.get("bayesian_wr") or tr.get("win_rate") or 0.5)
            tr_n = int(tr.get("games") or 0)
            tr_conf = min(0.75, (tr_n / 100.0) ** 0.5)  # sample is thinner

        pr = (sb or {}).get("pick_rate")
        pr_f = float(pr) if isinstance(pr, (int, float)) else 0.0

        if sb_wr is None and tr_wr is None:
            ladder = 50.0
            used = "neutral"
            blended_wr = 0.5
        elif sb_wr is not None and tr_wr is not None:
            # Weight primary harder; tracker is a high-SR tilt check
            w_sb = 0.72 * sb_conf + 0.18
            w_tr = 0.28 * tr_conf + 0.05
            blended_wr = (sb_wr * w_sb + tr_wr * w_tr) / (w_sb + w_tr)
            used = "smitebrain+tracker"
            ladder = _wr_to_ladder(blended_wr, matches=sb_n, pick_rate=pr_f)
        elif sb_wr is not None:
            blended_wr = sb_wr
            used = "smitebrain"
            ladder = _wr_to_ladder(sb_wr, matches=sb_n, pick_rate=pr_f)
        else:
            blended_wr = tr_wr or 0.5
            used = "tracker"
            ladder = _wr_to_ladder(blended_wr, matches=tr_n, narrow=True, pick_rate=0.0)

        # Mild pick-rate presence bump (contested meta > pocket 60% on 50 games)
        if pr_f > 0:
            # +0..3.5 points for ~0–3.5% pick rate
            ladder = min(100.0, ladder + min(3.5, pr_f * 100.0))

        out[name] = {
            "god": name,
            "ladder_score": round(ladder, 2),
            "blended_wr": round(float(blended_wr), 4),
            "source": used,
            "smitebrain_wr": round(sb_wr, 4) if sb_wr is not None else None,
            "smitebrain_matches": sb_n or None,
            "smitebrain_pick_rate": pr if isinstance(pr, (int, float)) else None,
            "smitebrain_tier": (sb or {}).get("tier_label"),
            "tracker_wr": round(tr_wr, 4) if tr_wr is not None else None,
            "tracker_games": tr_n or None,
        }
    return out


def _wr_to_ladder(
    wr: float,
    *,
    matches: int = 0,
    narrow: bool = False,
    pick_rate: float = 0.0,
) -> float:
    """
    Map win rate around 50% onto 0–100.

    45% → ~20, 50% → 50, 55% → ~80, 60% → ~95 (soft cap).
    ``narrow`` = thinner sample → compress toward 50.
    Low match counts and tiny pick rates also shrink extreme WRs.
    """
    import math

    # logistic-ish around 0.50 with scale
    scale = 0.038 if not narrow else 0.055
    z = (float(wr) - 0.5) / scale
    base = 100.0 / (1.0 + math.exp(-z))
    # pull toward 50 when sample is thin (full trust ~250 games)
    if matches and matches < 250:
        t = (matches / 250.0) ** 0.85
        base = 50.0 * (1 - t) + base * t
    # pocket picks (PR < 0.5%) get extra shrink so 64% on 80 games ≠ auto S
    if pick_rate and pick_rate < 0.005:
        shrink = 0.55 + 0.45 * (pick_rate / 0.005)
        base = 50.0 + (base - 50.0) * shrink
    if narrow:
        base = 50.0 + (base - 50.0) * 0.7
    return max(0.0, min(100.0, base))


def collect_ladder_winrates(
    *,
    fetch: bool = True,
    known_gods: set[str] | None = None,
    out_path: Path | None = None,
) -> dict[str, Any]:
    if fetch:
        print("Fetching SmiteBrain ranked god stats…")
        sb = scrape_smitebrain_gods()
        print(f"  {sb['god_count']} gods (raw rows {sb['row_count_raw']})")
    else:
        existing = (out_path or DEFAULT_OUT)
        if existing.exists():
            prev = json.loads(existing.read_text(encoding="utf-8"))
            sb = prev.get("smitebrain") or {"gods": {}}
            print("Using cached SmiteBrain block")
        else:
            sb = {"gods": {}, "note": "no cache"}
            print("WARN: no SmiteBrain cache and --no-fetch")

    print("Loading tracker.gg high-SR sample…")
    tr = tracker_high_sr_wr()
    print(f"  {tr.get('god_count', 0)} gods from inspiration snapshot")

    blended = blend_ladder_scores(sb, tr, known_gods=known_gods)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "philosophy": (
            "Tier ladder uses ranked WR as one vote alongside patch/kit/build. "
            "SmiteBrain = full top-ranked Conquest window; tracker.gg = high-SR "
            "match sample (global god-meta API is 403)."
        ),
        "smitebrain": sb,
        "tracker_high_sr": {
            k: tr[k]
            for k in tr
            if k != "gods"
        },
        "tracker_high_sr_gods": tr.get("gods") or {},
        "blended": blended,
        "blend_count": len(blended),
    }
    path = out_path or DEFAULT_OUT
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {path} ({len(blended)} blended gods)")
    return payload


def load_ladder_scores(path: Path | None = None) -> dict[str, dict[str, Any]]:
    p = path or DEFAULT_OUT
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    return dict(data.get("blended") or {})


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Scrape ranked WR ladder for tiers")
    ap.add_argument("--no-fetch", action="store_true", help="Skip network; use cache")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    collect_ladder_winrates(fetch=not args.no_fetch, out_path=args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
