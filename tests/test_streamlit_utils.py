from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from app.streamlit_app import _safe_filter, load_tables, _coalesce_na, _display_season, _load_available_seasons, _infer_current_season


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


def test_coalesce_na_with_pandas_na() -> None:
    """Test that _coalesce_na handles pandas.NA values without crashing."""
    # Test with pandas.NA values
    result = _coalesce_na(pd.NA, pd.NA, default="(status unknown)")
    assert result == "(status unknown)"

    result = _coalesce_na(pd.NA, "questionable", default="(status unknown)")
    assert result == "questionable"

    result = _coalesce_na("doubtful", pd.NA, default="(status unknown)")
    assert result == "doubtful"


def test_coalesce_na_with_none_values() -> None:
    """Test that _coalesce_na handles None values."""
    result = _coalesce_na(None, None, default="fallback")
    assert result == "fallback"

    result = _coalesce_na(None, "available", default="fallback")
    assert result == "available"


def test_coalesce_na_with_injuries_scenario() -> None:
    """Test _coalesce_na with a simulated injuries DataFrame scenario."""
    # Create a minimal injuries DataFrame with NA values
    injuries_df = pd.DataFrame({
        "event_id": ["test_123"],
        "player": ["Test Player"],
        "status": [pd.NA],
        "designation": [pd.NA],
        "note": ["test note"]
    })

    # Simulate the logic from render_matchup_expander
    row = injuries_df.iloc[0]
    status = _coalesce_na(row.get("status"), row.get("designation"), default="(status unknown)")

    assert status == "(status unknown)"


def test_load_available_seasons_empty_data(tmp_path):
    """Test that _load_available_seasons returns current season when no data is available."""
    # Create empty database
    db_path = tmp_path / "empty.db"
    import sqlite3
    with sqlite3.connect(db_path) as con:
        # Create empty defense_ratings table
        con.execute("CREATE TABLE defense_ratings (season INTEGER)")
        con.commit()

    # Test with empty edges_df and no seasons in DB
    empty_edges_df = pd.DataFrame()
    result = _load_available_seasons(db_path, empty_edges_df)

    current_season = _infer_current_season()
    assert result == [current_season], f"Expected [current season], got {result}"


def test_load_available_seasons_union_logic(tmp_path):
    """Test that _load_available_seasons properly unions seasons from edges and DB."""
    # Create database with 2024 season
    db_path = tmp_path / "test.db"
    import sqlite3
    with sqlite3.connect(db_path) as con:
        con.execute("CREATE TABLE defense_ratings (season INTEGER)")
        con.execute("INSERT INTO defense_ratings VALUES (2024)")
        con.commit()

    # Create edges_df with seasons 2023, 2025
    edges_df = pd.DataFrame({
        "season": [2023, 2025, 2023],  # Include duplicate to test uniqueness
        "player": ["Player A", "Player B", "Player C"]
    })

    result = _load_available_seasons(db_path, edges_df)

    # Should return union {2023, 2024, 2025} sorted descending
    expected = [2025, 2024, 2023]  # descending order
    assert result == expected, f"Expected {expected}, got {result}"


def test_load_available_seasons_with_na_values(tmp_path):
    """Test that _load_available_seasons properly handles NA values."""
    # Create empty database
    db_path = tmp_path / "empty.db"
    import sqlite3
    with sqlite3.connect(db_path) as con:
        con.execute("CREATE TABLE defense_ratings (season INTEGER)")
        con.commit()

    # Create edges_df with NA values and valid seasons
    edges_df = pd.DataFrame({
        "season": [2023, pd.NA, None, 2024, "invalid"],
        "player": ["Player A", "Player B", "Player C", "Player D", "Player E"]
    })

    result = _load_available_seasons(db_path, edges_df)

    # Should return {2023, 2024} sorted descending, ignoring NA/None/invalid
    expected = [2024, 2023]
    assert result == expected, f"Expected {expected}, got {result}"


def test_display_season_handles_nullable_int64():
    """Test that _display_season converts nullable Int64 to string with 'Unknown' for NA."""
    # Test with nullable Int64 series
    series = pd.Series([2023, 2024, pd.NA], dtype="Int64")
    result = _display_season(series)

    expected = pd.Series(["2023", "2024", "Unknown"])
    pd.testing.assert_series_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


def test_display_season_handles_regular_int():
    """Test that _display_season handles regular int series."""
    series = pd.Series([2023, 2024])
    result = _display_season(series)

    expected = pd.Series(["2023", "2024"])
    pd.testing.assert_series_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


def test_display_season_empty_series():
    """Test that _display_season handles empty series."""
    empty_series = pd.Series([], dtype="Int64")
    result = _display_season(empty_series)

    assert result.empty
    assert len(result) == 0


def test_display_season_mixed_values():
    """Test _display_season with mixed values including None and NaN."""
    series = pd.Series([2023, None, pd.NA, 2025], dtype="object")
    result = _display_season(series)

    # Should convert None, pd.NA to "Unknown", keep valid values as strings
    expected_values = ["2023", "Unknown", "Unknown", "2025"]
    assert result.tolist() == expected_values


def test_coalesce_na_comprehensive():
    """Comprehensive test for _coalesce_na covering edge cases from the plan."""
    # Test the exact case from the plan: _coalesce_na(pd.NA, "", None, "Q") == "Q"
    result = _coalesce_na(pd.NA, "", None, "Q")
    assert result == "Q"

    # Test all NA-like values
    result = _coalesce_na(pd.NA, None, "", default="fallback")
    assert result == "fallback"

    # Test with first valid value
    result = _coalesce_na(pd.NA, None, "first_valid", "second_valid", default="fallback")
    assert result == "first_valid"

    # Test with pandas NaN
    import numpy as np
    result = _coalesce_na(np.nan, pd.NA, "valid", default="fallback")
    assert result == "valid"
