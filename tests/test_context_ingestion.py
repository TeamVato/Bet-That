import pandas as pd

from adapters.weather import build_weather
from adapters.injuries import transform_injuries
from adapters.wr_cb_public import attach_event_ids
from engine.scheme import compute_team_week_scheme, SchemeConfig


def test_compute_team_week_scheme_positive_proe():
    pbp = pd.DataFrame(
        {
            "game_id": ["g1", "g1", "g1", "g1"],
            "season": [2023] * 4,
            "week": [1] * 4,
            "posteam": ["KC"] * 4,
            "pass": [1, 1, 0, 1],
            "down": [1, 2, 1, 3],
            "ydstogo": [10, 8, 5, 6],
            "yardline_100": [60, 55, 40, 35],
            "game_seconds_remaining": [900, 860, 820, 780],
        }
    )
    result = compute_team_week_scheme(pbp, SchemeConfig(seasons=[2023]))
    assert not result.empty
    row = result.iloc[0]
    assert row["team"] == "KC"
    assert row["proe"] > -1  # sanity
    assert row["ed_pass_rate"] > 0
    assert row["pace"] > 0


def test_build_weather_marks_indoor():
    schedule = pd.DataFrame(
        {
            "game_id": ["g1"],
            "temp": [68],
            "wind": [5],
            "roof": ["Dome"],
            "surface": ["turf"],
        }
    )
    weather = build_weather(schedule)
    assert weather.iloc[0]["event_id"] == "g1"
    assert weather.iloc[0]["indoor"] == 1


def test_transform_injuries_maps_event():
    raw = pd.DataFrame(
        {
            "season": [2023],
            "week": [1],
            "team": ["KC"],
            "full_name": ["Patrick Mahomes"],
            "report_status": ["Questionable"],
            "report_primary_injury": ["Ankle"],
            "practice_status": ["Limited"],
            "date_modified": ["2023-09-05T00:00:00+00:00"],
        }
    )
    schedule = pd.DataFrame(
        {
            "season": [2023],
            "week": [1],
            "game_id": ["g1"],
            "home_team": ["KC"],
            "away_team": ["DET"],
            "gameday": ["2023-09-07"],
        }
    )
    injuries = transform_injuries(raw, schedule)
    assert injuries.iloc[0]["event_id"] == "g1"


def test_attach_event_ids_assigns_game():
    context = pd.DataFrame(
        {
            "season": [2023],
            "week": [1],
            "team": ["KC"],
            "player": ["Marquez Valdes-Scantling"],
            "note": ["Faces outside coverage"],
            "source_url": ["https://example.com"],
        }
    )
    schedule = pd.DataFrame(
        {
            "season": [2023],
            "week": [1],
            "game_id": ["g1"],
            "home_team": ["KC"],
            "away_team": ["DET"],
        }
    )
    enriched = attach_event_ids(context, schedule)
    assert enriched.iloc[0]["event_id"] == "g1"
