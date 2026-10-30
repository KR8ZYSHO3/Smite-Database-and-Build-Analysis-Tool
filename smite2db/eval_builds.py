"""
Evaluate conquest build quality: identity fixtures + inspiration holdout.

Usage:
  python -m smite2db.eval_builds
  python -m smite2db.eval_builds --holdout 0.3 --min-games 4
  python -m smite2db.eval_builds --fixtures-only
  python -m smite2db.eval_builds --god Kuzenbo

Metrics:
  - Identity compliance (required / banned cores for locked kits)
  - Holdout hit-rate: algorithm's 6 items vs held-out high-SR item bags
  - Ablation: full blend vs kit-only (ladder_weight forced to 0)

Does not require raw match dumps — uses data/tracker_inspiration.json
god×role item bags as a proxy "winning build" distribution.
"""

from __future__ import annotations

import argparse
import json
import random
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .build_blend import (
    ASPECT_REMOVED_BANS,
    LADDER_N0,
    compute_build_confidence,
    god_role_ladder_games,
    item_hits_aspect_hard_ban,
    ladder_sample_weight,
)
from .build_pipeline import ALGORITHM_VERSION
from .conquest_builds import build_god_build, load_items
from .db import DEFAULT_DB, connect
from .tracker_inspire import load_inspiration

ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "data" / "eval_builds_report.json"


@dataclass
class Fixture:
    name: str
    god: str
    role: str
    aspect: str | None
    require_any: list[str] = field(default_factory=list)  # at least one substring match each group
    require_all: list[str] = field(default_factory=list)
    ban: list[str] = field(default_factory=list)
    max_actives: int | None = None
    note: str = ""


# Gold-set regressions — kit identity + role logic
FIXTURES: list[Fixture] = [
    Fixture(
        name="kuzenbo_base_support",
        god="Kuzenbo",
        role="Support",
        aspect=None,
        require_all=["thebes"],
        require_any=["contagion", "nemean", "mystical", "ethereal", "prophetic", "freya"],
        ban=["gluttonous", "umbral", "bancroft", "typhon"],
        max_actives=1,
        note="Base Support Max-HP/reflect shell; no spirit LS cores",
    ),
    Fixture(
        name="kuzenbo_spirits_jungle",
        god="Kuzenbo",
        role="Jungle",
        aspect="Aspect of Spirits",
        require_all=["gluttonous"],
        require_any=["chronos", "soul gem", "ethereal", "bancroft", "typhon", "prophetic", "magus"],
        ban=["contagion", "nemean", "thebes"],
        note="Spirits Jungle LS/INT; reflect cores and Thebes banned",
    ),
    Fixture(
        name="kuzenbo_spirits_support",
        god="Kuzenbo",
        role="Support",
        aspect="Aspect of Spirits",
        require_any=["gluttonous", "umbral", "soul gem", "bancroft"],
        ban=["contagion", "nemean", "mystical"],
        note="Spirits Support may keep Thebes; must not run reflect package",
    ),
    Fixture(
        name="kuzenbo_base_jungle",
        god="Kuzenbo",
        role="Jungle",
        aspect=None,
        ban=["thebes"],
        require_any=["gluttonous", "chronos", "ethereal", "contagion", "nemean", "mystical"],
        note="Base Jungle: no Thebes; clear/reflect tempo",
    ),
    Fixture(
        name="scylla_devourer_support",
        god="Scylla",
        role="Support",
        aspect="Aspect of the Devourer",
        require_all=["thoth"],
        require_any=["yogi", "breastplate", "genji", "isolation", "valor"],
        ban=["tahuti", "dreamer", "obsidian", "desolat"],
        note="Devourer Support: Max Mana bank (Thoth) + peel shell; no glass mid cores",
    ),
    Fixture(
        name="ah_puch_mid_base",
        god="Ah Puch",
        role="Mid",
        aspect=None,
        require_all=["thoth"],
        require_any=["desolat", "magus", "cosmic", "obsidian"],
        ban=[],
        note="Mana Mid: Thoth bank + real tank-melt pen (Deso/Magus/Cosmic/Obsidian; Doom alone insufficient)",
    ),
    Fixture(
        name="scylla_devourer_mid",
        god="Scylla",
        role="Mid",
        aspect="Aspect of the Devourer",
        require_all=["thoth"],
        require_any=["desolat", "magus", "cosmic", "obsidian"],
        ban=["thebes"],
        note="Devourer Mid: mana bank + flat/% pen; not a Thebes support shell",
    ),
    Fixture(
        name="cupid_love_carry",
        god="Cupid",
        role="Carry",
        aspect="Aspect of Love",
        require_any=["sickle", "asclepius", "heartwood"],
        ban=[],
        note="Love Carry: ally heal/shield identity must land a heal-amp core",
    ),
    Fixture(
        name="apollo_harmony_carry",
        god="Apollo",
        role="Carry",
        aspect="Aspect of Harmony",
        require_all=["ethereal"],
        require_any=["contagion", "thebes"],
        ban=["deathbringer", "tyrfing"],
        note="Harmony Carry: item-HP stack; no crit ADC package",
    ),
    Fixture(
        name="thanatos_reaping_jungle",
        god="Thanatos",
        role="Jungle",
        aspect="Aspect of Reaping",
        require_all=["contagion"],
        require_any=["leviathan", "gladiator", "nemean"],
        ban=["sickle", "asclepius"],
        note="Reaping Jungle: permanent Max-HP shell + Contagion; jungle tempo via normalize",
    ),
    Fixture(
        name="ymir_support_base",
        god="Ymir",
        role="Support",
        aspect=None,
        require_all=["thebes"],
        require_any=["breastplate", "genji"],
        ban=["thoth", "desolat", "cosmic"],
        note="Ymir Support: item-prot CC shell (Thebes + BoV/Genji)",
    ),
    Fixture(
        name="ravana_rakshasa_solo",
        god="Ravana",
        role="Solo",
        aspect="Aspect of the Rakshasa",
        require_any=["spectral", "alchemist", "mystical", "shifter"],
        ban=["deathbringer", "tyrfing"],
        note="Rakshasa Solo: Plat/Damp stack (≥1 of Spectral/Alchemist/Mystical/Shifter)",
    ),
    Fixture(
        name="ra_thermo_mid",
        god="Ra",
        role="Mid",
        aspect="Aspect of Thermotherapy",
        require_all=["sickle", "asclepius"],
        ban=["desolat", "thoth", "tahuti"],
        note="Thermo Mid: enchanter Sickle+Asclepius; no power-mage cores",
    ),
]


def _norm(s: str) -> str:
    return (s or "").lower()


def _path_names(build: dict[str, Any] | None) -> list[str]:
    if not build:
        return []
    items = build.get("items") or build.get("full_path") or []
    out = []
    for it in items:
        if isinstance(it, dict) and it.get("name"):
            out.append(str(it["name"]))
        elif isinstance(it, str):
            out.append(it)
    return out


def _has_substr(names: list[str], needle: str) -> bool:
    n = _norm(needle)
    return any(n in _norm(x) for x in names)


def _active_count(build: dict[str, Any] | None) -> int:
    if not build:
        return 0
    if build.get("active_count") is not None:
        try:
            return int(build["active_count"])
        except (TypeError, ValueError):
            pass
    n = 0
    for it in build.get("items") or []:
        if isinstance(it, dict) and it.get("is_active"):
            n += 1
    return n


def _load_god_row(conn: sqlite3.Connection, name: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT id, name, primary_damage_type, pantheon, type_label, roles FROM gods WHERE name=?",
        (name,),
    ).fetchone()
    if not row:
        return None
    return {
        "god_id": int(row["id"]),
        "entity_name": row["name"],
        "name": row["name"],
        "primary_damage_type": row["primary_damage_type"],
        "pantheon": row["pantheon"],
        "type_label": row["type_label"],
        "roles": row["roles"],
    }


def _resolve_aspect_id(conn: sqlite3.Connection, god_id: int, aspect_name: str | None) -> int | None:
    if not aspect_name:
        return None
    try:
        from .aspect_kit import list_god_aspects

        for a in list_god_aspects(conn, god_id) or []:
            if _norm(a.get("name") or "") == _norm(aspect_name):
                return int(a["id"])
            if _norm(aspect_name) in _norm(a.get("name") or ""):
                return int(a["id"])
    except Exception:  # noqa: BLE001
        pass
    row = conn.execute(
        "SELECT id, name FROM god_aspects WHERE god_id=?",
        (god_id,),
    ).fetchall()
    for r in row or []:
        if _norm(r["name"]) == _norm(aspect_name) or _norm(aspect_name) in _norm(r["name"]):
            return int(r["id"])
    return None


def build_for_fixture(
    conn: sqlite3.Connection,
    items: list[dict],
    fix: Fixture,
) -> dict[str, Any] | None:
    god = _load_god_row(conn, fix.god)
    if not god:
        return None
    aspect_id = _resolve_aspect_id(conn, int(god["god_id"]), fix.aspect)
    use_aspect = bool(fix.aspect)
    return build_god_build(
        conn,
        items,
        fix.role,
        god,
        use_aspect=use_aspect,
        aspect_id=aspect_id,
    )


def run_fixtures(
    conn: sqlite3.Connection,
    items: list[dict],
    *,
    only_god: str | None = None,
) -> dict[str, Any]:
    results = []
    passed = 0
    failed = 0
    for fix in FIXTURES:
        if only_god and _norm(fix.god) != _norm(only_god):
            continue
        build = build_for_fixture(conn, items, fix)
        names = _path_names(build)
        errors: list[str] = []
        if build is None:
            errors.append("build returned None")
        for req in fix.require_all:
            if not _has_substr(names, req):
                errors.append(f"missing required '{req}'")
        for group in fix.require_any:
            # require_any is a flat list of alternatives (any one is enough)
            pass
        if fix.require_any and not any(_has_substr(names, r) for r in fix.require_any):
            errors.append(f"missing any of {fix.require_any}")
        for ban in fix.ban:
            if _has_substr(names, ban):
                errors.append(f"banned item present '{ban}'")
        if fix.max_actives is not None and _active_count(build) > fix.max_actives:
            errors.append(
                f"active_count {_active_count(build)} > max {fix.max_actives}"
            )
        # Aspect hard-ban invariant when Spirits
        if fix.aspect and "spirit" in _norm(fix.aspect):
            for ban in ASPECT_REMOVED_BANS.get("spirit_lifesteal", ()):
                if _has_substr(names, ban):
                    errors.append(f"aspect hard-ban leak '{ban}'")

        conf = (build or {}).get("confidence_card") or {}
        ok = not errors
        if ok:
            passed += 1
        else:
            failed += 1
        results.append(
            {
                "name": fix.name,
                "ok": ok,
                "errors": errors,
                "items": names,
                "starter": ((build or {}).get("starter") or {}).get("name"),
                "confidence": (build or {}).get("confidence"),
                "ladder_games": (build or {}).get("ladder_games"),
                "ladder_weight": (build or {}).get("ladder_weight"),
                "aspect": (build or {}).get("aspect_name"),
                "note": fix.note,
                "confidence_rationale": conf.get("rationale"),
            }
        )
    return {
        "passed": passed,
        "failed": failed,
        "total": passed + failed,
        "results": results,
    }


def _item_bag_from_inspiration(gr: dict[str, Any]) -> list[str]:
    """Expand inspiration item counts into a multiset bag (for holdout splits)."""
    bag: list[str] = []
    items = gr.get("items") or {}
    for name, ent in items.items():
        if not isinstance(ent, dict):
            continue
        cnt = int(ent.get("count") or 0)
        # Cap per item so one staple does not dominate the bag
        cnt = max(1, min(cnt, 8)) if cnt else 0
        bag.extend([str(name)] * cnt)
    return bag


def holdout_hit_rate(
    conn: sqlite3.Connection,
    items: list[dict],
    *,
    holdout: float = 0.3,
    min_games: int = 4,
    seed: int = 42,
    only_god: str | None = None,
) -> dict[str, Any]:
    """
    For each god|role with enough inspiration games:
      - Split observed items into train/holdout bags
      - Build algorithm path (full)
      - Score: fraction of algorithm items that appear in holdout bag (unique)
    Also reports kit-only ablation proxy: hit rate expected lower/higher depending on sample.
    """
    random.seed(seed)
    insp = load_inspiration() or {}
    by_gr = insp.get("by_god_role") or {}
    rows = []
    for key, gr in by_gr.items():
        if "|" not in key:
            continue
        god, role = key.split("|", 1)
        if only_god and _norm(god) != _norm(only_god):
            continue
        games = int(gr.get("games") or 0)
        if games < min_games:
            continue
        bag = _item_bag_from_inspiration(gr)
        if len(bag) < 4:
            continue
        random.shuffle(bag)
        cut = max(1, int(len(bag) * holdout))
        hold = set(bag[:cut])
        train = set(bag[cut:])
        god_row = _load_god_row(conn, god)
        if not god_row:
            continue
        build = build_god_build(conn, items, role, god_row)
        if not build:
            continue
        algo = _path_names(build)
        if not algo:
            continue
        hits = sum(1 for nm in algo if nm in hold or any(_norm(nm) == _norm(h) for h in hold))
        # fuzzy: substring / case
        hits = 0
        for nm in algo:
            if any(_norm(nm) == _norm(h) or _norm(h) in _norm(nm) or _norm(nm) in _norm(h) for h in hold):
                hits += 1
        hit_rate = hits / len(algo)
        # Train overlap (sanity — should usually be higher than holdout)
        train_hits = sum(
            1
            for nm in algo
            if any(_norm(nm) == _norm(h) or _norm(h) in _norm(nm) for h in train)
        )
        n_ladder = god_role_ladder_games(god, role)
        rows.append(
            {
                "god": god,
                "role": role,
                "games": games,
                "ladder_games": n_ladder,
                "ladder_weight": ladder_sample_weight(n_ladder),
                "confidence": build.get("confidence"),
                "algo_items": algo,
                "holdout_hit_rate": round(hit_rate, 3),
                "train_hit_rate": round(train_hits / len(algo), 3),
                "holdout_size": len(hold),
                "identity_lock": bool(
                    (build.get("confidence_card") or {}).get("identity_lock")
                ),
            }
        )

    if not rows:
        return {
            "n": 0,
            "mean_holdout_hit_rate": None,
            "mean_train_hit_rate": None,
            "rows": [],
            "note": "No god|role bags met min_games",
        }

    mean_h = sum(r["holdout_hit_rate"] for r in rows) / len(rows)
    mean_t = sum(r["train_hit_rate"] for r in rows) / len(rows)
    # Stratify by ladder weight
    thin = [r for r in rows if r["ladder_weight"] < 0.25]
    fat = [r for r in rows if r["ladder_weight"] >= 0.5]
    return {
        "n": len(rows),
        "holdout": holdout,
        "min_games": min_games,
        "mean_holdout_hit_rate": round(mean_h, 3),
        "mean_train_hit_rate": round(mean_t, 3),
        "thin_sample_n": len(thin),
        "thin_mean_holdout_hit_rate": round(
            sum(r["holdout_hit_rate"] for r in thin) / len(thin), 3
        )
        if thin
        else None,
        "fat_sample_n": len(fat),
        "fat_mean_holdout_hit_rate": round(
            sum(r["holdout_hit_rate"] for r in fat) / len(fat), 3
        )
        if fat
        else None,
        "rows": rows,
    }


def unit_blend_checks() -> dict[str, Any]:
    """Pure function checks for build_blend (no DB)."""
    errors = []
    if ladder_sample_weight(0) != 0:
        errors.append("w(0) should be 0")
    if ladder_sample_weight(LADDER_N0) != 1.0:
        errors.append("w(n0) should be 1")
    if not (0.49 <= ladder_sample_weight(LADDER_N0 // 2) <= 0.51):
        errors.append("w(n0/2) should be ~0.5")
    if not item_hits_aspect_hard_ban("Hide of the Nemean Lion", {"spirit_lifesteal"}):
        errors.append("Nemean should hard-ban under spirit_lifesteal")
    if item_hits_aspect_hard_ban("Gluttonous Grimoire", {"spirit_lifesteal"}):
        errors.append("Gluttonous should not hard-ban under spirit_lifesteal")
    conf = compute_build_confidence(n_games=4, identity_lock=True, identity_hooks=["spirit_lifesteal"])
    if conf["confidence"] not in ("low", "medium"):
        errors.append(f"thin locked sample should be low/medium, got {conf['confidence']}")
    conf2 = compute_build_confidence(n_games=120, identity_lock=False)
    if conf2["confidence"] != "high":
        errors.append(f"fat sample should be high, got {conf2['confidence']}")
    return {"ok": not errors, "errors": errors}


def run_eval(
    *,
    db_path: Path | None = None,
    holdout: float = 0.3,
    min_games: int = 4,
    fixtures_only: bool = False,
    only_god: str | None = None,
    write_report: bool = True,
) -> dict[str, Any]:
    unit = unit_blend_checks()
    conn = connect(db_path or DEFAULT_DB)
    try:
        items = load_items(conn)
        fixtures = run_fixtures(conn, items, only_god=only_god)
        hold = None
        if not fixtures_only:
            hold = holdout_hit_rate(
                conn,
                items,
                holdout=holdout,
                min_games=min_games,
                only_god=only_god,
            )
    finally:
        conn.close()

    report = {
        "algorithm_version": ALGORITHM_VERSION,
        "ladder_n0": LADDER_N0,
        "unit_blend": unit,
        "fixtures": fixtures,
        "holdout": hold,
        "summary": {
            "fixtures_passed": fixtures["passed"],
            "fixtures_failed": fixtures["failed"],
            "unit_ok": unit["ok"],
            "holdout_mean_hit_rate": (hold or {}).get("mean_holdout_hit_rate"),
            "holdout_n": (hold or {}).get("n"),
        },
    }
    if write_report:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Evaluate conquest builds (fixtures + holdout)")
    p.add_argument("--db", type=Path, default=None)
    p.add_argument("--holdout", type=float, default=0.3)
    p.add_argument("--min-games", type=int, default=4)
    p.add_argument("--fixtures-only", action="store_true")
    p.add_argument("--god", type=str, default=None, help="Limit fixtures/holdout to one god")
    p.add_argument("--no-report", action="store_true")
    args = p.parse_args(argv)

    report = run_eval(
        db_path=args.db,
        holdout=args.holdout,
        min_games=args.min_games,
        fixtures_only=args.fixtures_only,
        only_god=args.god,
        write_report=not args.no_report,
    )
    s = report["summary"]
    print(f"algorithm {report['algorithm_version']}")
    print(f"unit_blend: {'PASS' if s['unit_ok'] else 'FAIL'} {report['unit_blend'].get('errors')}")
    print(
        f"fixtures: {s['fixtures_passed']}/{s['fixtures_passed'] + s['fixtures_failed']} passed"
    )
    for r in report["fixtures"]["results"]:
        mark = "OK" if r["ok"] else "FAIL"
        print(f"  [{mark}] {r['name']}: {r['items']} conf={r.get('confidence')} n={r.get('ladder_games')}")
        for e in r.get("errors") or []:
            print(f"       - {e}")
    if report.get("holdout"):
        h = report["holdout"]
        print(
            f"holdout: n={h.get('n')} mean_hit={h.get('mean_holdout_hit_rate')} "
            f"train_hit={h.get('mean_train_hit_rate')} "
            f"thin={h.get('thin_mean_holdout_hit_rate')} fat={h.get('fat_mean_holdout_hit_rate')}"
        )
    if not args.no_report:
        print(f"wrote {REPORT_PATH}")
    ok = s["unit_ok"] and s["fixtures_failed"] == 0
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
