# tests/test_week_populator.py
"""Comprehensive unit tests for week population functionality."""

from datetime import datetime

import pandas as pd
import pytest

from engine.week_populator import populate_week_from_schedule


class TestWeekPopulator:
    """Test suite for the week populator helper function."""

    def test_empty_dataframes(self):
        """Test handling of empty DataFrames."""
        lines = pd.DataFrame()
        schedule = pd.DataFrame()
        result = populate_week_from_schedule(lines, schedule)
        assert result.empty

        # Empty lines with populated schedule
        lines = pd.DataFrame()
        schedule = pd.DataFrame(
            {
                "season": [2025],
                "week": [1],
                "game_date": ["2025-09-07"],
                "home_code": ["KC"],
                "away_code": ["LV"],
            }
        )
        result = populate_week_from_schedule(lines, schedule)
        assert result.empty

    def test_missing_commence_time_column(self):
        """Test handling when commence_time column is missing."""
        lines = pd.DataFrame(
            {"event_id": ["KC-LV"], "player": ["Patrick Mahomes"], "season": [2025]}
        )
        schedule = pd.DataFrame(
            {
                "season": [2025],
                "week": [1],
                "game_date": ["2025-09-07"],
                "home_code": ["KC"],
                "away_code": ["LV"],
            }
        )

        result = populate_week_from_schedule(lines, schedule)
        # Should return original without week column since no date matching possible
        assert "week" not in result.columns or result["week"].isna().all()

    def test_exact_date_home_away_matching(self):
        """Test exact matching on (season, date, home_team, away_team)."""
        lines = pd.DataFrame(
            {
                "event_id": ["game1"],
                "commence_time": ["2025-09-07T20:00:00Z"],
                "home_team": ["KC"],
                "away_team": ["LV"],
                "season": [2025],
                "player": ["Patrick Mahomes"],
            }
        )
        schedule = pd.DataFrame(
            {
                "season": [2025],
                "week": [1],
                "game_date": ["2025-09-07"],
                "home_code": ["KC"],
                "away_code": ["LV"],
            }
        )

        result = populate_week_from_schedule(lines, schedule)
        assert result.iloc[0]["week"] == 1

    def test_team_normalization(self):
        """Test that team normalization works correctly."""
        lines = pd.DataFrame(
            {
                "event_id": ["game1"],
                "commence_time": ["2025-09-07T20:00:00Z"],
                "home_team": ["JAC"],  # Should normalize to JAX
                "away_team": ["LA"],  # Should normalize to LAR
                "season": [2025],
                "player": ["Trevor Lawrence"],
            }
        )
        schedule = pd.DataFrame(
            {
                "season": [2025],
                "week": [1],
                "game_date": ["2025-09-07"],
                "home_code": ["JAX"],  # Normalized form
                "away_code": ["LAR"],  # Normalized form
            }
        )

        result = populate_week_from_schedule(lines, schedule)
        assert result.iloc[0]["week"] == 1

    def test_event_id_fallback_matching(self):
        """Test fallback matching using event_id parsing."""
        lines = pd.DataFrame(
            {
                "event_id": ["2025-09-07-kc-lv"],
                "commence_time": ["2025-09-07T20:00:00Z"],
                "home_team": ["Unknown"],  # Won't match
                "away_team": ["Unknown"],  # Won't match
                "season": [2025],
                "player": ["Patrick Mahomes"],
            }
        )
        schedule = pd.DataFrame(
            {
                "season": [2025],
                "week": [1],
                "game_date": ["2025-09-07"],
                "home_code": ["KC"],  # Will match via event_id parsing
                "away_code": ["LV"],  # Will match via event_id parsing
            }
        )

        result = populate_week_from_schedule(lines, schedule)
        assert result.iloc[0]["week"] == 1

    def test_event_id_simple_format(self):
        """Test simple event_id format like 'KC-LV'."""
        lines = pd.DataFrame(
            {
                "event_id": ["KC-LV"],
                "commence_time": ["2025-09-07T20:00:00Z"],
                "home_team": ["Unknown"],  # Won't match, should fallback to event_id
                "away_team": ["Unknown"],  # Won't match, should fallback to event_id
                "season": [2025],
                "player": ["Patrick Mahomes"],
            }
        )
        schedule = pd.DataFrame(
            {
                "season": [2025],
                "week": [1],
                "game_date": ["2025-09-07"],
                "home_code": ["KC"],
                "away_code": ["LV"],
            }
        )

        result = populate_week_from_schedule(lines, schedule)
        assert result.iloc[0]["week"] == 1

    def test_no_matches_found(self):
        """Test case where no matches are found."""
        lines = pd.DataFrame(
            {
                "event_id": ["TB-GB"],
                "commence_time": ["2025-09-14T13:00:00Z"],
                "home_team": ["TB"],
                "away_team": ["GB"],
                "season": [2025],
                "player": ["Tom Brady"],
            }
        )
        schedule = pd.DataFrame(
            {
                "season": [2025],
                "week": [1],
                "game_date": ["2025-09-07"],
                "home_code": ["KC"],
                "away_code": ["LV"],
            }
        )

        result = populate_week_from_schedule(lines, schedule)
        assert pd.isna(result.iloc[0]["week"])

    def test_mixed_success_scenarios(self):
        """Test mix of successful and unsuccessful matches."""
        lines = pd.DataFrame(
            {
                "event_id": ["KC-LV", "TB-GB", "PIT-BAL"],
                "commence_time": [
                    "2025-09-07T20:00:00Z",
                    "2025-09-14T13:00:00Z",  # Won't match date
                    "2025-09-07T13:00:00Z",
                ],
                "home_team": ["KC", "TB", "PIT"],
                "away_team": ["LV", "GB", "BAL"],
                "season": [2025, 2025, 2025],
                "player": ["Mahomes", "Brady", "Wilson"],
            }
        )
        schedule = pd.DataFrame(
            {
                "season": [2025, 2025],
                "week": [1, 1],
                "game_date": ["2025-09-07", "2025-09-07"],
                "home_code": ["KC", "PIT"],
                "away_code": ["LV", "BAL"],
            }
        )

        result = populate_week_from_schedule(lines, schedule)
        assert result.iloc[0]["week"] == 1  # KC-LV match
        assert pd.isna(result.iloc[1]["week"])  # TB-GB no match
        assert result.iloc[2]["week"] == 1  # PIT-BAL match

    def test_season_default_handling(self):
        """Test that missing season defaults to 2025."""
        lines = pd.DataFrame(
            {
                "event_id": ["KC-LV"],
                "commence_time": ["2025-09-07T20:00:00Z"],
                "home_team": ["KC"],
                "away_team": ["LV"],
                # No season column
                "player": ["Patrick Mahomes"],
            }
        )
        schedule = pd.DataFrame(
            {
                "season": [2025],
                "week": [1],
                "game_date": ["2025-09-07"],
                "home_code": ["KC"],
                "away_code": ["LV"],
            }
        )

        result = populate_week_from_schedule(lines, schedule)
        assert result.iloc[0]["season"] == 2025
        assert result.iloc[0]["week"] == 1

    def test_nullable_integer_week_type(self):
        """Test that week column uses nullable Int64 type."""
        lines = pd.DataFrame(
            {
                "event_id": ["KC-LV", "NOMATCH"],
                "commence_time": ["2025-09-07T20:00:00Z", "2025-09-14T20:00:00Z"],
                "home_team": ["KC", "XX"],
                "away_team": ["LV", "YY"],
                "season": [2025, 2025],
            }
        )
        schedule = pd.DataFrame(
            {
                "season": [2025],
                "week": [1],
                "game_date": ["2025-09-07"],
                "home_code": ["KC"],
                "away_code": ["LV"],
            }
        )

        result = populate_week_from_schedule(lines, schedule)
        assert result["week"].dtype == "Int64"
        assert result.iloc[0]["week"] == 1
        assert pd.isna(result.iloc[1]["week"])

    def test_all_team_normalizations(self):
        """Test all team code normalizations."""
        normalizations = {
            "JAC": "JAX",
            "LA": "LAR",
            "WSH": "WAS",
            "OAK": "LV",
            "SD": "LAC",
            "STL": "LAR",
        }

        for old_code, new_code in normalizations.items():
            lines = pd.DataFrame(
                {
                    "event_id": ["game1"],
                    "commence_time": ["2025-09-07T20:00:00Z"],
                    "home_team": [old_code],
                    "away_team": ["KC"],
                    "season": [2025],
                }
            )
            schedule = pd.DataFrame(
                {
                    "season": [2025],
                    "week": [1],
                    "game_date": ["2025-09-07"],
                    "home_code": [new_code],
                    "away_code": ["KC"],
                }
            )

            result = populate_week_from_schedule(lines, schedule)
            assert result.iloc[0]["week"] == 1, f"Failed normalization {old_code} -> {new_code}"

    def test_cleanup_temporary_columns(self):
        """Test that temporary columns are cleaned up."""
        lines = pd.DataFrame(
            {
                "event_id": ["KC-LV"],
                "commence_time": ["2025-09-07T20:00:00Z"],
                "home_team": ["KC"],
                "away_team": ["LV"],
                "season": [2025],
            }
        )
        schedule = pd.DataFrame(
            {
                "season": [2025],
                "week": [1],
                "game_date": ["2025-09-07"],
                "home_code": ["KC"],
                "away_code": ["LV"],
            }
        )

        result = populate_week_from_schedule(lines, schedule)

        # Temporary columns should be cleaned up
        temp_cols = ["_gdate", "home_code", "away_code"]
        for col in temp_cols:
            assert col not in result.columns, f"Temporary column {col} should be cleaned up"
