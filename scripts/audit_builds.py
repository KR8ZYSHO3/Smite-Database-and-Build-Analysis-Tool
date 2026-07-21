"""Audit exported / live Conquest builds for quality issues."""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from smite2db.db import DEFAULT_DB, connect  # noqa: E402
from smite2db.conquest_builds import (  # noqa: E402
    DAMAGE_ROLES_NEED_PEN,
    DEFAULT_MAX_SHOP_ACTIVES,
    MIN_BUILD_PEN,
    build_god_build,
    generate_all,
    load_items,
)


def path_names(gb: dict) -> list[str]:
    items = gb.get("items") or gb.get("full_path") or []
    return [i.get("name") if isinstance(i, dict) else str(i) for i in items]


def pen_total(gb: dict) -> float:
    items = gb.get("items") or []
    t = 0.0
    for it in items:
        if isinstance(it, dict):
            t += float(it.get("pen") or 0)
    return t


def active_count(gb: dict) -> int:
    if gb.get("active_count") is not None:
        return int(gb["active_count"])
    return sum(1 for i in (gb.get("items") or []) if isinstance(i, dict) and i.get("is_active"))


def audit_payload(roles_data: dict) -> dict:
    issues = []
    by_role_paths: dict[str, list[tuple[str, tuple[str, ...]]]] = defaultdict(list)
    item_freq = Counter()
    starter_freq = Counter()
    arch_freq = Counter()
    n = 0
    pen_fail = 0
    active_over = 0
    empty = 0

    for role, data in roles_data.items():
        for gb in data.get("recommended_gods") or []:
            n += 1
            god = gb.get("god") or "?"
            names = path_names(gb)
            if not names:
                empty += 1
                issues.append(f"EMPTY {role} {god}")
                continue
            key = tuple(names)
            by_role_paths[role].append((god, key))
            for nm in names:
                item_freq[nm] += 1
            st = (gb.get("starter") or {}).get("name") if isinstance(gb.get("starter"), dict) else gb.get("starter")
            if st:
                starter_freq[str(st)] += 1
            if gb.get("archetype"):
                arch_freq[str(gb["archetype"])] += 1

            if role in DAMAGE_ROLES_NEED_PEN and pen_total(gb) < MIN_BUILD_PEN:
                pen_fail += 1
                issues.append(f"PEN_LOW {role} {god} pen={pen_total(gb):.0f} path={names}")

            ac = active_count(gb)
            if ac > DEFAULT_MAX_SHOP_ACTIVES + 1:  # allow hard max 3
                active_over += 1
                issues.append(f"ACTIVES {role} {god} n={ac}")

            # Support shouldn't be full lifesteal DPS
            if role == "Support":
                blob = " ".join(names).lower()
                if any(k in blob for k in ("bloodforge", "devourer", "deathbringer", "demon blade")):
                    issues.append(f"SUP_DPS {god} {names}")

            # Mid shouldn't be full tank aura stack only
            if role == "Mid":
                tankish = sum(
                    1
                    for nm in names
                    if any(
                        k in nm.lower()
                        for k in ("breastplate", "genji", "spectral", "thebes", "contagion", "sovereign")
                    )
                )
                if tankish >= 4:
                    issues.append(f"MID_TANK {god} {names}")

    # Cookie-cutter: identical full paths within role
    clones = []
    for role, pairs in by_role_paths.items():
        counts = Counter(k for _, k in pairs)
        for path, c in counts.items():
            if c >= 3:
                gods = [g for g, k in pairs if k == path]
                clones.append((role, c, gods[:8], path))
                issues.append(f"CLONE x{c} {role}: {', '.join(gods[:6])}…")

    # Pairwise overlap within role (avg jaccard)
    jaccards = []
    for role, pairs in by_role_paths.items():
        paths = [set(k) for _, k in pairs]
        if len(paths) < 2:
            continue
        for i in range(len(paths)):
            for j in range(i + 1, min(i + 15, len(paths))):  # sample neighbors
                a, b = paths[i], paths[j]
                if not a or not b:
                    continue
                jaccards.append(len(a & b) / len(a | b))

    avg_j = sum(jaccards) / len(jaccards) if jaccards else 0

    return {
        "n_builds": n,
        "empty": empty,
        "pen_fail": pen_fail,
        "active_over": active_over,
        "clone_groups": len(clones),
        "clones_detail": clones[:12],
        "avg_pairwise_jaccard_sample": round(avg_j, 3),
        "top_items": item_freq.most_common(15),
        "top_starters": starter_freq.most_common(10),
        "top_archetypes": arch_freq.most_common(12),
        "issue_count": len(issues),
        "issues_sample": issues[:40],
    }


def main() -> None:
    # Prefer regenerating live from engine for truth
    print("Generating builds from DB engine…")
    conn = connect(DEFAULT_DB)
    payload = generate_all(conn)
    conn.close()
    roles = payload.get("roles") or {}
    report = audit_payload(roles)
    print(json.dumps({k: v for k, v in report.items() if k != "clones_detail"}, indent=2))
    print("\n--- clone groups ---")
    for role, c, gods, path in report["clones_detail"]:
        print(f"  {role} x{c}: {gods}")
        print(f"    {list(path)}")
    print("\n--- issues sample ---")
    for line in report["issues_sample"]:
        print(" ", line)

    out = ROOT / "data" / "build_audit.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
