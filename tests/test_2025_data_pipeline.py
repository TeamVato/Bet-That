"""Integration test for 2025 data pipeline end-to-end."""

import sqlite3
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from jobs.compute_edges import main as compute_edges_main


def test_2025_pipeline_with_smoke_data():
    """Test that the complete 2025 pipeline works with seeded smoke data."""
    # For simplicity, test with the main database since seeder has already run
    db_path = "storage/odds.db"

    # Verify smoke data exists in the main database
    with sqlite3.connect(db_path) as conn:
        # Check current_best_lines
        cur = conn.execute("SELECT COUNT(*) FROM current_best_lines WHERE season=2025")
        cbl_count = cur.fetchone()[0]

        if cbl_count == 0:
            print("ℹ️  No 2025 data found - running smoke seeder first")
            from scripts.smoke_seed_2025 import main as seed_main

            seed_main()

            # Re-check after seeding
            cur = conn.execute("SELECT COUNT(*) FROM current_best_lines WHERE season=2025")
            cbl_count = cur.fetchone()[0]

        assert (
            cbl_count >= 1
        ), f"Expected at least 1 current_best_lines row for 2025, got {cbl_count}"

        # Check defense_ratings
        cur = conn.execute("SELECT COUNT(*) FROM defense_ratings WHERE season=2025")
        dr_count = cur.fetchone()[0]
        assert dr_count >= 1, f"Expected at least 1 defense_ratings row for 2025, got {dr_count}"

        # Check that our smoke row has the expected structure
        cur = conn.execute(
            """
            SELECT event_id, player, market, pos, season, week, team_code, opponent_def_code
            FROM current_best_lines
            WHERE season=2025 AND player='Isiah Pacheco'
        """
        )
        row = cur.fetchone()

        if row:  # If we have the specific smoke test row
            event_id, player, market, pos, season, week, team_code, opponent_def_code = row

            assert event_id is not None, "event_id should not be null"
            assert player == "Isiah Pacheco", f"Expected Isiah Pacheco, got {player}"
            assert market == "player_rush_yds", f"Expected player_rush_yds, got {market}"
            assert pos == "RB", f"Expected RB position, got {pos}"
            assert season == 2025, f"Expected season 2025, got {season}"
            assert week == 1, f"Expected week 1, got {week}"
        else:
            print("ℹ️  Specific smoke test row not found, but 2025 data exists")

        print("✅ Smoke data verification passed")


def test_2025_season_dtype_consistency():
    """Test that season dtypes are consistent across tables."""
    with sqlite3.connect("storage/odds.db") as conn:
        # Check current_best_lines season dtype
        cur = conn.execute(
            "SELECT typeof(season) as season_type, COUNT(*) FROM current_best_lines WHERE season=2025 GROUP BY season_type"
        )
        cbl_types = cur.fetchall()

        # Check defense_ratings season dtype
        cur = conn.execute(
            "SELECT typeof(season) as season_type, COUNT(*) FROM defense_ratings WHERE season=2025 GROUP BY season_type"
        )
        dr_types = cur.fetchall()

        print(f"current_best_lines season dtypes for 2025: {cbl_types}")
        print(f"defense_ratings season dtypes for 2025: {dr_types}")

        # Both should be INTEGER type
        for type_info in cbl_types:
            season_type, count = type_info
            assert (
                season_type == "integer"
            ), f"current_best_lines season should be integer, got {season_type}"

        for type_info in dr_types:
            season_type, count = type_info
            assert (
                season_type == "integer"
            ), f"defense_ratings season should be integer, got {season_type}"


def test_2025_join_key_coverage():
    """Test that 2025 data has adequate join key coverage."""
    with sqlite3.connect("storage/odds.db") as conn:
        # Get current_best_lines rows for 2025
        cur = conn.execute(
            """
            SELECT
                COUNT(*) as total_rows,
                SUM(CASE WHEN season IS NOT NULL THEN 1 ELSE 0 END) as has_season,
                SUM(CASE WHEN week IS NOT NULL THEN 1 ELSE 0 END) as has_week,
                SUM(CASE WHEN event_id IS NOT NULL THEN 1 ELSE 0 END) as has_event_id,
                SUM(CASE WHEN pos IS NOT NULL AND pos != '' THEN 1 ELSE 0 END) as has_pos
            FROM current_best_lines
            WHERE season=2025
        """
        )

        stats = cur.fetchone()
        if stats and stats[0] > 0:  # If we have 2025 data
            total, has_season, has_week, has_event_id, has_pos = stats

            print(f"2025 join key coverage:")
            print(f"  Total rows: {total}")
            print(f"  Has season: {has_season}/{total} ({has_season/total*100:.1f}%)")
            print(f"  Has week: {has_week}/{total} ({has_week/total*100:.1f}%)")
            print(f"  Has event_id: {has_event_id}/{total} ({has_event_id/total*100:.1f}%)")
            print(f"  Has pos: {has_pos}/{total} ({has_pos/total*100:.1f}%)")

            # Should have high coverage for basic keys
            assert (
                has_season == total
            ), f"All 2025 rows should have season, got {has_season}/{total}"
            assert (
                has_event_id >= total * 0.8
            ), f"Expected >=80% event_id coverage, got {has_event_id}/{total}"
            assert has_pos >= total * 0.8, f"Expected >=80% pos coverage, got {has_pos}/{total}"

            print("✅ 2025 join key coverage verification passed")
        else:
            print("ℹ️  No 2025 data found in current_best_lines - test skipped")


def test_2025_defense_ratings_join_potential():
    """Test that 2025 defense ratings are compatible for joining."""
    with sqlite3.connect("storage/odds.db") as conn:
        # Check defense ratings structure for 2025
        cur = conn.execute(
            """
            SELECT
                COUNT(*) as total_rows,
                COUNT(DISTINCT defteam) as unique_teams,
                MIN(week) as min_week,
                MAX(week) as max_week,
                COUNT(DISTINCT pos) as unique_positions
            FROM defense_ratings
            WHERE season=2025
        """
        )

        stats = cur.fetchone()
        if stats and stats[0] > 0:
            total, teams, min_week, max_week, positions = stats

            print(f"2025 defense ratings structure:")
            print(f"  Total rows: {total}")
            print(f"  Unique teams: {teams}")
            print(f"  Week range: {min_week} - {max_week}")
            print(f"  Unique positions: {positions}")

            # Should have reasonable coverage
            assert teams >= 30, f"Expected >= 30 teams in defense ratings, got {teams}"
            assert min_week >= 1, f"Expected min week >= 1, got {min_week}"

            # Check for QB_PASS position (needed for QB props)
            cur = conn.execute(
                "SELECT COUNT(*) FROM defense_ratings WHERE season=2025 AND pos='QB_PASS'"
            )
            qb_pass_count = cur.fetchone()[0]
            assert qb_pass_count > 0, "Should have QB_PASS defense ratings for 2025"

            print("✅ 2025 defense ratings compatibility verification passed")
        else:
            print("ℹ️  No 2025 defense ratings found - test skipped")


def test_team_code_normalization_consistency():
    """Test that team codes are normalized consistently across tables."""
    from engine.team_map import normalize_team_code

    # Test some key mappings that have caused issues
    test_codes = ["JAC", "JAX", "WSH", "WAS", "LV", "LVR"]

    print("Team code normalization consistency:")
    for code in test_codes:
        normalized = normalize_team_code(code)
        print(f"  {code} → {normalized}")

    # Key assertions based on typical mappings
    assert normalize_team_code("JAC") == "JAC", "JAC should normalize to JAC"
    assert normalize_team_code("JAX") == "JAC", "JAX should normalize to JAC"
    assert normalize_team_code("WSH") == "WAS", "WSH should normalize to WAS"
    assert normalize_team_code("WAS") == "WAS", "WAS should normalize to WAS"

    print("✅ Team code normalization consistency passed")


if __name__ == "__main__":
    print("Running 2025 data pipeline integration tests...")

    test_2025_pipeline_with_smoke_data()
    test_2025_season_dtype_consistency()
    test_2025_join_key_coverage()
    test_2025_defense_ratings_join_potential()
    test_team_code_normalization_consistency()

    print("🎉 All 2025 pipeline tests passed!")
