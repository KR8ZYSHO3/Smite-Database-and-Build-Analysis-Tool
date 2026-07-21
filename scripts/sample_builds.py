from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from smite2db.conquest_builds import ROLE_PROFILES, build_god_build, load_items
from smite2db.db import DEFAULT_DB, connect


def main() -> None:
    conn = connect(DEFAULT_DB)
    items = load_items(conn)
    gods = [dict(r) for r in conn.execute(
        "SELECT id AS god_id, name AS entity_name, primary_damage_type, pantheon, roles FROM gods ORDER BY name"
    )]
    # alias for build_god_build
    for g in gods:
        g["god_id"] = g["god_id"]
        g.setdefault("name", g.get("entity_name"))

    samples = [
        "Ah Puch", "Achilles", "Charon", "Medusa", "Geb", "Ymir", "Discordia",
        "Thor", "Nemesis", "Poseidon", "Izanami", "Vulcan", "Ganesha", "Bastet",
        "Kukulkan", "Ra", "Athena", "Hades", "Susano", "Jing Wei",
    ]
    by_name = {g["entity_name"]: g for g in gods}

    for name in samples:
        g = by_name.get(name)
        if not g:
            print("missing", name)
            continue
        try:
            roles = json.loads(g.get("roles") or "[]")
        except json.JSONDecodeError:
            roles = []
        role_names = []
        for r in roles:
            s = str(r)
            if "Role." in s:
                role_names.append(s.split("Role.")[-1].strip(" '\"}"))
            else:
                role_names.append(s)
        # primary roles first, then others for multi-role check
        check = list(dict.fromkeys(role_names + ["Support", "Mid", "Solo", "Jungle", "Carry"]))
        for role in check:
            if role not in ROLE_PROFILES:
                continue
            # only print primary roles + Mid for mages + Support for guardians
            if role not in role_names and not (
                (role == "Mid" and (g.get("primary_damage_type") or "").lower() == "magical")
                or (role == "Support" and name in ("Geb", "Ymir", "Ganesha", "Athena", "Charon"))
            ):
                if role not in role_names:
                    continue
            b = build_god_build(conn, items, role, g)
            path = b.get("items") or []
            names = [i["name"] for i in path]
            st = (b.get("starter") or {}).get("name")
            pen = sum(float(i.get("pen") or 0) for i in path)
            print(
                f"{name:12} {role:8} arch={str(b.get('archetype')):18} "
                f"pen={pen:4.0f} act={b.get('active_count')} st={st} | {' > '.join(names)}"
            )
    conn.close()


if __name__ == "__main__":
    main()
