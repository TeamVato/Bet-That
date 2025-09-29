# engine/week_populator.py
"""Production-ready week population from schedule data with team normalization and validation."""
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import pandas as pd

# Comprehensive team normalization mapping
_TEAM_NORM = {
    "JAC": "JAX",
    "JAGUARS": "JAX",
    "JACKSONVILLE": "JAX",
    "LA": "LAR",
    "RAMS": "LAR",
    "LOS ANGELES RAMS": "LAR",
    "STL": "LAR",
    "ST. LOUIS": "LAR",
    "WSH": "WAS",
    "WASHINGTON": "WAS",
    "COMMANDERS": "WAS",
    "REDSKINS": "WAS",
    "WASHINGTON FOOTBALL TEAM": "WAS",
    "OAK": "LV",
    "OAKLAND": "LV",
    "RAIDERS": "LV",
    "LAS VEGAS": "LV",
    "LV": "LV",
    "SD": "LAC",
    "SAN DIEGO": "LAC",
    "CHARGERS": "LAC",
    "LOS ANGELES CHARGERS": "LAC",
    "LAC": "LAC",
    # Standard abbreviations for validation
    "ARI": "ARI",
    "ATL": "ATL",
    "BAL": "BAL",
    "BUF": "BUF",
    "CAR": "CAR",
    "CHI": "CHI",
    "CIN": "CIN",
    "CLE": "CLE",
    "DAL": "DAL",
    "DEN": "DEN",
    "DET": "DET",
    "GB": "GB",
    "HOU": "HOU",
    "IND": "IND",
    "JAX": "JAX",
    "KC": "KC",
    "LAR": "LAR",
    "LAC": "LAC",
    "LV": "LV",
    "MIA": "MIA",
    "MIN": "MIN",
    "NE": "NE",
    "NO": "NO",
    "NYG": "NYG",
    "NYJ": "NYJ",
    "PHI": "PHI",
    "PIT": "PIT",
    "SF": "SF",
    "SEA": "SEA",
    "TB": "TB",
    "TEN": "TEN",
    "WAS": "WAS",
}


def normalize_team_code(team: Union[str, None]) -> str:
    """Normalize team codes to canonical 2-3 letter abbreviations."""
    if not team:
        return ""

    team_upper = str(team).upper().strip()
    return _TEAM_NORM.get(team_upper, team_upper)


def validate_team_codes(df: pd.DataFrame, team_columns: list[str]) -> Dict[str, list]:
    """Validate team codes in DataFrame columns and report issues."""
    issues = {"unknown_teams": [], "missing_teams": []}

    valid_teams = set(_TEAM_NORM.values())

    for col in team_columns:
        if col not in df.columns:
            continue

        # Check for missing values
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            issues["missing_teams"].append(f"{col}: {missing_count} missing values")

        # Check for unknown team codes
        unique_teams = df[col].dropna().unique()
        for team in unique_teams:
            normalized = normalize_team_code(team)
            if normalized and normalized not in valid_teams:
                issues["unknown_teams"].append(f"{col}: '{team}' -> '{normalized}'")

    return issues


def populate_week_from_schedule(
    lines: pd.DataFrame,
    schedule: pd.DataFrame,
    validate_teams: bool = True,
    logger: Optional[logging.Logger] = None,
) -> pd.DataFrame:
    """Populate week column in lines DataFrame using deterministic schedule matching.

    Uses multi-stage matching with comprehensive team normalization:
    1. Stage 1: Exact match on (season, date, home_team, away_team)
    2. Stage 2: Home/away swap fallback
    3. Stage 3: Team normalization and retry

    Args:
        lines: DataFrame with commence_time, home_team, away_team, season columns
        schedule: DataFrame with season, week, game_date, home_team, away_team columns
        validate_teams: Whether to validate and report team code issues
        logger: Optional logger for detailed diagnostics

    Returns:
        lines DataFrame with week column populated, includes match statistics
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    if lines.empty:
        logger.warning("Lines DataFrame is empty")
        return lines

    if schedule.empty:
        logger.warning("Schedule DataFrame is empty")
        return lines

    out = lines.copy()
    stage1_count = 0
    stage2_count = 0
    stage3_count = 0

    logger.info(f"Starting week population for {len(out)} rows")

    # Ensure season column exists
    if "season" not in out.columns:
        out["season"] = 2025

    # Validate required columns
    required_lines_cols = ["commence_time"]
    required_schedule_cols = ["season", "week", "game_date", "home_team", "away_team"]

    missing_lines_cols = [col for col in required_lines_cols if col not in out.columns]
    missing_schedule_cols = [col for col in required_schedule_cols if col not in schedule.columns]

    if missing_lines_cols:
        logger.error(f"Lines missing required columns: {missing_lines_cols}")
        return out

    if missing_schedule_cols:
        logger.error(f"Schedule missing required columns: {missing_schedule_cols}")
        return out

    # Team validation if requested
    if validate_teams:
        team_issues = validate_team_codes(out, ["home_team", "away_team"])
        if team_issues["unknown_teams"]:
            logger.warning(f"Unknown team codes in lines: {team_issues['unknown_teams'][:5]}")

        schedule_issues = validate_team_codes(schedule, ["home_team", "away_team"])
        if schedule_issues["unknown_teams"]:
            logger.warning(
                f"Unknown team codes in schedule: {schedule_issues['unknown_teams'][:5]}"
            )

    # Convert commence_time to UTC date for matching
    try:
        out["_gdate"] = pd.to_datetime(out["commence_time"], utc=True).dt.date
    except Exception as e:
        logger.error(f"Failed to parse commence_time: {e}")
        return out

    # Prepare schedule DataFrame with UTC dates
    schedule = schedule.copy()
    try:
        schedule["_gdate"] = pd.to_datetime(schedule["game_date"], utc=True).dt.date
    except Exception as e:
        logger.error(f"Failed to parse schedule game_date: {e}")
        return out

    # Normalize team codes in both DataFrames
    for col in ["home_team", "away_team"]:
        if col in out.columns:
            out[f"{col}_norm"] = out[col].apply(normalize_team_code)
        if col in schedule.columns:
            schedule[f"{col}_norm"] = schedule[col].apply(normalize_team_code)

    # Handle case where week column doesn't exist yet
    if "week" not in out.columns:
        out["week"] = pd.NA

    # Stage 1: Exact match on (season, date, home_team, away_team)
    logger.debug("Stage 1: Exact team name matching")

    stage1_result = out.merge(
        schedule[["season", "week", "_gdate", "home_team", "away_team"]],
        on=["season", "_gdate", "home_team", "away_team"],
        how="left",
        suffixes=("", "_sched"),
    )

    # Update week from stage1 matches
    stage1_matches = stage1_result["week_sched"].notna()
    out.loc[stage1_matches, "week"] = stage1_result.loc[stage1_matches, "week_sched"]
    stage1_count = stage1_matches.sum()
    logger.info(f"Stage 1 matched {stage1_count} rows")

    # Stage 2: Home/away swap fallback for remaining unmatched rows
    still_needs_week = out["week"].isna()
    if still_needs_week.any():
        logger.debug(
            f"Stage 2: Home/away swap matching for {still_needs_week.sum()} remaining rows"
        )

        stage2_subset = out.loc[still_needs_week].copy()

        stage2_result = stage2_subset.merge(
            schedule[["season", "week", "_gdate", "home_team", "away_team"]],
            left_on=["season", "_gdate", "away_team", "home_team"],  # Swap home/away
            right_on=["season", "_gdate", "home_team", "away_team"],
            how="left",
            suffixes=("", "_sched"),
        )

        stage2_matches = stage2_result["week_sched"].notna()
        if stage2_matches.any():
            # Get indices in original dataframe
            stage2_indices = still_needs_week[still_needs_week].index[stage2_matches]
            out.loc[stage2_indices, "week"] = stage2_result.loc[stage2_matches, "week_sched"]
            stage2_count = stage2_matches.sum()
            logger.info(f"Stage 2 matched {stage2_count} additional rows")

    # Stage 3: Normalized team code matching for remaining unmatched rows
    still_needs_week = out["week"].isna()
    if still_needs_week.any():
        logger.debug(
            f"Stage 3: Normalized team matching for {still_needs_week.sum()} remaining rows"
        )

        stage3_subset = out.loc[still_needs_week].copy()

        # Try normalized team matching
        stage3_result = stage3_subset.merge(
            schedule[["season", "week", "_gdate", "home_team_norm", "away_team_norm"]],
            left_on=["season", "_gdate", "home_team_norm", "away_team_norm"],
            right_on=["season", "_gdate", "home_team_norm", "away_team_norm"],
            how="left",
            suffixes=("", "_sched"),
        )

        stage3_matches = stage3_result["week_sched"].notna()
        if stage3_matches.any():
            stage3_indices = still_needs_week[still_needs_week].index[stage3_matches]
            out.loc[stage3_indices, "week"] = stage3_result.loc[stage3_matches, "week_sched"]
            stage3_count = stage3_matches.sum()
            logger.info(f"Stage 3 matched {stage3_count} additional rows")

    # Clean up temporary columns
    temp_cols = ["_gdate", "home_team_norm", "away_team_norm"]
    out.drop(columns=temp_cols, errors="ignore", inplace=True)

    # Convert week to nullable integer type
    if "week" in out.columns:
        out["week"] = out["week"].astype("Int64")

    # Final statistics and logging
    total_filled = int(stage1_count + stage2_count + stage3_count)
    total_rows = len(out)
    success_rate = (total_filled / total_rows * 100) if total_rows > 0 else 0

    logger.info(
        f"Week population completed: {total_filled}/{total_rows} rows ({success_rate:.1f}%) - "
        f"Stage1: {stage1_count}, Stage2: {stage2_count}, Stage3: {stage3_count}"
    )

    # Store detailed match counts for logging (attach as metadata)
    out._week_population_stats = {
        "stage1_count": int(stage1_count),
        "stage2_count": int(stage2_count),
        "stage3_count": int(stage3_count),
        "total_filled": total_filled,
        "total_rows": total_rows,
        "success_rate": round(success_rate, 2),
    }

    return out


def load_schedule_data(schedule_path: Union[str, Path]) -> pd.DataFrame:
    """Load and validate schedule data from CSV file."""
    logger = logging.getLogger(__name__)
    schedule_path = Path(schedule_path)

    if not schedule_path.exists():
        logger.error(f"Schedule file not found: {schedule_path}")
        return pd.DataFrame()

    try:
        schedule = pd.read_csv(schedule_path)

        # Validate required columns
        required_cols = ["season", "week", "game_date", "home_team", "away_team"]
        missing_cols = [col for col in required_cols if col not in schedule.columns]

        if missing_cols:
            logger.error(f"Schedule missing required columns: {missing_cols}")
            return pd.DataFrame()

        # Basic data validation
        if schedule.empty:
            logger.warning("Schedule file is empty")
            return schedule

        # Validate data types and ranges
        schedule["season"] = pd.to_numeric(schedule["season"], errors="coerce")
        schedule["week"] = pd.to_numeric(schedule["week"], errors="coerce")

        # Filter out invalid data
        valid_mask = (
            schedule["season"].between(2020, 2030, inclusive="both")
            & schedule["week"].between(1, 22, inclusive="both")
            & schedule["game_date"].notna()
            & schedule["home_team"].notna()
            & schedule["away_team"].notna()
        )

        invalid_rows = (~valid_mask).sum()
        if invalid_rows > 0:
            logger.warning(f"Filtered out {invalid_rows} invalid schedule rows")

        schedule = schedule[valid_mask]

        logger.info(f"Loaded {len(schedule)} valid schedule rows from {schedule_path}")
        return schedule

    except Exception as e:
        logger.error(f"Failed to load schedule data: {e}")
        return pd.DataFrame()


def ensure_week_populated(
    df: pd.DataFrame,
    schedule_path: Optional[Union[str, Path]] = None,
    default_schedule_paths: Optional[list[str]] = None,
) -> pd.DataFrame:
    """Ensure DataFrame has week column populated, with fallback schedule loading.

    Args:
        df: DataFrame to populate weeks for
        schedule_path: Explicit schedule file path
        default_schedule_paths: List of default paths to try if schedule_path not provided

    Returns:
        DataFrame with week column populated where possible
    """
    logger = logging.getLogger(__name__)

    if df.empty:
        return df

    # If week column already mostly populated, skip
    if "week" in df.columns:
        missing_weeks = df["week"].isna().sum()
        if missing_weeks == 0:
            logger.debug("Week column already fully populated")
            return df
        elif missing_weeks / len(df) < 0.1:  # Less than 10% missing
            logger.info(f"Week column mostly populated ({missing_weeks}/{len(df)} missing)")

    # Determine schedule file to use
    schedule_paths_to_try = []

    if schedule_path:
        schedule_paths_to_try.append(schedule_path)

    if default_schedule_paths:
        schedule_paths_to_try.extend(default_schedule_paths)

    # Default fallback paths
    schedule_paths_to_try.extend(
        [
            "tests/fixtures/schedule_2025_mini.csv",
            "storage/imports/nflverse_schedules_cache.csv",
            "data/schedules.csv",
            "schedules.csv",
        ]
    )

    # Try each schedule path until one works
    for path in schedule_paths_to_try:
        schedule = load_schedule_data(path)
        if not schedule.empty:
            logger.info(f"Using schedule data from {path}")
            return populate_week_from_schedule(df, schedule)

    logger.warning("No valid schedule data found - week population skipped")
    return df
