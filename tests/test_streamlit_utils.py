from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from app.streamlit_app import _safe_filter, load_tables


def test_safe_filter_returns_empty_dataframe() -> None:
    df = pd.DataFrame()
    result = _safe_filter(df, "col", 1)

    assert isinstance(result, pd.DataFrame)
    assert result.empty
    assert list(result.columns) == ["col"]


def test_load_tables_provides_context_columns(tmp_path) -> None:
    db_path = Path(tmp_path) / "ui_context.db"
    with sqlite3.connect(db_path) as con:
        con.execute(
            "CREATE TABLE edges (event_id TEXT, player TEXT, market TEXT, pos TEXT, line REAL, odds REAL)"
        )
        con.execute(
            "CREATE TABLE qb_props_odds (event_id TEXT, player TEXT, season INT, def_team TEXT)"
        )
        con.execute(
            "CREATE TABLE projections_qb (event_id TEXT, player TEXT, mu REAL)"
        )
        con.execute(
            "CREATE TABLE current_best_lines (player TEXT, market TEXT, book TEXT, line REAL)"
        )
        con.execute(
            "CREATE TABLE odds_snapshots (snap_id TEXT, created_at TEXT)"
        )
        con.commit()

    tables = load_tables.__wrapped__(db_path)
    assert {"team", "season", "week", "proe", "ed_pass_rate", "pace"}.issubset(
        set(tables["scheme"].columns)
    )
    assert {"event_id", "temp_f", "wind_mph", "precip", "indoor"}.issubset(
        set(tables["weather"].columns)
    )
    assert "pos" in tables["edges"].columns


def test_books_fallback_does_not_error() -> None:
    df = pd.DataFrame({"book": []})
    books = sorted(df.get("book", pd.Series(dtype=str)).dropna().unique().tolist())
    assert books == []
