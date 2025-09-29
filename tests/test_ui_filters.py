import sqlite3
from pathlib import Path

import pandas as pd

from app.streamlit_app import _infer_current_season, _load_available_seasons, apply_season_filter


def test_apply_season_filter_handles_na_values():
    df = pd.DataFrame(
        {
            "season": [2023, pd.NA, "2024", None, "  "],
            "ev_per_dollar": [0.1, 0.2, 0.3, 0.4, 0.5],
        }
    )

    available_seasons = [2023, 2024, 2025]
    filtered = apply_season_filter(df, [2024], available_seasons)
    assert not filtered.empty
    assert filtered["ev_per_dollar"].tolist() == [0.3]

    # Selecting season with NA entries should simply drop them without raising
    filtered_na = apply_season_filter(df, [2023], available_seasons)
    assert filtered_na["ev_per_dollar"].tolist() == [0.1]


def test_apply_season_filter_without_season_column_returns_original():
    df = pd.DataFrame({"value": [1, 2, 3]})
    available_seasons = [2025]

    filtered = apply_season_filter(df, [2025], available_seasons)
    assert filtered.equals(df)

    filtered_no_selection = apply_season_filter(df, [], available_seasons)
    assert filtered_no_selection.equals(df)


def test_load_available_seasons_falls_back_when_empty(tmp_path):
    db_path = tmp_path / "seasons.db"
    with sqlite3.connect(db_path):
        pass

    seasons = _load_available_seasons(db_path, pd.DataFrame())
    assert seasons == [_infer_current_season()]
