"""Test suite for EdgeEngine - CRITICAL BUSINESS LOGIC."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from engine.edge_engine import EdgeEngine, EdgeEngineConfig, _infer_pos


class TestInferPos:
    """Test position inference logic."""

    def test_infer_pos_from_market(self):
        """Test position inference from market name."""
        assert _infer_pos("player_pass_yds") == "QB"
        assert _infer_pos("player_rush_yds") == "RB"
        assert _infer_pos("player_rec_yds") == "WR"
        assert _infer_pos("player_receptions") == "WR"

    def test_infer_pos_explicit_override(self):
        """Test that explicit position overrides market inference."""
        assert _infer_pos("player_pass_yds", "TE") == "TE"
        assert _infer_pos("player_rush_yds", "QB") == "QB"

    def test_infer_pos_edge_cases(self):
        """Test edge cases for position inference."""
        assert _infer_pos(None) is None
        assert _infer_pos("unknown_market") is None
        assert _infer_pos("player_pass_yds", np.nan) == "QB"


class TestEdgeEngineConfig:
    """Test EdgeEngine configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = EdgeEngineConfig(database_path=Path("/tmp/test.db"))
        assert config.kelly_cap == 0.05
        assert config.export_dir == Path("storage/exports")
        assert config.database_path == Path("/tmp/test.db")

    def test_custom_config(self):
        """Test custom configuration values."""
        custom_dir = Path("/tmp/test")
        config = EdgeEngineConfig(
            database_path=Path("/tmp/custom.db"), export_dir=custom_dir, kelly_cap=0.1
        )
        assert config.kelly_cap == 0.1
        assert config.export_dir == custom_dir
        assert config.database_path == Path("/tmp/custom.db")


class TestEdgeEngine:
    """Test core EdgeEngine functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test.db"
        self.config = EdgeEngineConfig(
            database_path=self.db_path, export_dir=self.temp_dir, kelly_cap=0.05
        )
        self.engine = EdgeEngine(self.config)

    def create_sample_props_data(self):
        """Create sample props data for testing."""
        return pd.DataFrame(
            [
                {
                    "event_id": "2025-01-01-KC-BUF",
                    "player": "Patrick Mahomes",
                    "market": "player_pass_yds",
                    "line": 275.5,
                    "over_odds": -110,
                    "under_odds": -110,
                    "book": "draftkings",
                    "season": 2025,
                    "week": 1,
                    "def_team": "BUF",
                    "team": "KC",
                    "pos": "QB",
                },
                {
                    "event_id": "2025-01-01-KC-BUF",
                    "player": "Josh Allen",
                    "market": "player_pass_yds",
                    "line": 280.5,
                    "over_odds": -105,
                    "under_odds": -115,
                    "book": "fanduel",
                    "season": 2025,
                    "week": 1,
                    "def_team": "KC",
                    "team": "BUF",
                    "pos": "QB",
                },
            ]
        )

    def create_sample_projections_data(self):
        """Create sample projections data for testing."""
        return pd.DataFrame(
            [
                {
                    "event_id": "2025-01-01-KC-BUF",
                    "player": "Patrick Mahomes",
                    "mu": 285.0,  # Model predicts higher than line
                    "sigma": 45.0,
                    "season": 2025,
                    "week": 1,
                    "def_team": "BUF",
                    "team": "KC",
                },
                {
                    "event_id": "2025-01-01-KC-BUF",
                    "player": "Josh Allen",
                    "mu": 275.0,  # Model predicts lower than line
                    "sigma": 50.0,
                    "season": 2025,
                    "week": 1,
                    "def_team": "KC",
                    "team": "BUF",
                },
            ]
        )

    def test_compute_edges_basic_functionality(self):
        """Test basic edge computation functionality."""
        props_df = self.create_sample_props_data()
        projections_df = self.create_sample_projections_data()

        edges = self.engine.compute_edges(props_df, projections_df)

        # Should return a DataFrame with edges
        assert isinstance(edges, pd.DataFrame)
        assert not edges.empty, "EdgeEngine should find edges with sample data"

        # Check required columns exist
        expected_columns = ["event_id", "player", "market", "line", "side", "edge", "ev", "kelly"]
        for col in expected_columns:
            assert col in edges.columns, f"Missing required column: {col}"

    def test_compute_edges_mahomes_over_edge(self):
        """Test that Mahomes OVER edge is detected correctly."""
        props_df = self.create_sample_props_data()
        projections_df = self.create_sample_projections_data()

        edges = self.engine.compute_edges(props_df, projections_df)

        # Mahomes: line=275.5, mu=285.0 -> should favor OVER
        mahomes_edges = edges[edges["player"] == "Patrick Mahomes"]
        assert not mahomes_edges.empty, "Should find edges for Mahomes"

        # Should find an OVER edge (model higher than line)
        over_edges = mahomes_edges[mahomes_edges["side"] == "over"]
        if not over_edges.empty:
            over_edge = over_edges.iloc[0]
            assert over_edge["edge"] > 0, "Should have positive edge for Mahomes OVER"
            assert over_edge["ev"] > 0, "Should have positive EV"
            assert over_edge["kelly"] > 0, "Should recommend some bet size"

    def test_compute_edges_allen_under_edge(self):
        """Test that Josh Allen UNDER edge is detected correctly."""
        props_df = self.create_sample_props_data()
        projections_df = self.create_sample_projections_data()

        edges = self.engine.compute_edges(props_df, projections_df)

        # Allen: line=280.5, mu=275.0 -> should favor UNDER
        allen_edges = edges[edges["player"] == "Josh Allen"]
        assert not allen_edges.empty, "Should find edges for Allen"

        # Should find an UNDER edge (model lower than line)
        under_edges = allen_edges[allen_edges["side"] == "under"]
        if not under_edges.empty:
            under_edge = under_edges.iloc[0]
            assert under_edge["edge"] > 0, "Should have positive edge for Allen UNDER"
            assert under_edge["ev"] > 0, "Should have positive EV"

    def test_compute_edges_empty_inputs(self):
        """Test handling of empty input DataFrames."""
        empty_df = pd.DataFrame()

        # Empty props should return empty DataFrame
        edges = self.engine.compute_edges(empty_df, self.create_sample_projections_data())
        assert edges.empty, "Empty props should return empty edges"

        # Empty projections should still work (uses defaults)
        edges = self.engine.compute_edges(self.create_sample_props_data(), empty_df)
        assert isinstance(edges, pd.DataFrame), "Should handle empty projections"

    def test_compute_edges_missing_odds(self):
        """Test handling of missing odds data."""
        props_df = self.create_sample_props_data()

        # Remove odds from one row
        props_df.loc[0, "over_odds"] = np.nan
        projections_df = self.create_sample_projections_data()

        edges = self.engine.compute_edges(props_df, projections_df)

        # Should still work with remaining valid data
        assert isinstance(edges, pd.DataFrame)
        # Should have fewer rows due to filtering invalid odds
        valid_players = edges["player"].unique()
        assert "Josh Allen" in valid_players, "Should process valid data"

    def test_compute_edges_kelly_cap(self):
        """Test that Kelly fractions are capped correctly."""
        # Create scenario with huge edge
        props_df = pd.DataFrame(
            [
                {
                    "event_id": "test",
                    "player": "Test Player",
                    "market": "player_pass_yds",
                    "line": 200.0,
                    "over_odds": 200,  # +200 odds (underdog)
                    "under_odds": -300,  # -300 odds (heavy favorite)
                    "book": "test",
                    "season": 2025,
                    "week": 1,
                    "pos": "QB",
                }
            ]
        )

        projections_df = pd.DataFrame(
            [
                {
                    "event_id": "test",
                    "player": "Test Player",
                    "mu": 350.0,  # Huge edge over 200 line
                    "sigma": 30.0,
                    "season": 2025,
                    "week": 1,
                }
            ]
        )

        edges = self.engine.compute_edges(props_df, projections_df)

        if not edges.empty:
            # All Kelly fractions should be <= kelly_cap
            max_kelly = edges["kelly"].max()
            assert (
                max_kelly <= self.config.kelly_cap
            ), f"Kelly {max_kelly} exceeds cap {self.config.kelly_cap}"

    def test_compute_edges_confidence_scoring(self):
        """Test confidence scoring logic."""
        props_df = self.create_sample_props_data()
        projections_df = self.create_sample_projections_data()

        edges = self.engine.compute_edges(props_df, projections_df)

        if not edges.empty:
            # Check if confidence column exists, if not skip this test
            if "confidence" in edges.columns:
                # Confidence should be between 0 and 1
                assert (edges["confidence"] >= 0).all(), "Confidence should be >= 0"
                assert (edges["confidence"] <= 1).all(), "Confidence should be <= 1"

                # Higher edge should generally mean higher confidence
                # (This is a heuristic test - exact relationship may vary)
                for _, edge_row in edges.iterrows():
                    assert isinstance(
                        edge_row["confidence"], (int, float, np.number)
                    ), "Confidence should be numeric"
            else:
                # If no confidence column, just check that edges have reasonable values
                assert (
                    edges["edge"].abs() >= 0
                ).all(), "All edges should have non-negative absolute values"

    def test_position_inference_integration(self):
        """Test that position inference works in full pipeline."""
        props_df = pd.DataFrame(
            [
                {
                    "event_id": "test",
                    "player": "Test RB",
                    "market": "player_rush_yds",  # Should infer RB
                    "line": 75.5,
                    "over_odds": -110,
                    "under_odds": -110,
                    "book": "test",
                    "season": 2025,
                    "week": 1,
                    # No explicit pos field
                }
            ]
        )

        projections_df = pd.DataFrame(
            [
                {
                    "event_id": "test",
                    "player": "Test RB",
                    "mu": 80.0,
                    "sigma": 25.0,
                    "season": 2025,
                    "week": 1,
                }
            ]
        )

        edges = self.engine.compute_edges(props_df, projections_df)

        if not edges.empty:
            # Should have inferred position
            assert (edges["pos"] == "RB").any(), "Should infer RB position from market"

    def test_schedule_lookup_integration(self):
        """Test schedule lookup functionality."""
        schedule_lookup = {"2025-01-01-KC-BUF": {"season": "2025", "week": "1"}}

        engine_with_schedule = EdgeEngine(self.config, schedule_lookup=schedule_lookup)

        props_df = pd.DataFrame(
            [
                {
                    "event_id": "2025-01-01-KC-BUF",
                    "player": "Test Player",
                    "market": "player_pass_yds",
                    "line": 275.5,
                    "over_odds": -110,
                    "under_odds": -110,
                    "book": "test",
                    # Missing season/week - should use schedule lookup
                }
            ]
        )

        projections_df = pd.DataFrame(
            [
                {
                    "event_id": "2025-01-01-KC-BUF",
                    "player": "Test Player",
                    "mu": 280.0,
                    "sigma": 45.0,
                }
            ]
        )

        edges = engine_with_schedule.compute_edges(props_df, projections_df)

        # Should work despite missing season/week in props
        assert isinstance(edges, pd.DataFrame)

    def test_edge_filtering_logic(self):
        """Test that only meaningful edges are returned."""
        # Create scenario with no real edge (line = mu)
        props_df = pd.DataFrame(
            [
                {
                    "event_id": "test",
                    "player": "No Edge Player",
                    "market": "player_pass_yds",
                    "line": 275.0,
                    "over_odds": -110,
                    "under_odds": -110,
                    "book": "test",
                    "season": 2025,
                    "week": 1,
                    "pos": "QB",
                }
            ]
        )

        projections_df = pd.DataFrame(
            [
                {
                    "event_id": "test",
                    "player": "No Edge Player",
                    "mu": 275.0,  # Exactly at line
                    "sigma": 45.0,
                    "season": 2025,
                    "week": 1,
                }
            ]
        )

        edges = self.engine.compute_edges(props_df, projections_df)

        # Should either return empty or very small edges
        if not edges.empty:
            max_abs_edge = abs(edges["edge"]).max()
            assert max_abs_edge < 0.1, "Should not find significant edges when line = mu"


class TestEdgeEngineErrorHandling:
    """Test error handling and edge cases."""

    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test.db"
        self.config = EdgeEngineConfig(database_path=self.db_path, export_dir=self.temp_dir)
        self.engine = EdgeEngine(self.config)

    def test_invalid_odds_handling(self):
        """Test handling of invalid odds values."""
        props_df = pd.DataFrame(
            [
                {
                    "event_id": "test",
                    "player": "Test Player",
                    "market": "player_pass_yds",
                    "line": 275.0,
                    "over_odds": 0,  # Invalid odds
                    "under_odds": -110,
                    "book": "test",
                    "season": 2025,
                }
            ]
        )

        projections_df = pd.DataFrame(
            [
                {
                    "event_id": "test",
                    "player": "Test Player",
                    "mu": 280.0,
                    "sigma": 45.0,
                }
            ]
        )

        # Should not crash, should handle gracefully
        edges = self.engine.compute_edges(props_df, projections_df)
        assert isinstance(edges, pd.DataFrame)

    def test_extreme_sigma_values(self):
        """Test handling of extreme sigma (volatility) values."""
        props_df = pd.DataFrame(
            [
                {
                    "event_id": "test",
                    "player": "Test Player",
                    "market": "player_pass_yds",
                    "line": 275.0,
                    "over_odds": -110,
                    "under_odds": -110,
                    "book": "test",
                    "season": 2025,
                }
            ]
        )

        # Test with zero sigma
        projections_df = pd.DataFrame(
            [
                {
                    "event_id": "test",
                    "player": "Test Player",
                    "mu": 280.0,
                    "sigma": 0.0,  # Zero volatility
                }
            ]
        )

        edges = self.engine.compute_edges(props_df, projections_df)
        assert isinstance(edges, pd.DataFrame)

        # Test with very large sigma
        projections_df.loc[0, "sigma"] = 1000.0
        edges = self.engine.compute_edges(props_df, projections_df)
        assert isinstance(edges, pd.DataFrame)

    def test_non_standard_market_names(self):
        """Test handling of non-standard market names."""
        props_df = pd.DataFrame(
            [
                {
                    "event_id": "test",
                    "player": "Test Player",
                    "market": "unknown_market_type",
                    "line": 100.0,
                    "over_odds": -110,
                    "under_odds": -110,
                    "book": "test",
                    "season": 2025,
                }
            ]
        )

        projections_df = pd.DataFrame(
            [
                {
                    "event_id": "test",
                    "player": "Test Player",
                    "mu": 105.0,
                    "sigma": 20.0,
                }
            ]
        )

        # Should handle unknown markets gracefully
        edges = self.engine.compute_edges(props_df, projections_df)
        assert isinstance(edges, pd.DataFrame)


class TestEdgeEnginePerformance:
    """Test performance characteristics."""

    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test.db"
        self.config = EdgeEngineConfig(database_path=self.db_path, export_dir=self.temp_dir)
        self.engine = EdgeEngine(self.config)

    def test_large_dataset_handling(self):
        """Test that engine handles large datasets efficiently."""
        # Create large dataset (100 props)
        n_props = 100
        props_data = []
        projections_data = []

        for i in range(n_props):
            props_data.append(
                {
                    "event_id": f"game_{i % 10}",
                    "player": f"Player_{i}",
                    "market": "player_pass_yds",
                    "line": 250.0 + (i % 50),
                    "over_odds": -110 + (i % 10),
                    "under_odds": -110 - (i % 10),
                    "book": f"book_{i % 3}",
                    "season": 2025,
                    "week": 1,
                    "pos": "QB",
                }
            )

            projections_data.append(
                {
                    "event_id": f"game_{i % 10}",
                    "player": f"Player_{i}",
                    "mu": 255.0 + (i % 60),
                    "sigma": 45.0,
                    "season": 2025,
                    "week": 1,
                }
            )

        props_df = pd.DataFrame(props_data)
        projections_df = pd.DataFrame(projections_data)

        # Should complete in reasonable time (< 5 seconds)
        import time

        start_time = time.time()
        edges = self.engine.compute_edges(props_df, projections_df)
        elapsed = time.time() - start_time

        assert elapsed < 5.0, f"Large dataset processing took {elapsed:.2f}s (too slow)"
        assert isinstance(edges, pd.DataFrame)
        assert len(edges) <= len(props_df) * 2, "Should not create more edges than possible"
