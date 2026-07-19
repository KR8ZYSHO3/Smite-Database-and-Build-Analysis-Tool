"""Simple CLI to explore the SMITE 2 SQLite database."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .db import DEFAULT_DB, connect


def cmd_stats(conn) -> None:
    tables = ["gods", "abilities", "items", "patch_notes", "patch_changes"]
    print("SMITE 2 database counts")
    print("-" * 32)
    for t in tables:
        n = conn.execute(f"SELECT COUNT(*) AS c FROM {t}").fetchone()["c"]
        print(f"  {t:16} {n}")
    meta = conn.execute("SELECT key, value FROM meta ORDER BY key").fetchall()
    if meta:
        print("\nMeta")
        print("-" * 32)
        for row in meta:
            val = row["value"]
            if len(val) > 80:
                val = val[:77] + "..."
            print(f"  {row['key']}: {val}")


def cmd_god(conn, name: str) -> None:
    row = conn.execute(
        "SELECT * FROM gods WHERE name LIKE ? COLLATE NOCASE",
        (name,),
    ).fetchone()
    if not row:
        row = conn.execute(
            "SELECT * FROM gods WHERE name LIKE ? COLLATE NOCASE",
            (f"%{name}%",),
        ).fetchone()
    if not row:
        print(f"No god matching {name!r}")
        return
    print(f"{row['name']} — {row['title']}")
    print(f"  Pantheon: {row['pantheon']}")
    print(f"  Damage:   {row['primary_damage_type']}")
    print(f"  Roles:    {row['roles']}")
    print(f"  Wiki:     {row['wiki_url']}")
    if row["lore"]:
        lore = row["lore"][:400] + ("..." if len(row["lore"]) > 400 else "")
        print(f"\nLore:\n  {lore}")
    abs_ = conn.execute(
        "SELECT * FROM abilities WHERE god_id = ? ORDER BY slot_order",
        (row["id"],),
    ).fetchall()
    print("\nAbilities:")
    for ab in abs_:
        print(f"\n  [{ab['slot']}] {ab['name']}")
        if ab["short_label"]:
            print(f"    ({ab['short_label']})")
        if ab["description"]:
            print(f"    {ab['description']}")
        if ab["stats_text"]:
            for line in ab["stats_text"].splitlines():
                print(f"      • {line}")


def cmd_item(conn, name: str) -> None:
    row = conn.execute(
        "SELECT * FROM items WHERE name LIKE ? COLLATE NOCASE",
        (name,),
    ).fetchone()
    if not row:
        row = conn.execute(
            "SELECT * FROM items WHERE name LIKE ? COLLATE NOCASE",
            (f"%{name}%",),
        ).fetchone()
    if not row:
        print(f"No item matching {name!r}")
        return
    print(f"{row['name']}")
    print(f"  Tier/Type: {row['tier']} / {row['item_type']}")
    print(f"  Cost:      {row['cost']} (total {row['total_cost']})")
    print(f"  Wiki:      {row['wiki_url']}")
    if row["stats_text"]:
        print("  Stats:")
        for line in row["stats_text"].splitlines():
            print(f"    • {line}")
    if row["passive"]:
        print(f"  Passive: {row['passive']}")
    if row["active"]:
        print(f"  Active:  {row['active']}")
    if row["recipe_json"]:
        print(f"  Recipe:  {row['recipe_json']}")


def cmd_search(conn, term: str, kind: str) -> None:
    term_like = f"%{term}%"
    if kind in ("all", "gods"):
        rows = conn.execute(
            "SELECT name, pantheon, primary_damage_type FROM gods WHERE name LIKE ? COLLATE NOCASE ORDER BY name LIMIT 30",
            (term_like,),
        ).fetchall()
        if rows:
            print("Gods:")
            for r in rows:
                print(f"  - {r['name']} ({r['pantheon']}, {r['primary_damage_type']})")
    if kind in ("all", "items"):
        rows = conn.execute(
            "SELECT name, tier, total_cost FROM items WHERE name LIKE ? COLLATE NOCASE ORDER BY name LIMIT 30",
            (term_like,),
        ).fetchall()
        if rows:
            print("Items:")
            for r in rows:
                print(f"  - {r['name']} (tier {r['tier']}, {r['total_cost']}g)")
    if kind in ("all", "abilities"):
        rows = conn.execute(
            """
            SELECT a.name AS ability, a.slot, g.name AS god
            FROM abilities a JOIN gods g ON g.id = a.god_id
            WHERE a.name LIKE ? COLLATE NOCASE
            ORDER BY a.name LIMIT 30
            """,
            (term_like,),
        ).fetchall()
        if rows:
            print("Abilities:")
            for r in rows:
                print(f"  - {r['ability']} [{r['slot']}] — {r['god']}")
    if kind in ("all", "patches"):
        rows = conn.execute(
            "SELECT name, release_date, phase FROM patch_notes WHERE name LIKE ? COLLATE NOCASE OR content_text LIKE ? ORDER BY name DESC LIMIT 20",
            (term_like, term_like),
        ).fetchall()
        if rows:
            print("Patches:")
            for r in rows:
                print(f"  - {r['name']} ({r['phase']}, {r['release_date']})")


def cmd_patch(conn, name: str) -> None:
    row = conn.execute(
        "SELECT * FROM patch_notes WHERE name LIKE ? COLLATE NOCASE",
        (f"%{name}%",),
    ).fetchone()
    if not row:
        print(f"No patch matching {name!r}")
        return
    print(f"{row['name']}")
    print(f"  Phase:  {row['phase']} ({row['number_label']})")
    print(f"  Date:   {row['release_date']}")
    print(f"  Title:  {row['title']}")
    print(f"  Wiki:   {row['wiki_url']}")
    changes = conn.execute(
        """
        SELECT section, entity_name, change_text
        FROM patch_changes WHERE patch_id = ?
        ORDER BY change_order LIMIT 40
        """,
        (row["id"],),
    ).fetchall()
    print(f"\nChanges (first {len(changes)}):")
    for ch in changes:
        ent = f" [{ch['entity_name']}]" if ch["entity_name"] else ""
        print(f"  • ({ch['section']}){ent} {ch['change_text'][:160]}")


def cmd_list(conn, kind: str, limit: int) -> None:
    if kind == "gods":
        rows = conn.execute(
            "SELECT name, pantheon, primary_damage_type FROM gods ORDER BY name LIMIT ?",
            (limit,),
        ).fetchall()
        for r in rows:
            print(f"{r['name']:20} {r['pantheon'] or '':12} {r['primary_damage_type'] or ''}")
    elif kind == "items":
        rows = conn.execute(
            "SELECT name, tier, total_cost, item_type FROM items ORDER BY (total_cost IS NULL), total_cost, name LIMIT ?",
            (limit,),
        ).fetchall()
        for r in rows:
            print(f"{r['name']:30} tier={r['tier'] or '?':12} {r['total_cost'] or '-'}g  {r['item_type'] or ''}")
    elif kind == "patches":
        rows = conn.execute(
            "SELECT name, phase, release_date FROM patch_notes ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        for r in rows:
            print(f"{r['name']:40} {r['phase'] or '':14} {r['release_date'] or ''}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Query the SMITE 2 SQLite database.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("stats", help="Show row counts")
    p_god = sub.add_parser("god", help="Show a god and abilities")
    p_god.add_argument("name")
    p_item = sub.add_parser("item", help="Show an item")
    p_item.add_argument("name")
    p_patch = sub.add_parser("patch", help="Show a patch")
    p_patch.add_argument("name")
    p_search = sub.add_parser("search", help="Search names")
    p_search.add_argument("term")
    p_search.add_argument(
        "--kind",
        choices=["all", "gods", "items", "abilities", "patches"],
        default="all",
    )
    p_list = sub.add_parser("list", help="List entries")
    p_list.add_argument("kind", choices=["gods", "items", "patches"])
    p_list.add_argument("-n", "--limit", type=int, default=50)
    p_sql = sub.add_parser("sql", help="Run a read-only SQL query")
    p_sql.add_argument("query")

    args = parser.parse_args(argv)
    if not args.db.exists():
        print(f"Database not found: {args.db}\nRun: python -m smite2db.scrape", file=sys.stderr)
        return 1

    conn = connect(args.db)
    if args.cmd == "stats":
        cmd_stats(conn)
    elif args.cmd == "god":
        cmd_god(conn, args.name)
    elif args.cmd == "item":
        cmd_item(conn, args.name)
    elif args.cmd == "patch":
        cmd_patch(conn, args.name)
    elif args.cmd == "search":
        cmd_search(conn, args.term, args.kind)
    elif args.cmd == "list":
        cmd_list(conn, args.kind, args.limit)
    elif args.cmd == "sql":
        q = args.query.strip()
        if not q.lower().startswith("select"):
            print("Only SELECT queries allowed.", file=sys.stderr)
            return 1
        rows = conn.execute(q).fetchall()
        if not rows:
            print("(no rows)")
        else:
            cols = rows[0].keys()
            print(" | ".join(cols))
            print("-" * 60)
            for r in rows:
                print(" | ".join(str(r[c]) if r[c] is not None else "" for c in cols))
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
