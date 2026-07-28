"""
Soft ranked inspiration from tracker.gg high-SR Conquest players.

Philosophy (not a meta-copy bot):
  - Pull recent Ranked Conquest builds from top Skill Rating leaderboard players.
  - Aggregate item *frequency* by god × role (and role-wide fallback).
  - Feed a **capped soft boost** into conquest_builds scoring.
  - Kit identity, damage-type bans, pen floors, and ranked core order still win.
  - Snapshot ages out — one week's ladder never becomes permanent law.

Usage:
  python -m smite2db.tracker_inspire --players 40 --pages 2
  python -m smite2db.analyze refresh-inspire   # if wired
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "data" / "tracker_inspiration.json"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

ROLE_MAP = {
    "carry": "Carry",
    "middle": "Mid",
    "mid": "Mid",
    "jungle": "Jungle",
    "solo": "Solo",
    "support": "Support",
}

# Soft influence caps — inspiration never overrides kit hard rules
GOD_ROLE_ITEM_CAP = 32.0
ROLE_ITEM_CAP = 16.0
OPENER_BONUS = 8.0


def _http_json(url: str, *, timeout: float = 25.0) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "application/json",
            "Origin": "https://tracker.gg",
            "Referer": "https://tracker.gg/smite2/",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_text(url: str, *, timeout: float = 25.0) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml",
            "Referer": "https://tracker.gg/smite2/",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def scrape_leaderboard_players(
    *,
    pages: int = 2,
    season: int = 3,
    board: str = "SkillRating",
    ranked_mode: str = "conquest-ranked",
    sleep_s: float = 0.6,
) -> list[dict[str, str]]:
    """
    Parse tracker.gg HTML leaderboard pages for profile links.
    Leaderboard JSON API is 403-protected; HTML table works.
    """
    players: list[dict[str, str]] = []
    seen: set[str] = set()
    # /smite2/profile/{platform}/{id}
    pat = re.compile(
        r"/smite2/profile/(steam|epic|psn|xbox|xbl|switch)/([^?\"'#\s]+)",
        re.I,
    )
    for page in range(1, max(1, pages) + 1):
        url = (
            "https://tracker.gg/smite2/leaderboards"
            f"?ranked-mode={ranked_mode}&board={board}&season={season}&page={page}"
        )
        try:
            html = _http_text(url)
        except Exception as exc:  # noqa: BLE001
            print(f"  WARN leaderboard page {page}: {exc}")
            continue
        for m in pat.finditer(html):
            platform, ident = m.group(1).lower(), m.group(2)
            # URL-decode common cases lightly
            ident = urllib.parse.unquote(ident)
            key = f"{platform}:{ident}"
            if key in seen:
                continue
            seen.add(key)
            # rank from nearby table context if possible
            players.append({"platform": platform, "id": ident, "key": key})
        time.sleep(sleep_s)
    return players


def fetch_player_matches(
    platform: str,
    user_id: str,
    *,
    gamemode: str = "conquest-ranked",
    sleep_s: float = 0.35,
) -> list[dict[str, Any]]:
    url = (
        f"https://api.tracker.gg/api/v2/smite2/standard/matches/"
        f"{platform}/{urllib.parse.quote(user_id, safe='')}?type={gamemode}"
    )
    try:
        data = _http_json(url)
    except urllib.error.HTTPError as exc:
        if exc.code in (404, 403, 429):
            return []
        raise
    except Exception:  # noqa: BLE001
        return []
    time.sleep(sleep_s)
    return list((data.get("data") or {}).get("matches") or [])


def _normalize_role(meta: dict[str, Any]) -> str | None:
    played = meta.get("playedRole") or meta.get("assignedRole") or {}
    if isinstance(played, dict):
        key = (played.get("key") or played.get("name") or "").lower()
    else:
        key = str(played).lower()
    return ROLE_MAP.get(key)


def _core_items(items: list[dict[str, Any]]) -> list[str]:
    """T3-ish cores only — skip starter / relic / curio / incomplete components."""
    out: list[str] = []
    for it in items or []:
        et = (it.get("equipmentType") or "").lower()
        name = (it.get("name") or "").strip()
        if not name:
            continue
        if et in ("starter", "relic", "curio", "consumable"):
            continue
        # tracker uses item-passive / item-active for full items; bare 'item' too
        if et.startswith("item") or et in ("", "unknown"):
            # filter obvious T1/T2 component stubs (very short / generic)
            if name.lower() in ("bow", "sword", "axe", "staff", "shield", "cloak"):
                continue
            out.append(name)
    return out


def _starter_name(items: list[dict[str, Any]]) -> str | None:
    for it in items or []:
        if (it.get("equipmentType") or "").lower() == "starter":
            n = (it.get("name") or "").strip()
            if n:
                return n
    return None


def extract_build_from_match_segment(seg: dict[str, Any]) -> dict[str, Any] | None:
    meta = seg.get("metadata") or {}
    god = meta.get("godName") or meta.get("god")
    if not god:
        return None
    role = _normalize_role(meta)
    if not role:
        return None
    items = _core_items(meta.get("items") or [])
    if len(items) < 3:
        return None
    stats = seg.get("stats") or {}
    # win heuristic: placement 1 on overview or team won — tracker uses placement
    placement = (stats.get("placement") or {}).get("value")
    won = placement == 1 if placement is not None else None
    return {
        "god": str(god),
        "role": role,
        "items": items,
        "opener": items[0] if items else None,
        "starter": _starter_name(meta.get("items") or []),
        "won": won,
        "sr": (stats.get("skillRating") or {}).get("value"),
    }


def aggregate_builds(
    builds: list[dict[str, Any]],
    *,
    min_games_god: int = 2,
) -> dict[str, Any]:
    """Frequency tables for soft scoring."""
    by_god_role: dict[str, dict[str, Any]] = {}
    by_role: dict[str, dict[str, Any]] = {}
    global_items: Counter[str] = Counter()

    def bucket(store: dict, key: str) -> dict[str, Any]:
        if key not in store:
            store[key] = {
                "games": 0,
                "wins": 0,
                "items": Counter(),
                "openers": Counter(),
                "starters": Counter(),
                # sum of 0-based core slots for avg buy position
                "pos_sum": Counter(),
                "pos_n": Counter(),
            }
        return store[key]

    for b in builds:
        god, role = b["god"], b["role"]
        gk = f"{god}|{role}"
        for store, key in ((by_god_role, gk), (by_role, role)):
            bkt = bucket(store, key)
            bkt["games"] += 1
            if b.get("won"):
                bkt["wins"] += 1
            for idx, it in enumerate(b["items"]):
                bkt["items"][it] += 1
                bkt["pos_sum"][it] += idx
                bkt["pos_n"][it] += 1
                if store is by_god_role:
                    global_items[it] += 1
            if b.get("opener"):
                bkt["openers"][b["opener"]] += 1
            if b.get("starter"):
                bkt["starters"][b["starter"]] += 1

    def freeze(store: dict[str, Any], *, min_g: int = 1) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for k, v in store.items():
            if v["games"] < min_g:
                continue
            games = max(v["games"], 1)
            items = {}
            for name, c in v["items"].most_common(40):
                pn = max(int(v["pos_n"].get(name) or 0), 1)
                avg_pos = float(v["pos_sum"].get(name) or 0) / pn
                items[name] = {
                    "count": c,
                    "rate": round(c / games, 3),
                    # soft score 0..1 from frequency (sqrt dampens one-offs)
                    "weight": round(min(1.0, (c / games) ** 0.5), 3),
                    # 0 = always first core, 5 = last — critical for buy order
                    "avg_slot": round(avg_pos, 2),
                }
            openers = {
                name: {"count": c, "rate": round(c / games, 3)}
                for name, c in v["openers"].most_common(12)
            }
            starters = {
                name: {"count": c, "rate": round(c / games, 3)}
                for name, c in v["starters"].most_common(8)
            }
            out[k] = {
                "games": v["games"],
                "wins": v["wins"],
                "win_rate": round(v["wins"] / games, 3) if v["wins"] else None,
                "items": items,
                "openers": openers,
                "starters": starters,
            }
        return out

    return {
        "by_god_role": freeze(by_god_role, min_g=min_games_god),
        "by_role": freeze(by_role, min_g=max(3, min_games_god)),
        "global_items": {
            n: c for n, c in global_items.most_common(60)
        },
    }


def collect_inspiration(
    *,
    players: int = 40,
    pages: int = 2,
    season: int = 3,
    max_matches_per_player: int = 20,
    sleep_s: float = 0.4,
    verbose: bool = True,
) -> dict[str, Any]:
    if verbose:
        print(f"Scraping leaderboard (season {season}, {pages} pages)…")
    board = scrape_leaderboard_players(pages=pages, season=season, sleep_s=sleep_s)
    board = board[: max(1, players)]
    if verbose:
        print(f"  {len(board)} unique high-SR players")

    builds: list[dict[str, Any]] = []
    player_ok = 0
    for i, p in enumerate(board, 1):
        if verbose and (i == 1 or i % 10 == 0 or i == len(board)):
            print(f"  matches {i}/{len(board)} {p['platform']}/{p['id'][:24]}…")
        matches = fetch_player_matches(
            p["platform"], p["id"], sleep_s=sleep_s
        )[:max_matches_per_player]
        got = 0
        for match in matches:
            # list endpoint: one segment = this player's overview
            for seg in match.get("segments") or []:
                if seg.get("type") != "overview":
                    continue
                b = extract_build_from_match_segment(seg)
                if b:
                    b["player"] = p["key"]
                    b["match_id"] = (match.get("attributes") or {}).get("id")
                    builds.append(b)
                    got += 1
        if got:
            player_ok += 1

    if verbose:
        print(f"  extracted {len(builds)} builds from {player_ok} players")

    agg = aggregate_builds(builds)
    return {
        "source": "https://tracker.gg/smite2/leaderboards",
        "mode": "conquest-ranked",
        "board": "SkillRating",
        "season": season,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "philosophy": (
            "Soft inspiration only: high-SR item frequencies nudge scores. "
            "Kit identity, pen floors, and ranked core order remain primary. "
            "Not a 1:1 meta copy."
        ),
        "players_targeted": len(board),
        "players_with_builds": player_ok,
        "builds_extracted": len(builds),
        "player_keys": [p["key"] for p in board[:80]],
        **agg,
    }


# ---------- scoring helpers used by conquest_builds ----------

_INSPIRE_CACHE: dict[str, Any] | None = None
_INSPIRE_PATH: Path | None = None


def load_inspiration(path: Path | str | None = None) -> dict[str, Any] | None:
    global _INSPIRE_CACHE, _INSPIRE_PATH
    p = Path(path) if path else DEFAULT_OUT
    if _INSPIRE_CACHE is not None and _INSPIRE_PATH == p:
        return _INSPIRE_CACHE
    if not p.is_file():
        _INSPIRE_CACHE = None
        _INSPIRE_PATH = p
        return None
    try:
        _INSPIRE_CACHE = json.loads(p.read_text(encoding="utf-8"))
        _INSPIRE_PATH = p
        return _INSPIRE_CACHE
    except (OSError, json.JSONDecodeError):
        _INSPIRE_CACHE = None
        return None


def clear_inspiration_cache() -> None:
    global _INSPIRE_CACHE, _INSPIRE_PATH
    _INSPIRE_CACHE = None
    _INSPIRE_PATH = None


def inspiration_boost(
    item_name: str,
    *,
    god_name: str | None,
    role: str,
    data: dict[str, Any] | None = None,
) -> tuple[float, str | None]:
    """
    Soft score boost for an item. Returns (delta, short why) or (0, None).

    Caps:
      god×role: ≤ GOD_ROLE_ITEM_CAP
      role-wide: ≤ ROLE_ITEM_CAP
      opener list: +OPENER_BONUS
    Early-slot items (low avg_slot) get a bit more pick priority.
    """
    data = data if data is not None else load_inspiration()
    if not data or not item_name:
        return 0.0, None
    n = item_name
    role_key = role
    god = (god_name or "").strip()
    delta = 0.0
    why_bits: list[str] = []

    gr = (data.get("by_god_role") or {}).get(f"{god}|{role_key}") if god else None
    if gr and gr.get("games", 0) >= 2:
        ent = (gr.get("items") or {}).get(n)
        if ent:
            w = float(ent.get("weight") or 0)
            conf = min(1.0, gr["games"] / 8.0)
            add = GOD_ROLE_ITEM_CAP * w * conf
            # Prefer items that high-SR actually buys *early*
            avg = ent.get("avg_slot")
            if avg is not None and float(avg) <= 1.5:
                add *= 1.25
            if add >= 4:
                delta += add
                why_bits.append(f"high-SR {god} {role} ({ent.get('count')}/{gr['games']})")
        op = (gr.get("openers") or {}).get(n)
        if op and float(op.get("rate") or 0) >= 0.2:
            delta += OPENER_BONUS * min(1.0, float(op["rate"]) * 1.4)
            why_bits.append("common high-SR opener")

    if delta < 6:
        rr = (data.get("by_role") or {}).get(role_key)
        if rr and rr.get("games", 0) >= 5:
            ent = (rr.get("items") or {}).get(n)
            if ent:
                w = float(ent.get("weight") or 0)
                conf = min(1.0, rr["games"] / 25.0)
                add = ROLE_ITEM_CAP * w * conf
                avg = ent.get("avg_slot")
                if avg is not None and float(avg) <= 1.5:
                    add *= 1.2
                if add >= 3:
                    delta += add
                    why_bits.append(f"high-SR {role} staple")
            op = (rr.get("openers") or {}).get(n)
            if op and float(op.get("rate") or 0) >= 0.12:
                delta += OPENER_BONUS * 0.7 * min(1.0, float(op["rate"]) * 2)
                if "opener" not in " ".join(why_bits):
                    why_bits.append("high-SR role opener")

    if delta <= 0:
        return 0.0, None
    return round(delta, 2), ("; ".join(why_bits) if why_bits else "high-SR inspiration")


def inspiration_buy_rank(
    item_name: str,
    *,
    god_name: str | None,
    role: str,
    data: dict[str, Any] | None = None,
) -> float | None:
    """
    Preferred buy position from high-SR data (0 = first core, 5 = last).
    None if we lack enough samples. Used by _order_buy_path.
    """
    data = data if data is not None else load_inspiration()
    if not data or not item_name:
        return None
    god = (god_name or "").strip()
    # Prefer god×role avg_slot when sample is decent
    if god:
        gr = (data.get("by_god_role") or {}).get(f"{god}|{role}")
        if gr and gr.get("games", 0) >= 4:
            ent = (gr.get("items") or {}).get(item_name)
            if ent and ent.get("avg_slot") is not None and ent.get("count", 0) >= 2:
                return float(ent["avg_slot"])
            op = (gr.get("openers") or {}).get(item_name)
            if op and float(op.get("rate") or 0) >= 0.3:
                return 0.0
    rr = (data.get("by_role") or {}).get(role)
    if rr and rr.get("games", 0) >= 20:
        ent = (rr.get("items") or {}).get(item_name)
        if ent and ent.get("avg_slot") is not None and ent.get("count", 0) >= 8:
            return float(ent["avg_slot"])
        op = (rr.get("openers") or {}).get(item_name)
        if op and float(op.get("rate") or 0) >= 0.15:
            return 0.2
    return None


def save_inspiration(doc: dict[str, Any], path: Path | str | None = None) -> Path:
    out = Path(path) if path else DEFAULT_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    # Never clobber a good snapshot with an empty scrape (403 / rate-limit)
    n = int(doc.get("builds_extracted") or 0)
    if n < 20 and out.is_file():
        try:
            old = json.loads(out.read_text(encoding="utf-8"))
            if int(old.get("builds_extracted") or 0) >= 20:
                print(
                    f"WARN: refusing to overwrite {out} "
                    f"(new builds={n}, existing={old.get('builds_extracted')})"
                )
                return out
        except (OSError, json.JSONDecodeError, TypeError):
            pass
    out.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    clear_inspiration_cache()
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Scrape tracker.gg high-SR builds for soft inspiration")
    p.add_argument("--players", type=int, default=40, help="Top N leaderboard players")
    p.add_argument("--pages", type=int, default=2, help="Leaderboard HTML pages to parse")
    p.add_argument("--season", type=int, default=3)
    p.add_argument("--matches", type=int, default=20, help="Max matches per player")
    p.add_argument("--sleep", type=float, default=0.4, help="Delay between HTTP calls")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("-q", "--quiet", action="store_true")
    args = p.parse_args(argv)

    doc = collect_inspiration(
        players=args.players,
        pages=args.pages,
        season=args.season,
        max_matches_per_player=args.matches,
        sleep_s=args.sleep,
        verbose=not args.quiet,
    )
    path = save_inspiration(doc, args.out)
    print(f"Wrote {path}")
    print(
        f"  builds={doc.get('builds_extracted')}  "
        f"god×role buckets={len(doc.get('by_god_role') or {})}  "
        f"role buckets={len(doc.get('by_role') or {})}"
    )
    # preview top mid/jungle staples
    for role in ("Mid", "Jungle", "Carry", "Solo", "Support"):
        rr = (doc.get("by_role") or {}).get(role) or {}
        items = list((rr.get("items") or {}).items())[:6]
        if items:
            top = ", ".join(f"{n}({v['count']})" for n, v in items)
            print(f"  {role}: {top}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
