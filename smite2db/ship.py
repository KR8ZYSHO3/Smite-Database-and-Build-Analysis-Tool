"""
One-command ship: analyze → inspire (optional) → fixture gate → export → report.

Examples:
  python -m smite2db.ship
  python -m smite2db.ship --refresh-inspire
  python -m smite2db.ship --skip-analyze          # export + report only
  python -m smite2db.ship --deploy-netlify
  python -m smite2db.ship --scrape patches
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from .db import DEFAULT_DB
from .ship_report import print_report

ROOT = Path(__file__).resolve().parent.parent


def _run_eval_gate(db: Path, verbose: bool, *, fixtures_only: bool = False) -> int:
    """Fixtures always; holdout + win-assoc when inspiration bags exist."""
    from . import eval_builds

    argv = ["--db", str(db), "--min-games", "4"]
    if fixtures_only:
        argv.append("--fixtures-only")
    if not verbose:
        # eval_builds always prints; keep default
        pass
    return eval_builds.main(argv)


def _maybe_inspire(*, refresh: bool, quiet: bool) -> None:
    if not refresh:
        if not quiet:
            print("Inspire: reusing data/tracker_inspiration.json (pass --refresh-inspire to scrape)")
        return
    from .tracker_inspire import main as inspire_main

    if not quiet:
        print("Inspire: scraping tracker.gg …")
    code = inspire_main([])
    if code != 0 and not quiet:
        print("WARN: tracker_inspire returned non-zero; continuing with existing snapshot if any")


def _maybe_netlify(verbose: bool) -> None:
    if shutil.which("netlify") is None:
        if verbose:
            print("Netlify CLI not found — skip deploy")
        return
    if verbose:
        print("Deploying docs/ to Netlify prod …")
    try:
        subprocess.run(
            ["netlify", "deploy", "--prod", "--dir=docs"],
            cwd=ROOT,
            check=True,
        )
    except (subprocess.CalledProcessError, OSError) as exc:
        print(f"WARN: Netlify deploy failed ({exc}). Use local / githack links below.")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Ship SMITE 2 analysis + builds with fixture gates and a delta report"
    )
    p.add_argument("--db", type=Path, default=DEFAULT_DB)
    p.add_argument(
        "--scrape",
        nargs="*",
        metavar="TARGET",
        help="Optional scrape first (gods items patches aspects)",
    )
    p.add_argument("--skip-analyze", action="store_true")
    p.add_argument("--skip-export", action="store_true")
    p.add_argument(
        "--refresh-inspire",
        action="store_true",
        help="Re-scrape tracker.gg inspiration (default: reuse snapshot)",
    )
    p.add_argument("--skip-fixtures", action="store_true", help="Do not gate on eval fixtures")
    p.add_argument("--deploy-netlify", action="store_true")
    p.add_argument("--vs", default="HEAD", help="git rev for tier delta baseline")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args(argv)
    verbose = not args.quiet

    if args.scrape is not None:
        from .scrape import run_scrape

        targets = set(args.scrape) if args.scrape else {"gods", "items", "patches"}
        if verbose:
            print(f"Scraping: {', '.join(sorted(targets))} …")
        full = {"gods", "items", "patches"}
        reset = targets >= full or targets == full
        run_scrape(db_path=args.db, targets=targets, reset=reset, verbose=verbose)

    if not args.skip_analyze:
        from .metrics.engine import run_full_analysis

        if verbose:
            print("Analyzing metrics (kit / patch / build / tiers) …")
        run_full_analysis(db_path=args.db, verbose=verbose)

    _maybe_inspire(refresh=args.refresh_inspire, quiet=args.quiet)

    if not args.skip_fixtures:
        if verbose:
            print("Eval gate (fixtures + holdout / win-assoc) …")
        code = _run_eval_gate(args.db, verbose, fixtures_only=False)
        if code != 0:
            print("SHIP ABORTED: eval gate failed (fixtures and/or holdout floor).")
            return code

    if not args.skip_export:
        from .export_web import export_web

        if verbose:
            print("Exporting web data (rebuild conquest paths) …")
        out = export_web(db_path=args.db, rebuild_builds=True)
        if verbose:
            print(f"Export → {out}")

        # Hard-fail on pen / role-job quality gate (shared clones stay WARN)
        qg_path = ROOT / "data" / "conquest_builds.json"
        if qg_path.is_file():
            import json

            try:
                qg = (json.loads(qg_path.read_text(encoding="utf-8")) or {}).get(
                    "quality_gate"
                ) or {}
            except (OSError, json.JSONDecodeError):
                qg = {}
            pen_fails: list[str] = []
            job_fails: list[str] = []
            for role, info in (qg.get("roles") or {}).items():
                for g in info.get("pen_fail") or []:
                    pen_fails.append(f"{role}:{g}")
                for g in info.get("role_job_fail") or []:
                    job_fails.append(f"{role}:{g}")
            if pen_fails or job_fails:
                print("SHIP ABORTED: quality gate pen/role-job failures.")
                if pen_fails:
                    print(f"  pen_fail: {pen_fails}")
                if job_fails:
                    print(f"  role_job_fail: {job_fails}")
                return 2

    if args.deploy_netlify:
        _maybe_netlify(verbose)

    print_report(vs=args.vs, local_port=args.port, verbose=verbose)
    if verbose:
        print("Ship complete. Commit + push for the githack link to update.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
