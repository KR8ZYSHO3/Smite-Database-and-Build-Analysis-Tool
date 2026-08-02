"""
Meta lab reports: role staples, answer-item coverage, patch trajectories,
tank-shred package scores, and situational flex catalogs.

Pure analysis on smite2.db + optional builds dict from conquest_builds.generate_all.
"""

from __future__ import annotations

import json
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Answer / situational item catalog (role-agnostic identities)
# ---------------------------------------------------------------------------

ANSWER_CATALOG: dict[str, dict[str, Any]] = {
    "heal": {
        "label": "vs heals / sustain",
        "short": "heal",
        "items": [
            "Divine Ruin",
            "Brawler's Beat Stick",
            "Brawler’s Beat Stick",  # curly apostrophe variant
            "Stygian Anchor",
            "Toxic Blade",
        ],
        "why": "25% healing reduction — stops Yogi's, Aphro, Cu sustain, lifesteal.",
    },
    "crit": {
        "label": "vs crit",
        "short": "crit",
        "items": ["Spectral Armor"],
        "why": "Cut crit damage on you and nearby allies (Carry freefire).",
    },
    "attack_speed": {
        "label": "vs attack speed",
        "short": "AS",
        "items": ["Midgardian Mail", "Toxic Blade", "Stygian Anchor"],
        "why": "Slow freefire AAs; Midgardian stacks when they hit you.",
    },
    "magic": {
        "label": "vs magic damage",
        "short": "magic",
        "items": [
            "Genji's Guard",
            "Phoenix Feather",
            "Oni Hunter's Garb",
            "Void Stone",
        ],
        "why": "Magical protections / mitigation into mid and magical junglers.",
    },
    "physical": {
        "label": "vs physical damage",
        "short": "phys",
        "items": [
            "Breastplate of Valor",
            "Berserker's Shield",
            "Midgardian Mail",
            "Spectral Armor",
            "Void Shield",
        ],
        "why": "Physical bulk into ADCs, hunters, physical junglers.",
    },
    "cc_dive": {
        "label": "vs CC / dive",
        "short": "CC",
        "items": ["Magi's Cloak", "Spirit Robe", "Mantle Of Discord", "Mantle of Discord"],
        "why": "Absorb or survive hard CC and all-ins.",
    },
    "tanks_hp": {
        "label": "vs high HP / tanks",
        "short": "tanks",
        "items": [
            "Soul Reaver",
            "Ethereal Staff",
            "Obsidian Shard",
            "Titan's Bane",
            "Stone of Binding",
            "Void Stone",
            "The Executioner",
        ],
        "why": "%HP, pen, and prot shred so fat targets take real damage.",
    },
}

# Role-prioritized flex chips shown on builds (order = display priority)
ROLE_FLEX_CHIPS: dict[str, list[str]] = {
    "Carry": ["heal", "tanks_hp", "cc_dive", "physical"],
    "Mid": ["heal", "tanks_hp", "cc_dive", "magic"],
    "Jungle": ["heal", "tanks_hp", "cc_dive", "physical"],
    "Solo": ["heal", "magic", "physical", "cc_dive", "tanks_hp", "crit", "attack_speed"],
    "Support": ["crit", "attack_speed", "magic", "heal", "cc_dive", "physical"],
}

# Expected "almost every game" answers for coverage scoring
ROLE_COVERAGE_EXPECT: dict[str, list[str]] = {
    "Support": ["crit", "attack_speed", "magic", "heal"],
    "Solo": ["heal", "physical", "magic", "cc_dive"],
    "Mid": ["heal", "tanks_hp"],
    "Carry": ["heal", "tanks_hp"],
    "Jungle": ["heal", "tanks_hp"],
}

# Tank-shred package pieces (magical offline / mid)
TANK_SHRED_MAGE = {
    "anti_heal": ["Divine Ruin", "Brawler's Beat Stick", "Brawler’s Beat Stick", "Stygian Anchor"],
    "pct_hp": ["Soul Reaver", "Ethereal Staff"],
    "pen": ["Obsidian Shard", "Spear of Desolation", "Titan's Bane"],
    "shred": ["Stone of Binding", "Void Stone", "The Executioner"],
}


def _norm_name(n: str) -> str:
    return (
        str(n or "")
        .replace("'", "'")
        .replace("'", "'")
        .replace("'", "'")
        .strip()
        .lower()
    )


def _item_set(names: list[str]) -> set[str]:
    return {_norm_name(x) for x in names if x}


def _path_item_names(gb: dict[str, Any]) -> list[str]:
    out: list[str] = []
    st = gb.get("starter")
    if isinstance(st, dict) and st.get("name"):
        out.append(st["name"])
    elif isinstance(st, str):
        out.append(st)
    for it in gb.get("items") or gb.get("full_path") or []:
        if isinstance(it, dict) and it.get("name"):
            out.append(it["name"])
        elif isinstance(it, str):
            out.append(it)
    return out


def _path_has_answer(path_names: list[str], answer_key: str) -> bool:
    cat = ANSWER_CATALOG.get(answer_key) or {}
    want = _item_set(list(cat.get("items") or []))
    have = _item_set(path_names)
    return bool(want & have)


def _matching_answer_items(path_names: list[str], answer_key: str) -> list[str]:
    cat = ANSWER_CATALOG.get(answer_key) or {}
    want = list(cat.get("items") or [])
    have = _item_set(path_names)
    # de-dupe by norm, prefer first spelling in catalog
    seen: set[str] = set()
    hit: list[str] = []
    for n in want:
        nn = _norm_name(n)
        if nn in have and nn not in seen:
            seen.add(nn)
            # canonical display without curly variants preferred
            if "'" in n and "Beat" in n:
                hit.append("Brawler's Beat Stick")
            else:
                hit.append(n.replace("'", "'"))
    return hit


def flex_chips_for_path(role: str, path_names: list[str]) -> list[dict[str, Any]]:
    """Situational flex chips: what's already in path vs suggested swaps."""
    chips: list[dict[str, Any]] = []
    for key in ROLE_FLEX_CHIPS.get(role, list(ANSWER_CATALOG.keys())):
        cat = ANSWER_CATALOG[key]
        have = _matching_answer_items(path_names, key)
        # Suggest primary item (first unique catalog name)
        suggest = []
        seen = set()
        for n in cat["items"]:
            nn = _norm_name(n)
            if nn in seen:
                continue
            if "brawler" in nn:
                label = "Brawler's Beat Stick"
            else:
                label = n.replace("'", "'")
            seen.add(nn)
            suggest.append(label)
            if len(suggest) >= 2:
                break
        chips.append(
            {
                "id": key,
                "label": cat["label"],
                "short": cat["short"],
                "why": cat["why"],
                "in_path": bool(have),
                "path_items": have,
                "suggest": suggest,
            }
        )
    return chips


def _collect_role_paths(builds: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """role -> list of {god, items, starter, ...} from generate_all report."""
    out: dict[str, list[dict[str, Any]]] = {}
    roles = (builds or {}).get("roles") or {}
    for role, data in roles.items():
        paths = []
        for gb in data.get("recommended_gods") or []:
            names = _path_item_names(gb)
            paths.append(
                {
                    "god": gb.get("god") or gb.get("entity_name"),
                    "tier": gb.get("tier"),
                    "rank": gb.get("rank"),
                    "items": names,
                    "flex_chips": flex_chips_for_path(role, names),
                }
            )
        out[role] = paths
    return out


def compute_role_staples(role_paths: dict[str, list[dict[str, Any]]], top_n: int = 15) -> dict[str, Any]:
    report: dict[str, Any] = {}
    for role, paths in role_paths.items():
        ctr: Counter[str] = Counter()
        n = max(1, len(paths))
        for p in paths:
            # count unique items per path once
            for name in set(p.get("items") or []):
                if name and name not in ("Selflessness", "Warrior's Axe", "Conduit Gem", "Bumba's Cudgel", "Bumba's Golden Dagger", "Gilded Arrow", "Death's Toll", "Bluestone Pendant"):
                    ctr[name] += 1
        top = [
            {
                "name": name,
                "paths": count,
                "pct": round(100.0 * count / n, 1),
            }
            for name, count in ctr.most_common(top_n)
        ]
        report[role] = {
            "path_count": len(paths),
            "staples": top,
        }
    return report


def compute_answer_coverage(role_paths: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    report: dict[str, Any] = {}
    for role, paths in role_paths.items():
        expect = ROLE_COVERAGE_EXPECT.get(role, ["heal"])
        n = max(1, len(paths))
        by_answer: dict[str, Any] = {}
        for key in expect:
            covered = sum(1 for p in paths if _path_has_answer(p.get("items") or [], key))
            missing_gods = [
                p["god"]
                for p in paths
                if not _path_has_answer(p.get("items") or [], key)
            ][:12]
            by_answer[key] = {
                "label": ANSWER_CATALOG[key]["label"],
                "covered": covered,
                "total": len(paths),
                "pct": round(100.0 * covered / n, 1),
                "missing_sample": missing_gods,
            }
        # gaps: paths missing 2+ expected answers
        multi_gap = []
        for p in paths:
            miss = [k for k in expect if not _path_has_answer(p.get("items") or [], k)]
            if len(miss) >= 2:
                multi_gap.append({"god": p["god"], "missing": miss})
        report[role] = {
            "expected": expect,
            "answers": by_answer,
            "multi_gap_sample": multi_gap[:15],
            "note": (
                "Coverage = recommended paths that already include an answer item. "
                "Low % means the default shell under-answers that threat — use flex chips."
            ),
        }
    return report


def compute_tank_shred_scores(role_paths: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """Score Mid/Solo/Jungle magical-ish paths for shred package completeness."""
    out: dict[str, Any] = {}
    for role in ("Mid", "Solo", "Jungle", "Support"):
        paths = role_paths.get(role) or []
        scored = []
        for p in paths:
            have = _item_set(p.get("items") or [])
            parts = {}
            score = 0
            for part, names in TANK_SHRED_MAGE.items():
                ok = bool(have & _item_set(names))
                parts[part] = ok
                if ok:
                    score += 1
            scored.append(
                {
                    "god": p["god"],
                    "score": score,
                    "max": len(TANK_SHRED_MAGE),
                    "parts": parts,
                    "complete": score >= 3,
                }
            )
        scored.sort(key=lambda x: (-x["score"], x["god"] or ""))
        complete_n = sum(1 for s in scored if s["complete"])
        out[role] = {
            "package": list(TANK_SHRED_MAGE.keys()),
            "complete_paths": complete_n,
            "total": len(scored),
            "pct_complete": round(100.0 * complete_n / max(1, len(scored)), 1),
            "leaders": scored[:10],
            "weak": [s for s in scored if s["score"] <= 1][:10],
        }
    return out


def compute_trajectories(conn: sqlite3.Connection, limit: int = 12) -> dict[str, Any]:
    def fetch(etype: str) -> dict[str, Any]:
        rows = conn.execute(
            """
            SELECT entity_name, trajectory, recent_5_score, recent_10_score,
                   net_weighted_score, buff_events, nerf_events, last_patch,
                   last_direction, patches_touched
            FROM entity_patch_summary
            WHERE entity_type = ?
            """,
            (etype,),
        ).fetchall()
        data = [dict(r) for r in rows]
        rising = sorted(
            [r for r in data if (r.get("recent_5_score") or 0) > 0.05],
            key=lambda r: -(r.get("recent_5_score") or 0),
        )[:limit]
        falling = sorted(
            [r for r in data if (r.get("recent_5_score") or 0) < -0.05],
            key=lambda r: (r.get("recent_5_score") or 0),
        )[:limit]
        volatile = sorted(
            [r for r in data if (r.get("trajectory") or "") == "volatile"],
            key=lambda r: -(abs(r.get("net_weighted_score") or 0)),
        )[:limit]
        newish = [r for r in data if (r.get("trajectory") or "") in ("new", "rising") and (r.get("patches_touched") or 0) <= 3]
        newish = sorted(newish, key=lambda r: -(r.get("recent_5_score") or 0))[:limit]
        return {
            "rising": rising,
            "falling": falling,
            "volatile": volatile,
            "new_or_fresh": newish,
            "total_tracked": len(data),
        }

    # Axis meta: sum recent axes across gods
    axis_acc: dict[str, float] = defaultdict(float)
    axis_n = 0
    for r in conn.execute(
        "SELECT recent_axes_json FROM entity_patch_summary WHERE entity_type='god' AND recent_axes_json IS NOT NULL"
    ):
        try:
            ax = json.loads(r[0] or "{}")
        except json.JSONDecodeError:
            continue
        if not isinstance(ax, dict):
            continue
        axis_n += 1
        for k, v in ax.items():
            try:
                axis_acc[k] += float(v)
            except (TypeError, ValueError):
                pass
    axis_avg = {
        k: round(v / max(1, axis_n), 3)
        for k, v in sorted(axis_acc.items(), key=lambda kv: -abs(kv[1]))
    }

    return {
        "gods": fetch("god"),
        "items": fetch("item"),
        "patch_axes_avg_r5": axis_avg,
        "axis_note": "Average recent-5 patch axes across gods — positive = meta tilted toward that axis.",
    }


def compute_role_tier_snapshot(conn: sqlite3.Connection) -> dict[str, Any]:
    snap: dict[str, Any] = {}
    for role in ("Carry", "Mid", "Jungle", "Solo", "Support"):
        rows = conn.execute(
            """
            SELECT entity_name, tier, rank_in_scope, score, rationale
            FROM tier_list
            WHERE scope = ? AND entity_type = 'god'
            ORDER BY rank_in_scope
            """,
            (f"role:{role}",),
        ).fetchall()
        by_tier: dict[str, list] = defaultdict(list)
        for r in rows:
            by_tier[r["tier"] or "?"].append(
                {
                    "name": r["entity_name"],
                    "rank": r["rank_in_scope"],
                    "score": round(r["score"] or 0, 1),
                }
            )
        snap[role] = {
            "count": len(rows),
            "s_tier": by_tier.get("S", []),
            "a_tier": by_tier.get("A", []),
            "tier_counts": {t: len(v) for t, v in sorted(by_tier.items())},
        }
    return snap


def build_flex_catalog() -> dict[str, Any]:
    """Static situational flex guide for the UI."""
    roles = {}
    for role, keys in ROLE_FLEX_CHIPS.items():
        chips = []
        for key in keys:
            cat = ANSWER_CATALOG[key]
            items = []
            seen = set()
            for n in cat["items"]:
                nn = _norm_name(n)
                if nn in seen:
                    continue
                seen.add(nn)
                items.append("Brawler's Beat Stick" if "brawler" in nn else n.replace("'", "'"))
            chips.append(
                {
                    "id": key,
                    "label": cat["label"],
                    "short": cat["short"],
                    "why": cat["why"],
                    "items": items[:4],
                }
            )
        roles[role] = chips
    return {
        "roles": roles,
        "all_answers": {
            k: {
                "label": v["label"],
                "why": v["why"],
                "items": list(dict.fromkeys(
                    ("Brawler's Beat Stick" if "brawler" in _norm_name(i) else i.replace("'", "'"))
                    for i in v["items"]
                )),
            }
            for k, v in ANSWER_CATALOG.items()
        },
    }


def attach_flex_to_builds(builds: dict[str, Any]) -> dict[str, Any]:
    """Mutate/copy builds report: add flex_chips on each recommended god path."""
    if not builds or "roles" not in builds:
        return builds
    for role, data in (builds.get("roles") or {}).items():
        for gb in data.get("recommended_gods") or []:
            names = _path_item_names(gb)
            gb["flex_chips"] = flex_chips_for_path(role, names)
            # compact coverage flags for UI badges
            gb["answer_flags"] = {
                k: _path_has_answer(names, k)
                for k in ROLE_FLEX_CHIPS.get(role, [])
            }
    return builds


def generate_meta_lab(
    conn: sqlite3.Connection,
    builds: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Full meta lab payload for export + UI."""
    if builds is None:
        from ..conquest_builds import generate_all

        builds = generate_all(conn)

    builds = attach_flex_to_builds(builds)
    role_paths = _collect_role_paths(builds)

    lab = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "game": "SMITE 2",
        "disclaimer": (
            "Kit + patch model — not live win rates. "
            "Staples/coverage reflect algorithm recommended paths; flex chips are situational swaps."
        ),
        "flex_catalog": build_flex_catalog(),
        "role_staples": compute_role_staples(role_paths),
        "answer_coverage": compute_answer_coverage(role_paths),
        "tank_shred": compute_tank_shred_scores(role_paths),
        "trajectories": compute_trajectories(conn),
        "role_tiers": compute_role_tier_snapshot(conn),
        "weekly_themes": _infer_themes(conn, role_paths),
    }
    return lab


def _infer_themes(conn: sqlite3.Connection, role_paths: dict[str, list]) -> list[str]:
    themes: list[str] = []
    # Support spectral coverage
    sup = None
    # recompute quick support crit coverage
    from_cov = None
    try:
        cov = compute_answer_coverage(role_paths)
        sc = (cov.get("Support") or {}).get("answers") or {}
        crit_pct = (sc.get("crit") or {}).get("pct", 0)
        heal_pct = (sc.get("heal") or {}).get("pct", 0)
        if crit_pct < 40:
            themes.append(
                f"Support paths under-buy anti-crit (Spectral on ~{crit_pct}% of recs) — flex Spectral almost every game."
            )
        if heal_pct < 35:
            themes.append(
                f"Support/Solo anti-heal is rare in defaults (~{heal_pct}% support) — Stygian/Brawler's is a live flex."
            )
    except Exception:
        pass

    traj = compute_trajectories(conn, limit=5)
    top_g = (traj.get("gods") or {}).get("rising") or []
    if top_g:
        names = ", ".join(r["entity_name"] for r in top_g[:4])
        themes.append(f"Gods rising (r5 patch): {names}.")
    top_i = (traj.get("items") or {}).get("rising") or []
    if top_i:
        names = ", ".join(r["entity_name"] for r in top_i[:4])
        themes.append(f"Items hot (r5 patch): {names}.")

    axes = traj.get("patch_axes_avg_r5") or {}
    if axes:
        top_ax = list(axes.items())[:3]
        themes.append(
            "Patch axes (avg r5): "
            + ", ".join(f"{k} {v:+.2f}" for k, v in top_ax)
            + "."
        )

    if not themes:
        themes.append("Run a fresh scrape/analysis after each OB for updated themes.")
    return themes


def write_meta_lab_markdown(lab: dict[str, Any], path: Path) -> None:
    lines = [
        "# SMITE 2 Meta Lab",
        "",
        lab.get("disclaimer") or "",
        "",
        f"_Generated: {lab.get('generated_at')}_",
        "",
        "## Weekly themes",
        "",
    ]
    for t in lab.get("weekly_themes") or []:
        lines.append(f"- {t}")
    lines += ["", "## Role staples (top items in recommended paths)", ""]
    for role, data in (lab.get("role_staples") or {}).items():
        lines.append(f"### {role} ({data.get('path_count')} paths)")
        lines.append("")
        lines.append("| Item | Paths | % |")
        lines.append("|------|------:|--:|")
        for s in data.get("staples") or []:
            lines.append(f"| {s['name']} | {s['paths']} | {s['pct']} |")
        lines.append("")
    lines += ["## Answer coverage", ""]
    for role, data in (lab.get("answer_coverage") or {}).items():
        lines.append(f"### {role}")
        for key, ans in (data.get("answers") or {}).items():
            lines.append(
                f"- **{ans['label']}**: {ans['covered']}/{ans['total']} ({ans['pct']}%)"
            )
        lines.append("")
    lines += ["## Trajectories — gods rising", ""]
    for r in ((lab.get("trajectories") or {}).get("gods") or {}).get("rising") or []:
        lines.append(
            f"- {r['entity_name']}: r5 {r.get('recent_5_score', 0):+.2f} ({r.get('trajectory')})"
        )
    lines += ["", "## Trajectories — items rising", ""]
    for r in ((lab.get("trajectories") or {}).get("items") or {}).get("rising") or []:
        lines.append(
            f"- {r['entity_name']}: r5 {r.get('recent_5_score', 0):+.2f}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_meta_lab_cli(db_path: Path | str | None = None) -> dict[str, Any]:
    from ..db import DEFAULT_DB, connect
    from ..conquest_builds import generate_all

    conn = connect(db_path or DEFAULT_DB)
    builds = generate_all(conn)
    lab = generate_meta_lab(conn, builds)
    root = Path(__file__).resolve().parents[2]
    out_json = root / "data" / "meta_lab.json"
    out_md = root / "data" / "meta_lab.md"
    out_json.write_text(json.dumps(lab, indent=2), encoding="utf-8")
    write_meta_lab_markdown(lab, out_md)
    conn.close()
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    return lab
