"""Test edge key population with schedule-based fallbacks."""
import pandas as pd

from engine.edge_engine import EdgeEngine, EdgeEngineConfig


def test_edge_engine_uses_schedule_fallback_for_missing_week(tmp_path):
    """Test that EdgeEngine uses schedule lookup when week is missing from props/projections."""
    config = EdgeEngineConfig(database_path=tmp_path / "edges.db", export_dir=tmp_path)

    # Mock schedule lookup with event_id -> season/week mapping
    schedule_lookup = {
        "2025-01-12-BAL-PIT": {"season": 2025, "week": 19},
        "2025-01-12-PIT-BAL": {"season": 2025, "week": 19},  # Alternative key format
    }

    engine = EdgeEngine(config, schedule_lookup=schedule_lookup)

    # Props with missing week data
    props_df = pd.DataFrame([{
        "event_id": "2025-01-12-BAL-PIT",
        "player": "Lamar Jackson",
        "market": "player_pass_yds",
        "line": 225.5,
        "over_odds": -110,
        "under_odds": -110,
        "book": "draftkings",
        "season": 2025,
        "week": pd.NA,  # Missing week
        "def_team": "PIT",
        "team": "BAL",
        "pos": "QB",
    }])

    # Projections with missing week data
    projections_df = pd.DataFrame([{
        "event_id": "2025-01-12-BAL-PIT",
        "player": "Lamar Jackson",
        "mu": 240.0,
        "sigma": 35.0,
        "season": 2025,
        "week": pd.NA,  # Missing week
        "def_team": "PIT",
        "team": "BAL",
    }])

    edges_df = engine.compute_edges(props_df, projections_df)

    assert not edges_df.empty
    assert len(edges_df) == 1

    # Verify week was populated from schedule lookup
    assert edges_df.iloc[0]["week"] == 19
    assert edges_df.iloc[0]["season"] == 2025


def test_edge_engine_uses_schedule_fallback_for_missing_opponent_def_code(tmp_path):
    """Test that EdgeEngine infers opponent_def_code from schedule when missing."""
    config = EdgeEngineConfig(database_path=tmp_path / "edges.db", export_dir=tmp_path)

    # Mock schedule lookup
    schedule_lookup = {
        "2025-01-12-BAL-PIT": {"season": 2025, "week": 19},
    }

    engine = EdgeEngine(config, schedule_lookup=schedule_lookup)

    # Props with missing opponent defense code but valid team
    props_df = pd.DataFrame([{
        "event_id": "2025-01-12-BAL-PIT",
        "player": "Lamar Jackson",
        "market": "player_pass_yds",
        "line": 225.5,
        "over_odds": -110,
        "under_odds": -110,
        "book": "draftkings",
        "season": 2025,
        "week": 19,
        "def_team": pd.NA,  # Missing opponent defense
        "team": "BAL",  # Player's team
        "pos": "QB",
    }])

    projections_df = pd.DataFrame([{
        "event_id": "2025-01-12-BAL-PIT",
        "player": "Lamar Jackson",
        "mu": 240.0,
        "sigma": 35.0,
        "season": 2025,
        "week": 19,
        "def_team": pd.NA,  # Missing opponent defense
        "team": "BAL",
    }])

    edges_df = engine.compute_edges(props_df, projections_df)

    assert not edges_df.empty
    assert len(edges_df) == 1

    # Verify opponent_def_code was inferred from event_id parsing
    # BAL-PIT event, BAL is offense, so PIT should be defense
    assert edges_df.iloc[0]["opponent_def_code"] == "PIT"


def test_edge_engine_schedule_fallback_with_alternative_key_format(tmp_path):
    """Test that EdgeEngine tries alternative date-team key formats for schedule lookup."""
    config = EdgeEngineConfig(database_path=tmp_path / "edges.db", export_dir=tmp_path)

    # Schedule lookup with date-team format (common nflverse pattern)
    schedule_lookup = {
        "2025-01-12-BAL-PIT": {"season": 2025, "week": 19},
    }

    engine = EdgeEngine(config, schedule_lookup=schedule_lookup)

    # Props missing both week and opponent defense
    props_df = pd.DataFrame([{
        "event_id": "2025-01-12-BAL-PIT",
        "player": "Josh Allen",
        "market": "player_pass_yds",
        "line": 275.5,
        "over_odds": -115,
        "under_odds": -105,
        "book": "fanduel",
        "season": 2025,
        "week": pd.NA,  # Missing
        "def_team": pd.NA,  # Missing
        "team": "BAL",
        "pos": "QB",
    }])

    projections_df = pd.DataFrame([{
        "event_id": "2025-01-12-BAL-PIT",
        "player": "Josh Allen",
        "mu": 280.0,
        "sigma": 40.0,
        "season": 2025,
        "week": pd.NA,
        "def_team": pd.NA,
        "team": "BAL",
    }])

    edges_df = engine.compute_edges(props_df, projections_df)

    assert not edges_df.empty
    assert len(edges_df) == 1

    # Both should be populated from schedule
    assert edges_df.iloc[0]["week"] == 19
    assert edges_df.iloc[0]["opponent_def_code"] == "PIT"


def test_edge_engine_preserves_existing_values_over_schedule_fallback(tmp_path):
    """Test that EdgeEngine preserves existing values and only uses schedule as fallback."""
    config = EdgeEngineConfig(database_path=tmp_path / "edges.db", export_dir=tmp_path)

    # Schedule lookup with different values
    schedule_lookup = {
        "2025-01-12-BAL-PIT": {"season": 2025, "week": 18},  # Different week
    }

    engine = EdgeEngine(config, schedule_lookup=schedule_lookup)

    # Props with existing values (should take precedence)
    props_df = pd.DataFrame([{
        "event_id": "2025-01-12-BAL-PIT",
        "player": "Lamar Jackson",
        "market": "player_pass_yds",
        "line": 225.5,
        "over_odds": -110,
        "under_odds": -110,
        "book": "draftkings",
        "season": 2025,
        "week": 19,  # Existing value
        "def_team": "PIT",  # Existing value
        "team": "BAL",
        "pos": "QB",
    }])

    projections_df = pd.DataFrame([{
        "event_id": "2025-01-12-BAL-PIT",
        "player": "Lamar Jackson",
        "mu": 240.0,
        "sigma": 35.0,
        "season": 2025,
        "week": 19,  # Existing value
        "def_team": "PIT",  # Existing value
        "team": "BAL",
    }])

    edges_df = engine.compute_edges(props_df, projections_df)

    assert not edges_df.empty
    assert len(edges_df) == 1

    # Should preserve existing values, not use schedule fallback
    assert edges_df.iloc[0]["week"] == 19  # Not 18 from schedule
    assert edges_df.iloc[0]["opponent_def_code"] == "PIT"


def test_edge_engine_handles_missing_schedule_lookup_gracefully(tmp_path):
    """Test that EdgeEngine handles missing schedule lookup without crashing."""
    config = EdgeEngineConfig(database_path=tmp_path / "edges.db", export_dir=tmp_path)

    # No schedule lookup provided
    engine = EdgeEngine(config, schedule_lookup=None)

    props_df = pd.DataFrame([{
        "event_id": "2025-01-12-BAL-PIT",
        "player": "Lamar Jackson",
        "market": "player_pass_yds",
        "line": 225.5,
        "over_odds": -110,
        "under_odds": -110,
        "book": "draftkings",
        "season": 2025,
        "week": pd.NA,  # Missing
        "def_team": pd.NA,  # Missing
        "team": "BAL",
        "pos": "QB",
    }])

    projections_df = pd.DataFrame([{
        "event_id": "2025-01-12-BAL-PIT",
        "player": "Lamar Jackson",
        "mu": 240.0,
        "sigma": 35.0,
        "season": 2025,
        "week": pd.NA,
        "def_team": pd.NA,
        "team": "BAL",
    }])

    # Should not crash, just return edges with missing values
    edges_df = engine.compute_edges(props_df, projections_df)

    assert not edges_df.empty
    assert len(edges_df) == 1

    # Values should remain missing without schedule lookup
    assert pd.isna(edges_df.iloc[0]["week"])
    # opponent_def_code might still be inferred from event parsing


def test_edge_engine_handles_empty_schedule_lookup(tmp_path):
    """Test that EdgeEngine handles empty schedule lookup gracefully."""
    config = EdgeEngineConfig(database_path=tmp_path / "edges.db", export_dir=tmp_path)

    # Empty schedule lookup
    engine = EdgeEngine(config, schedule_lookup={})

    props_df = pd.DataFrame([{
        "event_id": "2025-01-12-BAL-PIT",
        "player": "Lamar Jackson",
        "market": "player_pass_yds",
        "line": 225.5,
        "over_odds": -110,
        "under_odds": -110,
        "book": "draftkings",
        "season": 2025,
        "week": pd.NA,
        "def_team": pd.NA,
        "team": "BAL",
        "pos": "QB",
    }])

    projections_df = pd.DataFrame([{
        "event_id": "2025-01-12-BAL-PIT",
        "player": "Lamar Jackson",
        "mu": 240.0,
        "sigma": 35.0,
        "season": 2025,
        "week": pd.NA,
        "def_team": pd.NA,
        "team": "BAL",
    }])

    # Should not crash with empty schedule
    edges_df = engine.compute_edges(props_df, projections_df)

    assert not edges_df.empty
    assert len(edges_df) == 1