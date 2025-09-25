import pytest

from utils.teams import infer_is_home, infer_offense_team, normalize_team_code, parse_event_id


def test_parse_event_id_returns_components():
    date_str, away, home = parse_event_id("2023-01-01-KC-LV")
    assert date_str == "2023-01-01"
    assert away == "KC"
    assert home == "LV"


def test_infer_offense_team_uses_defense_hint():
    offense = infer_offense_team("2023-01-01-KC-LV", "LV")
    assert offense == "KC"
    offense_home = infer_offense_team("2023-01-01-KC-LV", "KC")
    assert offense_home == "LV"


def test_infer_is_home_identifies_home_and_away():
    assert infer_is_home("2023-01-01-KC-LV", "LV") == 1
    assert infer_is_home("2023-01-01-KC-LV", "KC") == 0
    assert infer_is_home("bad", "KC") is None


def test_normalize_team_code_handles_aliases():
    assert normalize_team_code("LVR") == "LV"
    assert normalize_team_code("kc") == "KC"
    assert normalize_team_code(None) is None
