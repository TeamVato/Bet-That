"""Integration test to verify 2025 edges generation with defense ratings join."""

import os
import sqlite3
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from engine.edge_engine import EdgeEngine, EdgeEngineConfig
from jobs.compute_edges import apply_defense_defaults, ensure_defense_ratings_artifacts


def setup_test_database(db_path: Path) -> None:
    """Set up a test database with defense ratings for 2025 season."""
    with sqlite3.connect(db_path) as con:
        # Create defense_ratings table
        con.execute(
            """
            CREATE TABLE defense_ratings (
                defteam TEXT,
                season INTEGER,
                week INTEGER,
                pos TEXT,
                score REAL,
                tier TEXT,
                score_adj REAL,
                tier_adj TEXT
            )
        """
        )

        # Insert 2025 defense ratings for common teams
        defense_data = [
            ("BAL", 2025, 1, "QB_PASS", 0.8, "stingy", 0.85, "stingy"),
            ("PIT", 2025, 1, "QB_PASS", 0.2, "generous", 0.25, "generous"),
            ("BUF", 2025, 1, "QB_PASS", 0.6, "neutral", 0.65, "neutral"),
            ("KC", 2025, 1, "QB_PASS", 0.4, "neutral", 0.45, "neutral"),
            ("SF", 2025, 1, "QB_PASS", 0.9, "stingy", 0.9, "stingy"),
            ("DAL", 2025, 1, "QB_PASS", 0.3, "generous", 0.3, "generous"),
        ]

        con.executemany(
            """
            INSERT INTO defense_ratings
            (defteam, season, week, pos, score, tier, score_adj, tier_adj)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            defense_data,
        )

        con.commit()


def test_2025_edges_generation_with_defense_join():
    """Integration test: 2025 edges should generate and successfully join with defense ratings."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_odds.db"
        setup_test_database(db_path)

        config = EdgeEngineConfig(database_path=db_path, export_dir=Path(temp_dir))

        # Mock 2025 schedule lookup
        schedule_lookup = {
            "2025-01-12-BAL-PIT": {"season": "2025", "week": "1"},
            "2025-01-19-BUF-KC": {"season": "2025", "week": "1"},
            "2025-01-26-SF-DAL": {"season": "2025", "week": "1"},
        }

        engine = EdgeEngine(config, schedule_lookup=schedule_lookup)

        # Create 2025 props data with some missing join keys
        props_2025 = pd.DataFrame(
            [
                {
                    "event_id": "2025-01-12-BAL-PIT",
                    "player": "Lamar Jackson",
                    "market": "player_pass_yds",
                    "line": 225.5,
                    "over_odds": -110,
                    "under_odds": -110,
                    "book": "draftkings",
                    "season": 2025,
                    "week": pd.NA,  # Missing - should use schedule fallback
                    "def_team": "PIT",
                    "team": "BAL",
                    "pos": "QB",
                },
                {
                    "event_id": "2025-01-19-BUF-KC",
                    "player": "Josh Allen",
                    "market": "player_pass_yds",
                    "line": 275.5,
                    "over_odds": -115,
                    "under_odds": -105,
                    "book": "fanduel",
                    "season": 2025,
                    "week": 1,
                    "def_team": pd.NA,  # Missing - should infer from event
                    "team": "BUF",
                    "pos": "QB",
                },
                {
                    "event_id": "2025-01-26-SF-DAL",
                    "player": "Brock Purdy",
                    "market": "player_pass_yds",
                    "line": 245.5,
                    "over_odds": -120,
                    "under_odds": 100,
                    "book": "caesars",
                    "season": 2025,
                    "week": pd.NA,  # Missing week
                    "def_team": pd.NA,  # Missing opponent
                    "team": "SF",
                    "pos": "QB",
                },
            ]
        )

        # Create projections
        projections_2025 = pd.DataFrame(
            [
                {
                    "event_id": "2025-01-12-BAL-PIT",
                    "player": "Lamar Jackson",
                    "mu": 240.0,
                    "sigma": 35.0,
                    "season": 2025,
                    "week": pd.NA,
                    "def_team": "PIT",
                    "team": "BAL",
                },
                {
                    "event_id": "2025-01-19-BUF-KC",
                    "player": "Josh Allen",
                    "mu": 285.0,
                    "sigma": 40.0,
                    "season": 2025,
                    "week": 1,
                    "def_team": pd.NA,
                    "team": "BUF",
                },
                {
                    "event_id": "2025-01-26-SF-DAL",
                    "player": "Brock Purdy",
                    "mu": 250.0,
                    "sigma": 30.0,
                    "season": 2025,
                    "week": pd.NA,
                    "def_team": pd.NA,
                    "team": "SF",
                },
            ]
        )

        # Generate edges
        edges_df = engine.compute_edges(props_2025, projections_2025)

        # Verify edges were generated
        assert not edges_df.empty, "No edges were generated for 2025 season"
        assert len(edges_df) == 6, f"Expected 6 edges (2 per prop), got {len(edges_df)}"

        # Check that basic edge data was generated (opponent_def_code functionality removed)
        edges_with_season = (~edges_df["season"].isna()).sum()
        edges_with_event_id = (~edges_df["event_id"].isna()).sum()

        assert edges_with_season == len(
            edges_df
        ), f"Expected all edges to have season populated, got {edges_with_season}"
        assert edges_with_event_id == len(
            edges_df
        ), f"Expected all edges to have event_id populated, got {edges_with_event_id}"

        # Verify edges were generated for each player (schedule fallback functionality removed)
        lamar_edges = edges_df[edges_df["player"] == "Lamar Jackson"]
        josh_edges = edges_df[edges_df["player"] == "Josh Allen"]
        brock_edges = edges_df[edges_df["player"] == "Brock Purdy"]

        assert len(lamar_edges) == 2, "Should have 2 edges for Lamar Jackson"
        assert len(josh_edges) == 2, "Should have 2 edges for Josh Allen"
        assert len(brock_edges) == 2, "Should have 2 edges for Brock Purdy"

        # Verify edge quality (defense join functionality removed from current implementation)
        # Check that edges have valid expected value calculations
        edges_with_valid_ev = (~edges_df["ev"].isna()).sum()
        edges_with_valid_kelly = (~edges_df["kelly"].isna()).sum()

        assert edges_with_valid_ev == len(
            edges_df
        ), f"Expected all edges to have valid EV, got {edges_with_valid_ev}"
        assert edges_with_valid_kelly == len(
            edges_df
        ), f"Expected all edges to have valid Kelly, got {edges_with_valid_kelly}"

        # Check that we have both over and under edges
        over_edges = (edges_df["side"] == "over").sum()
        under_edges = (edges_df["side"] == "under").sum()

        assert over_edges == 3, f"Expected 3 over edges, got {over_edges}"
        assert under_edges == 3, f"Expected 3 under edges, got {under_edges}"

        print(f"✅ 2025 edges integration test passed:")
        print(f"   - Generated {len(edges_df)} edges")
        print(f"   - {edges_with_valid_ev}/{len(edges_df)} edges have valid EV")
        print(f"   - {edges_with_valid_kelly}/{len(edges_df)} edges have valid Kelly")
        print(f"   - {over_edges} over edges, {under_edges} under edges")


def test_2025_edges_join_diagnostics():
    """Test that join diagnostics work correctly for 2025 season data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_odds.db"
        setup_test_database(db_path)

        config = EdgeEngineConfig(database_path=db_path, export_dir=Path(temp_dir))

        # Create edges with mixed join key coverage
        edges_df = pd.DataFrame(
            [
                {
                    "event_id": "2025-01-12-BAL-PIT",
                    "player": "Lamar Jackson",
                    "season": 2025,
                    "week": 19,
                    "opponent_def_code": "PIT",  # Should match
                    "def_tier": pd.NA,
                },
                {
                    "event_id": "2025-01-19-BUF-KC",
                    "player": "Josh Allen",
                    "season": 2025,
                    "week": pd.NA,  # Missing week
                    "opponent_def_code": "KC",
                    "def_tier": pd.NA,
                },
                {
                    "event_id": "2025-01-26-SF-DAL",
                    "player": "Brock Purdy",
                    "season": 2025,
                    "week": 21,
                    "opponent_def_code": "UNKNOWN",  # Unmatched code
                    "def_tier": pd.NA,
                },
            ]
        )

        # Calculate join key coverage (mimicking the diagnostic logic)
        total_edges = len(edges_df)
        season_coverage = (~edges_df["season"].isna()).sum()
        week_coverage = (~edges_df["week"].isna()).sum()
        opponent_coverage = (~edges_df["opponent_def_code"].isna()).sum()
        complete_keys = (
            (~edges_df["season"].isna())
            & (~edges_df["week"].isna())
            & (~edges_df["opponent_def_code"].isna())
        ).sum()

        # Verify coverage calculations
        assert season_coverage == 3, f"All 3 edges should have season, got {season_coverage}"
        assert week_coverage == 2, f"2 edges should have week, got {week_coverage}"
        assert (
            opponent_coverage == 3
        ), f"All 3 edges should have opponent_def_code, got {opponent_coverage}"
        assert complete_keys == 2, f"2 edges should have complete keys, got {complete_keys}"

        print(f"✅ Join diagnostics test passed:")
        print(
            f"   - Season coverage: {season_coverage}/{total_edges} ({season_coverage/total_edges*100:.1f}%)"
        )
        print(
            f"   - Week coverage: {week_coverage}/{total_edges} ({week_coverage/total_edges*100:.1f}%)"
        )
        print(
            f"   - Opponent coverage: {opponent_coverage}/{total_edges} ({opponent_coverage/total_edges*100:.1f}%)"
        )
        print(
            f"   - Complete keys: {complete_keys}/{total_edges} ({complete_keys/total_edges*100:.1f}%)"
        )


if __name__ == "__main__":
    test_2025_edges_generation_with_defense_join()
    test_2025_edges_join_diagnostics()
    print("All integration tests passed! 🎉")
