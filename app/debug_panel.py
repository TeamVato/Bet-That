"""Utilities for gathering lightweight debug metrics from the SQLite datastore."""
from __future__ import annotations

import os
import re
import sqlite3
from typing import Any, Dict, Optional, Sequence, Tuple

import pandas as pd

_VALID_IDENT = re.compile(r"^[A-Za-z0-9_]+$")


def _connect(db_path: str) -> sqlite3.Connection:
    """Return a short-lived SQLite connection with row access enabled."""
    con = sqlite3.connect(db_path, timeout=5.0)
    con.row_factory = sqlite3.Row
    return con


def _sanitize_ident(name: str) -> str:
    if not _VALID_IDENT.match(name or ""):
        raise ValueError(f"Unsafe identifier: {name}")
    return name


def table_exists(con: sqlite3.Connection, name: str) -> bool:
    """Return True when the given table exists in the connected database."""
    name = _sanitize_ident(name)
    cur = con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
        (name,),
    )
    return cur.fetchone() is not None


def scalar(
    con: sqlite3.Connection,
    sql: str,
    params: Sequence[Any] | Tuple[Any, ...] = (),
) -> Optional[Any]:
    """Execute a scalar SQL query, returning the single value or None on error."""
    try:
        cur = con.execute(sql, params)
        row = cur.fetchone()
        return None if row is None else row[0]
    except Exception:
        return None


def count_rows(con: sqlite3.Connection, table: str) -> int:
    """Return the row count for the given table (0 when absent or on error)."""
    table = _sanitize_ident(table)
    if not table_exists(con, table):
        return 0
    value = scalar(con, f"SELECT COUNT(*) FROM {table};")
    return int(value or 0)


def max_updated(
    con: sqlite3.Connection,
    table: str,
    col: str = "updated_at",
) -> Optional[str]:
    """Return the MAX(column) value for the table, if both exist."""
    table = _sanitize_ident(table)
    col = _sanitize_ident(col)
    if not table_exists(con, table):
        return None
    return scalar(con, f"SELECT MAX({col}) FROM {table};")


def counts_by(con: sqlite3.Connection, table: str, col: str) -> pd.DataFrame:
    """Return counts grouped by a column; empty frame when unavailable."""
    table = _sanitize_ident(table)
    col = _sanitize_ident(col)
    if not table_exists(con, table):
        return pd.DataFrame(columns=["key", "count"])
    query = (
        f"SELECT {col} AS key, COUNT(*) AS count "
        f"FROM {table} GROUP BY 1 ORDER BY 2 DESC;"
    )
    try:
        return pd.read_sql_query(query, con)
    except Exception:
        return pd.DataFrame(columns=["key", "count"])


def edges_quality(con: sqlite3.Connection) -> Dict[str, Any]:
    """Summarize defensive join coverage for edges."""
    if not table_exists(con, "edges"):
        return {
            "edges_rows": 0,
            "missing_def_code": 0,
            "missing_def_tier": 0,
            "missing_def_score": 0,
        }

    def _q(statement: str) -> int:
        value = scalar(con, statement)
        return int(value or 0)

    rows = _q("SELECT COUNT(*) FROM edges;")
    missing_def_code = _q(
        "SELECT COUNT(*) FROM edges "
        "WHERE opponent_def_code IS NULL OR TRIM(opponent_def_code) = '';"
    )
    missing_def_tier = _q(
        "SELECT COUNT(*) FROM edges "
        "WHERE def_tier IS NULL OR TRIM(def_tier) = '';"
    )
    missing_def_score = _q("SELECT COUNT(*) FROM edges WHERE def_score IS NULL;")
    return {
        "edges_rows": rows,
        "missing_def_code": missing_def_code,
        "missing_def_tier": missing_def_tier,
        "missing_def_score": missing_def_score,
    }


def edges_weather_coverage(con: sqlite3.Connection) -> Dict[str, Any]:
    """Return counts for edges that have matching weather context."""
    total = count_rows(con, "edges")
    if total == 0 or not table_exists(con, "weather"):
        return {
            "edges_with_weather": 0,
            "edges_total": total,
        }
    sql = (
        "SELECT COUNT(*) FROM edges e "
        "WHERE EXISTS ("
        " SELECT 1 FROM weather w "
        " WHERE (w.event_id IS NOT NULL AND w.event_id = e.event_id) "
        "    OR (w.game_id IS NOT NULL AND w.game_id = e.event_id)"
        ");"
    )
    with_cov = scalar(con, sql)
    return {
        "edges_with_weather": int(with_cov or 0),
        "edges_total": total,
    }


def odds_staleness(con: sqlite3.Connection) -> Dict[str, Any]:
    """Return counts of fresh vs stale rows in current_best_lines."""
    if not table_exists(con, "current_best_lines"):
        return {"fresh": 0, "stale": 0}
    fresh_sql = (
        "SELECT COUNT(*) FROM current_best_lines WHERE COALESCE(stale, 0) = 0;"
    )
    stale_sql = (
        "SELECT COUNT(*) FROM current_best_lines WHERE COALESCE(stale, 0) = 1;"
    )
    fresh = scalar(con, fresh_sql)
    stale = scalar(con, stale_sql)
    return {"fresh": int(fresh or 0), "stale": int(stale or 0)}


def active_env_settings() -> Dict[str, Any]:
    """Expose selected environment knobs relevant to the app."""
    return {
        "STALE_MINUTES": int(os.getenv("STALE_MINUTES", "120") or 120),
        "SHRINK_TO_MARKET_WEIGHT": float(os.getenv("SHRINK_TO_MARKET_WEIGHT", "0.35") or 0.35),
        "DEFAULT_SEASONS": os.getenv("DEFAULT_SEASONS", ""),
    }


__all__ = [
    "_connect",
    "table_exists",
    "scalar",
    "count_rows",
    "max_updated",
    "counts_by",
    "edges_quality",
    "edges_weather_coverage",
    "odds_staleness",
    "active_env_settings",
]
