"""Orchestrate full metrics pipeline and persist results."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from ..db import DEFAULT_DB, connect
from .ability_metrics import compute_ability_metrics
from .build_metrics import compute_build_metrics
from .patch_impact import compute_patch_impacts
from .tier_list import WEIGHTS, compute_tier_lists

METRICS_SCHEMA = Path(__file__).resolve().parent.parent / "metrics_schema.sql"


def init_metrics_schema(conn: sqlite3.Connection) -> None:
    sql = METRICS_SCHEMA.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()


def run_full_analysis(
    db_path: Path | str | None = None,
    weights: dict[str, float] | None = None,
    verbose: bool = True,
) -> dict:
    conn = connect(db_path)
    init_metrics_schema(conn)

    results: dict = {"weights": {**WEIGHTS, **(weights or {})}}

    if verbose:
        print("1/4 Ability & kit metrics …")
    results["abilities"] = compute_ability_metrics(conn)

    if verbose:
        print("2/4 Patch impact (buff/nerf momentum) …")
    results["patches"] = compute_patch_impacts(conn)

    if verbose:
        print("3/4 Build / item synergy …")
    results["builds"] = compute_build_metrics(conn)

    if verbose:
        print("4/4 Tier lists …")
    results["tiers"] = compute_tier_lists(conn, weights=weights)

    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO analysis_meta(key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        ("last_analysis_at", now),
    )
    conn.execute(
        "INSERT INTO analysis_meta(key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        ("last_analysis_results", json.dumps(results)),
    )
    conn.execute(
        "INSERT INTO analysis_meta(key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        ("weights", json.dumps(results["weights"])),
    )
    conn.commit()
    conn.close()

    if verbose:
        print("Analysis complete.")
        for k, v in results.items():
            print(f"  {k}: {v}")
    return results
