"""
Post-export ship report: tier deltas + smoke paths + live links.

Usage:
  python -m smite2db.ship_report
  python -m smite2db.ship_report --vs HEAD
  python -m smite2db.ship_report --vs f3377e9
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DOCS_DATA = ROOT / "docs" / "data"
SMOKE = (
    ("Scylla", "Support", "Aspect of the Devourer"),
    ("Scylla", "Mid", "Aspect of the Devourer"),
    ("Kuzenbo", "Support", "base"),
    ("Kuzenbo", "Jungle", "Aspect of Spirits"),
    ("Ymir", "Support", "base"),
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_show_json(rev: str, rel: str) -> Any | None:
    try:
        raw = subprocess.check_output(
            ["git", "show", f"{rev}:{rel}"],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
        )
        return json.loads(raw)
    except (subprocess.CalledProcessError, json.JSONDecodeError, OSError):
        return None


def _overall_index(tiers: dict | list) -> dict[str, tuple]:
    """name -> (tier, rank, score, build_score)."""
    rows = tiers
    if isinstance(tiers, dict):
        rows = tiers.get("overall") or tiers.get("scopes", {}).get("overall") or []
        if isinstance(rows, dict):
            rows = rows.get("entities") or rows.get("rows") or []
    out = {}
    for r in rows or []:
        if not isinstance(r, dict):
            continue
        name = r.get("entity_name") or r.get("name")
        if not name:
            continue
        out[name] = (
            r.get("tier"),
            r.get("rank_in_scope") or r.get("rank"),
            r.get("score"),
            r.get("build_score"),
        )
    return out


def _path_key_items(god: dict, role: str, aspect: str) -> list[str] | None:
    if aspect == "base":
        b = (god.get("conquest_by_role") or {}).get(role)
    else:
        b = ((god.get("conquest_by_aspect") or {}).get(aspect) or {}).get(role)
        if not b:
            # fallback: role_aspect if name matches
            ra = (god.get("conquest_by_role_aspect") or {}).get(role)
            if ra and (ra.get("aspect_name") or "") == aspect:
                b = ra
    if not isinstance(b, dict):
        return None
    items = b.get("items") or []
    names = []
    for it in items:
        if isinstance(it, dict):
            names.append(it.get("name") or "?")
        else:
            names.append(str(it))
    return names


def _algo_version(gods: list) -> str | None:
    for g in gods:
        for role, b in (g.get("conquest_by_role") or {}).items():
            if isinstance(b, dict):
                v = (b.get("algorithm") or {}).get("version")
                if v:
                    return str(v)
    return None


def _git_sha() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT)
            .decode()
            .strip()
        )
    except (subprocess.CalledProcessError, OSError):
        return "unknown"


def compare_tiers(old: Any, new: Any) -> dict[str, Any]:
    o, n = _overall_index(old), _overall_index(new)
    shared = set(o) & set(n)
    letter = [name for name in shared if o[name][0] != n[name][0]]
    rank = [name for name in shared if o[name][1] != n[name][1]]
    build = [
        name
        for name in shared
        if abs(float(o[name][3] or 0) - float(n[name][3] or 0)) > 0.05
    ]
    movers = sorted(
        shared,
        key=lambda name: abs(int(o[name][1] or 0) - int(n[name][1] or 0)),
        reverse=True,
    )
    top = []
    for name in movers[:12]:
        d_rank = int(n[name][1] or 0) - int(o[name][1] or 0)
        if (
            d_rank == 0
            and o[name][0] == n[name][0]
            and abs(float(o[name][3] or 0) - float(n[name][3] or 0)) < 0.05
        ):
            continue
        top.append(
            {
                "name": name,
                "tier": f"{o[name][0]}→{n[name][0]}",
                "rank": f"{o[name][1]}→{n[name][1]} ({d_rank:+d})",
                "build": f"{float(o[name][3] or 0):.1f}→{float(n[name][3] or 0):.1f}",
                "score": f"{float(o[name][2] or 0):.1f}→{float(n[name][2] or 0):.1f}",
            }
        )
    return {
        "gods": len(shared),
        "tier_letter_changed": len(letter),
        "rank_changed": len(rank),
        "build_score_changed": len(build),
        "letter_names": sorted(letter),
        "movers": top,
    }


def smoke_paths(gods: list) -> list[dict[str, Any]]:
    by_name = {g.get("name"): g for g in gods}
    rows = []
    for god, role, aspect in SMOKE:
        g = by_name.get(god)
        if not g:
            rows.append({"key": f"{god}|{role}|{aspect}", "items": None, "error": "missing god"})
            continue
        items = _path_key_items(g, role, aspect)
        rows.append(
            {
                "key": f"{god}|{role}|{aspect}",
                "items": items,
                "identity_lock": None
                if not items
                else (
                    ((g.get("conquest_by_role") or {}).get(role) or {}).get("identity_lock")
                    if aspect == "base"
                    else None
                ),
            }
        )
    return rows


def print_report(
    *,
    vs: str | None = None,
    local_port: int = 8765,
    verbose: bool = True,
) -> dict[str, Any]:
    cur_tiers = _load_json(DOCS_DATA / "tiers.json")
    cur_gods = _load_json(DOCS_DATA / "gods.json")
    if isinstance(cur_gods, dict):
        cur_gods = cur_gods.get("gods") or []

    old_tiers = None
    if vs:
        old_tiers = _git_show_json(vs, "docs/data/tiers.json")

    delta = compare_tiers(old_tiers, cur_tiers) if old_tiers is not None else None
    smoke = smoke_paths(cur_gods)
    sha = _git_sha()
    algo = _algo_version(cur_gods)

    report = {
        "algorithm_version": algo,
        "git_sha": sha,
        "tier_delta": delta,
        "smoke": smoke,
        "links": {
            "local": f"http://127.0.0.1:{local_port}/standalone.html",
            "githack": (
                f"https://raw.githack.com/KR8ZYSHO3/"
                f"Smite-Database-and-Build-Analysis-Tool/{sha}/docs/standalone.html"
            ),
        },
    }

    if not verbose:
        return report

    print("\n=== SHIP REPORT ===")
    print(f"algorithm: {algo}")
    print(f"git HEAD:  {sha}")
    if delta is None:
        print(f"tier delta: (no baseline; pass --vs {vs or 'HEAD'})")
    else:
        print(
            f"tier delta vs {vs}: "
            f"letter={delta['tier_letter_changed']}  "
            f"rank={delta['rank_changed']}  "
            f"build_score={delta['build_score_changed']}  "
            f"(n={delta['gods']})"
        )
        if delta["letter_names"]:
            print(f"  letter flips: {', '.join(delta['letter_names'])}")
        for m in delta["movers"][:10]:
            print(
                f"  {m['name']}: tier {m['tier']}  rank {m['rank']}  "
                f"build {m['build']}  score {m['score']}"
            )
    print("\nsmoke paths:")
    for s in smoke:
        items = s.get("items")
        if items is None:
            print(f"  FAIL {s['key']}: {s.get('error')}")
        else:
            print(f"  {s['key']}: {' → '.join(items)}")
    print("\nlinks:")
    print(f"  local:   {report['links']['local']}")
    print(f"  githack: {report['links']['githack']}  (after push)")
    print("===================\n")
    return report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Ship report: tiers + smoke + links")
    p.add_argument("--vs", default="HEAD", help="git rev for tier baseline (default HEAD)")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--json", action="store_true", help="Print JSON only")
    args = p.parse_args(argv)
    report = print_report(vs=args.vs, local_port=args.port, verbose=not args.json)
    if args.json:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
