"""Tests for team code normalization."""

from __future__ import annotations

import pandas as pd

from engine.team_map import normalize_team_code


def test_normalize_team_code_key_examples():
    """Test key normalization examples from the specification."""
    # JAX -> JAC (Jacksonville canonical)
    assert normalize_team_code("JAX") == "JAC"

    # WSH -> WAS (Washington canonical)
    assert normalize_team_code("WSH") == "WAS"

    # Legacy team relocations
    assert normalize_team_code("OAK") == "LV"  # Oakland -> Las Vegas
    assert normalize_team_code("SD") == "LAC"  # San Diego -> Los Angeles Chargers

    # LA -> LAR (when Rams)
    assert normalize_team_code("LA") == "LAR"


def test_normalize_team_code_edge_cases():
    """Test edge cases and input validation."""
    # Empty/None cases
    assert normalize_team_code("") == ""
    assert normalize_team_code("   ") == ""

    # Case insensitive
    assert normalize_team_code("jax") == "JAC"
    assert normalize_team_code("wsh") == "WAS"

    # Whitespace handling
    assert normalize_team_code("  JAX  ") == "JAC"

    # Unmapped codes pass through
    assert normalize_team_code("DAL") == "DAL"
    assert normalize_team_code("NE") == "NE"


def test_normalize_team_code_common_variations():
    """Test other common team code variations."""
    assert normalize_team_code("LVR") == "LV"  # Las Vegas variant
    assert normalize_team_code("KCC") == "KC"  # Kansas City variant
    assert normalize_team_code("TBB") == "TB"  # Tampa Bay variant
    assert normalize_team_code("NWE") == "NE"  # New England variant
    assert normalize_team_code("GNB") == "GB"  # Green Bay variant


def test_merge_scenario():
    """Test that two frames can join successfully after normalization."""
    # Simulate edges DataFrame with non-canonical team codes
    edges_df = pd.DataFrame(
        {
            "opponent_def_code": ["JAX", "WSH", "OAK", "DAL"],
            "season": [2023, 2023, 2023, 2023],
            "player": ["Player A", "Player B", "Player C", "Player D"],
        }
    )

    # Simulate defense_ratings DataFrame with canonical team codes
    defense_df = pd.DataFrame(
        {
            "defteam": ["JAC", "WAS", "LV", "DAL"],
            "season": [2023, 2023, 2023, 2023],
            "tier": ["Average", "Stingy", "Generous", "Average"],
            "score": [0.1, -0.3, 0.4, 0.0],
        }
    )

    # Apply normalization to edges
    edges_df["normalized_def_code"] = edges_df["opponent_def_code"].apply(normalize_team_code)

    # Merge should work now
    merged = edges_df.merge(
        defense_df,
        left_on=["normalized_def_code", "season"],
        right_on=["defteam", "season"],
        how="left",
    )

    # All rows should have matched
    assert len(merged) == 4
    assert merged["tier"].notna().all()
    assert merged["score"].notna().all()

    # Check specific mappings
    assert merged.loc[merged["opponent_def_code"] == "JAX", "defteam"].iloc[0] == "JAC"
    assert merged.loc[merged["opponent_def_code"] == "WSH", "defteam"].iloc[0] == "WAS"
    assert merged.loc[merged["opponent_def_code"] == "OAK", "defteam"].iloc[0] == "LV"
    assert merged.loc[merged["opponent_def_code"] == "DAL", "defteam"].iloc[0] == "DAL"
