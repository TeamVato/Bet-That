import pandas as pd
import pytest

from engine.scheme import SchemeConfig, compute_team_week_scheme


def test_compute_team_week_scheme_positive_when_passing_more_than_expected():
    buf_rows = {
        "game_id": ["g1"] * 6,
        "season": [2024] * 6,
        "week": [1] * 6,
        "posteam": ["BUF"] * 6,
        "pass": [1, 1, 1, 0, 1, 1],
        "down": [1, 2, 3, 1, 2, 3],
        "ydstogo": [10, 8, 6, 7, 5, 4],
        "yardline_100": [60, 50, 45, 40, 35, 30],
        "game_seconds_remaining": [900, 870, 840, 810, 780, 750],
    }
    league_baseline = {
        "game_id": ["g2"] * 6,
        "season": [2024] * 6,
        "week": [1] * 6,
        "posteam": ["NYJ"] * 6,
        "pass": [0, 0, 0, 1, 0, 0],
        "down": [1, 2, 3, 1, 2, 3],
        "ydstogo": [10, 8, 6, 7, 5, 4],
        "yardline_100": [60, 50, 45, 40, 35, 30],
        "game_seconds_remaining": [900, 870, 840, 810, 780, 750],
    }

    pbp = pd.concat([pd.DataFrame(buf_rows), pd.DataFrame(league_baseline)], ignore_index=True)

    result = compute_team_week_scheme(pbp, SchemeConfig(seasons=[2024]))
    buf_row = result[result["team"] == "BUF"].iloc[0]

    assert buf_row["proe"] == pytest.approx(buf_row["pass_rate"] - buf_row["expected_pass"])
    assert buf_row["proe"] > 0
    assert buf_row["plays"] == 6
