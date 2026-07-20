"""
One-command refresh: optional wiki scrape → analyze → export web.

Examples:
  python -m smite2db.refresh              # analyze + export (fast)
  python -m smite2db.refresh --scrape     # scrape all then analyze + export
  python -m smite2db.refresh --scrape patches
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .db import DEFAULT_DB


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Refresh SMITE 2 metrics + web export")
    p.add_argument("--db", type=Path, default=DEFAULT_DB)
    p.add_argument(
        "--scrape",
        nargs="*",
        metavar="TARGET",
        help="If set, scrape first. Optional targets: gods items patches (default all)",
    )
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--skip-export", action="store_true")
    p.add_argument("--skip-analyze", action="store_true")
    args = p.parse_args(argv)

    verbose = not args.quiet

    if args.scrape is not None:
        from .scrape import run_scrape

        targets = set(args.scrape) if args.scrape else {"gods", "items", "patches"}
        if verbose:
            print(f"Scraping: {', '.join(sorted(targets))} …")
        # Full scrape resets; patch-only keeps gods/items
        reset = targets >= {"gods", "items", "patches"} or "gods" in targets
        run_scrape(db_path=args.db, targets=targets, reset=reset, verbose=verbose)

    if not args.skip_analyze:
        from .metrics.engine import run_full_analysis

        if verbose:
            print("Analyzing metrics …")
        run_full_analysis(db_path=args.db, verbose=verbose)

    if not args.skip_export:
        from .export_web import export_web

        if verbose:
            print("Exporting web data …")
        out = export_web(db_path=args.db, rebuild_builds=True)
        if verbose:
            print(f"Done → {out}")

    if verbose:
        print("Refresh complete. Re-drop docs/ on Netlify if hosting there.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
