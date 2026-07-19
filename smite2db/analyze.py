"""CLI: run metrics analysis and inspect tier lists."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from .db import DEFAULT_DB, connect
from .metrics.engine import run_full_analysis
from .metrics.tier_list import WEIGHTS


def cmd_run(args: argparse.Namespace) -> int:
    weights = dict(WEIGHTS)
    if args.patch_weight is not None:
        weights["patch"] = args.patch_weight
    if args.kit_weight is not None:
        weights["kit"] = args.kit_weight
    if args.build_weight is not None:
        weights["build"] = args.build_weight
    # renormalize if custom weights set
    if any(x is not None for x in (args.patch_weight, args.kit_weight, args.build_weight)):
        total = sum(weights.values())
        weights = {k: v / total for k, v in weights.items()}

    print(f"Analyzing {args.db}")
    print(f"Weights: {weights}")
    run_full_analysis(db_path=args.db, weights=weights, verbose=not args.quiet)
    return 0


def cmd_tiers(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    scope = args.scope
    rows = conn.execute(
        """
        SELECT tier, rank_in_scope, entity_name, score, patch_score, kit_score,
               build_score, confidence, rationale
        FROM tier_list
        WHERE scope = ? AND entity_type = ?
        ORDER BY rank_in_scope
        """,
        (scope, args.entity_type),
    ).fetchall()
    if not rows:
        scopes = [
            r["scope"]
            for r in conn.execute(
                "SELECT DISTINCT scope FROM tier_list ORDER BY scope"
            )
        ]
        print(f"No rows for scope={scope!r}. Available scopes:")
        for s in scopes:
            print(f"  - {s}")
        return 1

    print(f"Tier list — {scope} ({args.entity_type})")
    print("=" * 72)
    current = None
    for r in rows:
        if args.tier and r["tier"] != args.tier:
            continue
        if r["tier"] != current:
            current = r["tier"]
            print(f"\n### {current}-Tier")
        conf = f"{r['confidence']:.0%}" if r["confidence"] is not None else "?"
        print(
            f"  {r['rank_in_scope']:3}. [{r['tier']}] {r['entity_name']:22} "
            f"score={r['score']:5.1f}  patch={_fmt(r['patch_score'])}  "
            f"kit={_fmt(r['kit_score'])}  build={_fmt(r['build_score'])}  conf={conf}"
        )
        if args.verbose and r["rationale"]:
            print(f"       {r['rationale'][:160]}")
    conn.close()
    return 0


def cmd_god(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    g = conn.execute(
        "SELECT * FROM gods WHERE name LIKE ? COLLATE NOCASE",
        (args.name,),
    ).fetchone()
    if not g:
        g = conn.execute(
            "SELECT * FROM gods WHERE name LIKE ? COLLATE NOCASE",
            (f"%{args.name}%",),
        ).fetchone()
    if not g:
        print(f"No god matching {args.name!r}")
        return 1

    print(f"=== {g['name']} metrics ===")
    print(f"Pantheon: {g['pantheon']} | Damage: {g['primary_damage_type']}")

    kit = conn.execute(
        "SELECT * FROM god_kit_metrics WHERE god_id = ?", (g["id"],)
    ).fetchone()
    if kit:
        print("\nKit")
        print(f"  Power:    {kit['kit_power_score']:.1f}/100")
        print(f"  Burst:    {kit['kit_burst_score']:.1f}  DPS: {kit['kit_dps_score']:.1f}  Utility: {kit['kit_utility_score']:.1f}")
        print(f"  Scaling:  {kit['primary_scaling']} (STR avg {kit['avg_scaling_str']:.0f}% / INT avg {kit['avg_scaling_int']:.0f}%)")
        print(f"  CC/Heal/Mobility abilities: {kit['cc_count']}/{kit['heal_count']}/{kit['mobility_count']}")
        print(f"  Stance variants: {kit['stance_variants']} | abilities: {kit['ability_count']}")

    print("\nAbility breakdown")
    for ab in conn.execute(
        """
        SELECT a.slot, a.name, m.damage_rank5, m.scaling_str_pct, m.scaling_int_pct,
               m.cooldown_rank5, m.has_cc, m.has_mobility, m.power_score, m.utility_score,
               m.burst_proxy, m.dps_proxy
        FROM abilities a
        LEFT JOIN ability_metrics m ON m.ability_id = a.id
        WHERE a.god_id = ?
        ORDER BY a.slot_order
        """,
        (g["id"],),
    ):
        flags = []
        if ab["has_cc"]:
            flags.append("CC")
        if ab["has_mobility"]:
            flags.append("Mobility")
        flag_s = f" [{', '.join(flags)}]" if flags else ""
        print(
            f"  {ab['slot']:14} {ab['name']:22} "
            f"pwr={_fmt(ab['power_score'])} dmg5={_fmt(ab['damage_rank5'])} "
            f"STR={_fmt(ab['scaling_str_pct'])}% INT={_fmt(ab['scaling_int_pct'])}% "
            f"cd={_fmt(ab['cooldown_rank5'])}s{flag_s}"
        )

    build = conn.execute(
        "SELECT * FROM god_build_metrics WHERE god_id = ?", (g["id"],)
    ).fetchone()
    if build:
        print("\nBuild")
        print(f"  Starter:  {build['recommended_starter']}")
        print(f"  Cores:    {build['core_items_json']}")
        print(f"  Defense:  {build['defense_items_json']}")
        print(f"  Hybrid:   {build['hybrid_items_json']}")
        print(f"  Relics:   {build['relic_suggestions']}")
        print(f"  Synergy:  {_fmt(build['build_synergy_score'])}  Meta items: {_fmt(build['meta_item_score'])}")
        if build["build_notes"]:
            print(f"  Notes:    {build['build_notes']}")

    patch = conn.execute(
        "SELECT * FROM entity_patch_summary WHERE entity_type='god' AND entity_name=?",
        (g["name"],),
    ).fetchone()
    if patch:
        print("\nPatch momentum")
        print(f"  Trajectory:     {patch['trajectory']}")
        print(f"  Net weighted:   {patch['net_weighted_score']:+.2f}")
        print(f"  Last 5 patches: {patch['recent_5_score']:+.2f}")
        print(f"  Last 10:        {patch['recent_10_score']:+.2f}")
        print(f"  Buff/Nerf events: {patch['buff_events']}/{patch['nerf_events']} across {patch['patches_touched']} patches")
        print(f"  Last: {patch['last_direction']} — {patch['last_patch']} ({patch['last_patch_date']})")

        print("\n  Recent impact rows:")
        for row in conn.execute(
            """
            SELECT p.name, p.number_label, i.direction, i.magnitude, i.weighted_score, i.sample_text
            FROM patch_impacts i
            JOIN patch_notes p ON p.id = i.patch_id
            WHERE i.entity_type='god' AND i.entity_name=?
            ORDER BY p.id ASC
            LIMIT 12
            """,
            (g["name"],),
        ):
            print(
                f"    {row['number_label'] or row['name'][:20]:8} "
                f"{row['direction']:6} mag={row['magnitude']:.1f} "
                f"w={row['weighted_score']:+.2f}  { (row['sample_text'] or '')[:70]}"
            )
    else:
        print("\nPatch momentum: no attributed changes found")

    print("\nTier placements")
    for t in conn.execute(
        """
        SELECT scope, tier, rank_in_scope, score, rationale
        FROM tier_list
        WHERE entity_type='god' AND entity_name=?
        ORDER BY scope
        """,
        (g["name"],),
    ):
        print(f"  {t['scope']:22} {t['tier']}-tier  rank #{t['rank_in_scope']}  score={t['score']:.1f}")
        if args.verbose:
            print(f"    {t['rationale'][:140]}")

    conn.close()
    return 0


def cmd_momentum(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    et = args.entity_type
    rows = conn.execute(
        f"""
        SELECT entity_name, trajectory, net_weighted_score, recent_5_score,
               buff_events, nerf_events, patches_touched, last_patch
        FROM entity_patch_summary
        WHERE entity_type = ?
        ORDER BY net_weighted_score {"DESC" if args.top else "ASC"}
        LIMIT ?
        """,
        (et, args.limit),
    ).fetchall()
    label = "most buffed (weighted)" if args.top else "most nerfed (weighted)"
    print(f"Patch momentum — {et} — {label}")
    for i, r in enumerate(rows, 1):
        print(
            f"  {i:2}. {r['entity_name']:24} {r['trajectory']:9} "
            f"net={r['net_weighted_score']:+6.2f}  r5={r['recent_5_score']:+5.2f}  "
            f"B/N={r['buff_events']}/{r['nerf_events']}  last={r['last_patch']}"
        )
    conn.close()
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "json":
        scopes = [args.scope] if args.scope else [
            r["scope"] for r in conn.execute("SELECT DISTINCT scope FROM tier_list")
        ]
        payload = {}
        for scope in scopes:
            rows = conn.execute(
                """
                SELECT tier, rank_in_scope, entity_type, entity_name, score,
                       patch_score, kit_score, build_score, novelty_score,
                       confidence, rationale, components_json
                FROM tier_list WHERE scope = ? ORDER BY rank_in_scope
                """,
                (scope,),
            ).fetchall()
            payload[scope] = [dict(r) for r in rows]
        # attach analysis meta
        meta = {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM analysis_meta")}
        doc = {"meta": meta, "tiers": payload}
        out.write_text(json.dumps(doc, indent=2), encoding="utf-8")
        print(f"Wrote {out}")
    elif args.format == "csv":
        rows = conn.execute(
            """
            SELECT scope, entity_type, entity_name, tier, rank_in_scope, score,
                   patch_score, kit_score, build_score, confidence, rationale
            FROM tier_list
            WHERE (? IS NULL OR scope = ?)
            ORDER BY scope, rank_in_scope
            """,
            (args.scope, args.scope),
        ).fetchall()
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(rows[0].keys() if rows else [])
            for r in rows:
                w.writerow([r[k] for k in r.keys()])
        print(f"Wrote {out} ({len(rows)} rows)")
    elif args.format == "md":
        scope = args.scope or "overall"
        rows = conn.execute(
            """
            SELECT tier, rank_in_scope, entity_name, score, patch_score, kit_score,
                   build_score, rationale
            FROM tier_list
            WHERE scope = ? AND entity_type = 'god'
            ORDER BY rank_in_scope
            """,
            (scope,),
        ).fetchall()
        lines = [
            f"# SMITE 2 Tier List — `{scope}`",
            "",
            "Generated from ability metrics, item/build synergy, and **patch-note momentum** "
            "(recency-weighted buff/nerf analysis of official wiki patch notes).",
            "",
            "| Rank | Tier | God | Score | Patch | Kit | Build |",
            "|-----:|:----:|-----|------:|------:|----:|------:|",
        ]
        for r in rows:
            lines.append(
                f"| {r['rank_in_scope']} | **{r['tier']}** | {r['entity_name']} | "
                f"{r['score']:.1f} | {_fmt(r['patch_score'])} | {_fmt(r['kit_score'])} | "
                f"{_fmt(r['build_score'])} |"
            )
        lines.append("")
        lines.append("## Rationale (top 15)")
        lines.append("")
        for r in rows[:15]:
            lines.append(f"### {r['rank_in_scope']}. {r['entity_name']} ({r['tier']})")
            lines.append(f"{r['rationale']}")
            lines.append("")
        out.write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote {out}")
    else:
        print(f"Unknown format {args.format}", file=sys.stderr)
        return 1
    conn.close()
    return 0


def cmd_scopes(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    for r in conn.execute(
        """
        SELECT scope, entity_type, COUNT(*) AS n,
               SUM(CASE WHEN tier='S' THEN 1 ELSE 0 END) AS s_count
        FROM tier_list
        GROUP BY scope, entity_type
        ORDER BY scope
        """
    ):
        print(f"  {r['scope']:28} {r['entity_type']:5}  n={r['n']:3}  S-tier={r['s_count']}")
    conn.close()
    return 0


def _fmt(v) -> str:
    if v is None:
        return "  -"
    return f"{v:5.1f}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="SMITE 2 metrics analysis & tier lists (patch-note weighted)."
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Recompute all metrics and tier lists")
    p_run.add_argument("--quiet", action="store_true")
    p_run.add_argument("--patch-weight", type=float, default=None)
    p_run.add_argument("--kit-weight", type=float, default=None)
    p_run.add_argument("--build-weight", type=float, default=None)
    p_run.set_defaults(func=cmd_run)

    p_tiers = sub.add_parser("tiers", help="Show a tier list")
    p_tiers.add_argument("--scope", default="overall")
    p_tiers.add_argument("--entity-type", default="god", choices=["god", "item"])
    p_tiers.add_argument("--tier", default=None, help="Filter to S/A/B/C/D")
    p_tiers.add_argument("-v", "--verbose", action="store_true")
    p_tiers.set_defaults(func=cmd_tiers)

    p_god = sub.add_parser("god", help="Full metrics report for one god")
    p_god.add_argument("name")
    p_god.add_argument("-v", "--verbose", action="store_true")
    p_god.set_defaults(func=cmd_god)

    p_mom = sub.add_parser("momentum", help="Buff/nerf leaderboard from patches")
    p_mom.add_argument("--entity-type", default="god", choices=["god", "item"])
    p_mom.add_argument("--limit", type=int, default=20)
    p_mom.add_argument("--top", action="store_true", default=True)
    p_mom.add_argument("--bottom", action="store_true", help="Most nerfed")
    p_mom.set_defaults(func=cmd_momentum)

    p_exp = sub.add_parser("export", help="Export tier list to json/csv/md")
    p_exp.add_argument("-o", "--output", type=Path, required=True)
    p_exp.add_argument("--format", choices=["json", "csv", "md"], default="md")
    p_exp.add_argument("--scope", default=None)
    p_exp.set_defaults(func=cmd_export)

    p_sc = sub.add_parser("scopes", help="List available tier list scopes")
    p_sc.set_defaults(func=cmd_scopes)

    args = parser.parse_args(argv)
    if args.cmd == "momentum" and args.bottom:
        args.top = False
    if not args.db.exists() and args.cmd != "run":
        # run creates analysis tables but needs base db
        pass
    if not args.db.exists():
        print(f"Database not found: {args.db}\nRun: python -m smite2db.scrape", file=sys.stderr)
        return 1
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
