import pandas as pd

from engine.season import infer_season, infer_season_series


def test_infer_season_january_maps_to_previous_year():
    assert infer_season("2025-01-07T18:30:00Z") == 2024


def test_infer_season_august_maps_to_same_year():
    assert infer_season("2024-08-15T00:00:00Z") == 2024


def test_infer_season_series_handles_mixed_values():
    values = pd.Series([
        "2024-09-10T00:00:00Z",
        "2025-02-02T00:00:00Z",
        None,
    ])
    seasons = infer_season_series(values)
    assert int(seasons.iloc[0]) == 2024
    assert int(seasons.iloc[1]) == 2024
    assert pd.isna(seasons.iloc[2])
