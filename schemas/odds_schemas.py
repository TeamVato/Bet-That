"""Pandera schemas for odds data validation and quality assurance."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import pandas as pd
import pandera as pa
from pandera import Field, Check
from pandera.typing import DataFrame, Series


class OddsSnapshotSchema(pa.DataFrameModel):
    """Schema for raw odds snapshots from The Odds API."""

    fetched_at: Series[str] = Field(
        description="UTC timestamp when data was fetched",
        checks=[
            Check.str_matches(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"),
            Check(lambda s: pd.to_datetime(s, errors='coerce').notna().all(),
                  error="Invalid ISO datetime format")
        ]
    )

    sport_key: Series[str] = Field(
        description="Sport identifier (e.g., 'americanfootball_nfl')",
        checks=[Check.str_length(min_val=3, max_val=50)]
    )

    event_id: Series[str] = Field(
        description="Unique event identifier",
        checks=[
            Check.str_length(min_val=5, max_val=100),
            Check(lambda s: s.notna().all(), error="Event ID cannot be null")
        ]
    )

    commence_time: Optional[Series[str]] = Field(
        description="Game start time in ISO format",
        nullable=True,
        checks=[
            Check(lambda s: s.isna() | pd.to_datetime(s, errors='coerce').notna(),
                  error="Invalid commence_time format")
        ]
    )

    home_team: Optional[Series[str]] = Field(
        description="Home team name",
        nullable=True,
        checks=[Check.str_length(max_val=50)]
    )

    away_team: Optional[Series[str]] = Field(
        description="Away team name",
        nullable=True,
        checks=[Check.str_length(max_val=50)]
    )

    bookmaker_key: Series[str] = Field(
        description="Bookmaker identifier",
        checks=[
            Check.str_length(min_val=2, max_val=50),
            Check(lambda s: s.notna().all(), error="Bookmaker key cannot be null")
        ]
    )

    market_key: Series[str] = Field(
        description="Market type identifier",
        checks=[
            Check.str_length(min_val=2, max_val=50),
            Check.isin(['h2h', 'spreads', 'totals', 'outrights', 'player_props']),
            Check(lambda s: s.notna().all(), error="Market key cannot be null")
        ]
    )

    outcome: Series[str] = Field(
        description="Bet outcome name",
        checks=[
            Check.str_length(min_val=1, max_val=100),
            Check(lambda s: s.notna().all(), error="Outcome cannot be null")
        ]
    )

    price: Series[int] = Field(
        description="American odds (e.g., -110, +150)",
        checks=[
            Check.in_range(-2000, 2000, include_min=True, include_max=True),
            Check(lambda s: s.notna().all(), error="Price cannot be null"),
            Check(lambda s: (s != 0).all(), error="Price cannot be zero")
        ]
    )

    points: Optional[Series[float]] = Field(
        description="Point spread or total (for applicable markets)",
        nullable=True,
        checks=[
            Check.in_range(-100.0, 100.0, include_min=True, include_max=True)
        ]
    )

    line: Optional[Series[float]] = Field(
        description="Betting line value (alias for points)",
        nullable=True,
        checks=[
            Check.in_range(-100.0, 100.0, include_min=True, include_max=True)
        ]
    )

    iso_time: Optional[Series[str]] = Field(
        description="Last update time from bookmaker",
        nullable=True,
        checks=[
            Check(lambda s: s.isna() | pd.to_datetime(s, errors='coerce').notna(),
                  error="Invalid iso_time format")
        ]
    )

    odds_raw_json: Optional[Series[str]] = Field(
        description="Raw JSON data from API",
        nullable=True,
        checks=[Check.str_length(max_val=2000)]
    )

    class Config:
        """Pandera configuration."""
        strict = True
        coerce = True
        ordered = False


class CurrentBestLinesSchema(pa.DataFrameModel):
    """Schema for current best lines table."""

    event_id: Series[str] = Field(
        description="Unique event identifier",
        checks=[
            Check.str_length(min_val=5, max_val=100),
            Check(lambda s: s.notna().all(), error="Event ID cannot be null")
        ]
    )

    market_key: Series[str] = Field(
        description="Market type identifier",
        checks=[
            Check.str_length(min_val=2, max_val=50),
            Check.isin(['h2h', 'spreads', 'totals', 'outrights', 'player_props']),
            Check(lambda s: s.notna().all(), error="Market key cannot be null")
        ]
    )

    outcome: Series[str] = Field(
        description="Bet outcome name",
        checks=[
            Check.str_length(min_val=1, max_val=100),
            Check(lambda s: s.notna().all(), error="Outcome cannot be null")
        ]
    )

    best_book: Series[str] = Field(
        description="Bookmaker offering best price",
        checks=[
            Check.str_length(min_val=2, max_val=50),
            Check(lambda s: s.notna().all(), error="Best book cannot be null")
        ]
    )

    best_price: Series[int] = Field(
        description="Best available American odds",
        checks=[
            Check.in_range(-2000, 2000, include_min=True, include_max=True),
            Check(lambda s: s.notna().all(), error="Best price cannot be null"),
            Check(lambda s: (s != 0).all(), error="Best price cannot be zero")
        ]
    )

    best_points: Optional[Series[float]] = Field(
        description="Point spread or total for best line",
        nullable=True,
        checks=[
            Check.in_range(-100.0, 100.0, include_min=True, include_max=True)
        ]
    )

    updated_at: Series[str] = Field(
        description="Timestamp when best line was computed",
        checks=[
            Check.str_matches(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"),
            Check(lambda s: pd.to_datetime(s, errors='coerce').notna().all(),
                  error="Invalid timestamp format")
        ]
    )

    class Config:
        """Pandera configuration."""
        strict = True
        coerce = True
        ordered = False


class QBPropsOddsSchema(pa.DataFrameModel):
    """Schema for QB props odds data (legacy CSV format)."""

    event_id: Series[str] = Field(
        description="Unique event identifier",
        checks=[
            Check.str_length(min_val=5, max_val=100),
            Check(lambda s: s.notna().all(), error="Event ID cannot be null")
        ]
    )

    player: Series[str] = Field(
        description="Player name",
        checks=[
            Check.str_length(min_val=2, max_val=50),
            Check(lambda s: s.notna().all(), error="Player name cannot be null")
        ]
    )

    market: Series[str] = Field(
        description="Prop market type",
        checks=[
            Check.str_length(min_val=5, max_val=100),
            Check(lambda s: s.str.contains('pass|rush|rec', case=False, na=False).any(),
                  error="Market must contain pass, rush, or rec")
        ]
    )

    line: Series[float] = Field(
        description="Betting line value",
        checks=[
            Check.in_range(0.0, 1000.0, include_min=True, include_max=True),
            Check(lambda s: s.notna().all(), error="Line cannot be null")
        ]
    )

    over_odds: Series[int] = Field(
        description="Over odds in American format",
        checks=[
            Check.in_range(-1000, 1000, include_min=True, include_max=True),
            Check(lambda s: s.notna().all(), error="Over odds cannot be null"),
            Check(lambda s: (s != 0).all(), error="Over odds cannot be zero")
        ]
    )

    under_odds: Series[int] = Field(
        description="Under odds in American format",
        checks=[
            Check.in_range(-1000, 1000, include_min=True, include_max=True),
            Check(lambda s: s.notna().all(), error="Under odds cannot be null"),
            Check(lambda s: (s != 0).all(), error="Under odds cannot be zero")
        ]
    )

    book: Series[str] = Field(
        description="Sportsbook name",
        checks=[
            Check.str_length(min_val=2, max_val=50),
            Check(lambda s: s.notna().all(), error="Book cannot be null")
        ]
    )

    season: Optional[Series[int]] = Field(
        description="NFL season year",
        nullable=True,
        checks=[
            Check.in_range(2020, 2030, include_min=True, include_max=True)
        ]
    )

    def_team: Optional[Series[str]] = Field(
        description="Opposing defense team code",
        nullable=True,
        checks=[Check.str_length(min_val=2, max_val=5)]
    )

    team: Optional[Series[str]] = Field(
        description="Player's team code",
        nullable=True,
        checks=[Check.str_length(min_val=2, max_val=5)]
    )

    class Config:
        """Pandera configuration."""
        strict = True
        coerce = True
        ordered = False


class EdgeSchema(pa.DataFrameModel):
    """Schema for computed betting edges."""

    created_at: Series[str] = Field(
        description="UTC timestamp when edge was computed",
        checks=[
            Check.str_matches(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"),
            Check(lambda s: pd.to_datetime(s, errors='coerce').notna().all(),
                  error="Invalid timestamp format")
        ]
    )

    event_id: Series[str] = Field(
        description="Unique event identifier",
        checks=[
            Check.str_length(min_val=5, max_val=100),
            Check(lambda s: s.notna().all(), error="Event ID cannot be null")
        ]
    )

    book: Series[str] = Field(
        description="Sportsbook name",
        checks=[
            Check.str_length(min_val=2, max_val=50),
            Check(lambda s: s.notna().all(), error="Book cannot be null")
        ]
    )

    player: Series[str] = Field(
        description="Player name",
        checks=[
            Check.str_length(min_val=2, max_val=50),
            Check(lambda s: s.notna().all(), error="Player name cannot be null")
        ]
    )

    market: Series[str] = Field(
        description="Betting market type",
        checks=[
            Check.str_length(min_val=5, max_val=100),
            Check(lambda s: s.notna().all(), error="Market cannot be null")
        ]
    )

    pos: Optional[Series[str]] = Field(
        description="Player position",
        nullable=True,
        checks=[
            Check.isin(['QB', 'RB', 'WR', 'TE']),
            Check.str_length(min_val=2, max_val=2)
        ]
    )

    line: Series[float] = Field(
        description="Betting line value",
        checks=[
            Check.in_range(0.0, 1000.0, include_min=True, include_max=True),
            Check(lambda s: s.notna().all(), error="Line cannot be null")
        ]
    )

    odds_side: Series[str] = Field(
        description="Recommended bet side",
        checks=[
            Check.isin(['over', 'under', 'Over', 'Under']),
            Check(lambda s: s.notna().all(), error="Odds side cannot be null")
        ]
    )

    odds: Series[int] = Field(
        description="American odds for recommended side",
        checks=[
            Check.in_range(-1000, 1000, include_min=True, include_max=True),
            Check(lambda s: s.notna().all(), error="Odds cannot be null"),
            Check(lambda s: (s != 0).all(), error="Odds cannot be zero")
        ]
    )

    model_p: Series[float] = Field(
        description="Model probability (0-1)",
        checks=[
            Check.in_range(0.0, 1.0, include_min=True, include_max=True),
            Check(lambda s: s.notna().all(), error="Model probability cannot be null")
        ]
    )

    p_model_shrunk: Optional[Series[float]] = Field(
        description="Market-shrunk model probability",
        nullable=True,
        checks=[
            Check.in_range(0.0, 1.0, include_min=True, include_max=True)
        ]
    )

    ev_per_dollar: Series[float] = Field(
        description="Expected value per dollar bet",
        checks=[
            Check.in_range(-1.0, 10.0, include_min=True, include_max=True),
            Check(lambda s: s.notna().all(), error="EV per dollar cannot be null")
        ]
    )

    kelly_frac: Series[float] = Field(
        description="Kelly criterion fraction",
        checks=[
            Check.in_range(0.0, 1.0, include_min=True, include_max=True),
            Check(lambda s: s.notna().all(), error="Kelly fraction cannot be null")
        ]
    )

    strategy_tag: Series[str] = Field(
        description="Strategy classification",
        checks=[
            Check.str_length(min_val=3, max_val=50),
            Check(lambda s: s.notna().all(), error="Strategy tag cannot be null")
        ]
    )

    season: Optional[Series[int]] = Field(
        description="NFL season year",
        nullable=True,
        checks=[
            Check.in_range(2020, 2030, include_min=True, include_max=True)
        ]
    )

    week: Optional[Series[int]] = Field(
        description="NFL week number",
        nullable=True,
        checks=[
            Check.in_range(1, 22, include_min=True, include_max=True)
        ]
    )

    opponent_def_code: Optional[Series[str]] = Field(
        description="Opponent defense team code",
        nullable=True,
        checks=[Check.str_length(min_val=2, max_val=5)]
    )

    def_tier: Optional[Series[str]] = Field(
        description="Defense tier classification",
        nullable=True,
        checks=[Check.isin(['generous', 'stingy', 'neutral'])]
    )

    def_score: Optional[Series[float]] = Field(
        description="Defense strength score",
        nullable=True,
        checks=[Check.in_range(-10.0, 10.0, include_min=True, include_max=True)]
    )

    class Config:
        """Pandera configuration."""
        strict = True
        coerce = True
        ordered = False


class DefenseRatingsSchema(pa.DataFrameModel):
    """Schema for defense ratings data."""

    defteam: Series[str] = Field(
        description="Defense team code",
        checks=[
            Check.str_length(min_val=2, max_val=5),
            Check(lambda s: s.notna().all(), error="Defense team cannot be null")
        ]
    )

    season: Series[int] = Field(
        description="NFL season year",
        checks=[
            Check.in_range(2020, 2030, include_min=True, include_max=True),
            Check(lambda s: s.notna().all(), error="Season cannot be null")
        ]
    )

    pos: Series[str] = Field(
        description="Position group being defended",
        checks=[
            Check.isin(['QB_PASS', 'RB_RUSH', 'WR_REC', 'TE_REC']),
            Check(lambda s: s.notna().all(), error="Position cannot be null")
        ]
    )

    week: Optional[Series[int]] = Field(
        description="Week number (null for season-long)",
        nullable=True,
        checks=[
            Check.in_range(1, 22, include_min=True, include_max=True)
        ]
    )

    score: Series[float] = Field(
        description="Defense performance score",
        checks=[
            Check.in_range(-10.0, 10.0, include_min=True, include_max=True),
            Check(lambda s: s.notna().all(), error="Score cannot be null")
        ]
    )

    tier: Series[str] = Field(
        description="Defense tier classification",
        checks=[
            Check.isin(['generous', 'stingy', 'neutral']),
            Check(lambda s: s.notna().all(), error="Tier cannot be null")
        ]
    )

    score_adj: Optional[Series[float]] = Field(
        description="Adjusted defense score",
        nullable=True,
        checks=[Check.in_range(-10.0, 10.0, include_min=True, include_max=True)]
    )

    tier_adj: Optional[Series[str]] = Field(
        description="Adjusted defense tier",
        nullable=True,
        checks=[Check.isin(['generous', 'stingy', 'neutral'])]
    )

    class Config:
        """Pandera configuration."""
        strict = True
        coerce = True
        ordered = False


# Validation functions for easy integration
def validate_odds_snapshots(df: pd.DataFrame) -> pd.DataFrame:
    """Validate odds snapshots DataFrame with comprehensive error reporting."""
    try:
        return OddsSnapshotSchema.validate(df, lazy=True)
    except pa.errors.SchemaErrors as e:
        print(f"Odds snapshots validation failed:")
        for error in e.failure_cases:
            print(f"  - {error}")
        raise


def validate_current_best_lines(df: pd.DataFrame) -> pd.DataFrame:
    """Validate current best lines DataFrame."""
    try:
        return CurrentBestLinesSchema.validate(df, lazy=True)
    except pa.errors.SchemaErrors as e:
        print(f"Best lines validation failed:")
        for error in e.failure_cases:
            print(f"  - {error}")
        raise


def validate_edges(df: pd.DataFrame) -> pd.DataFrame:
    """Validate betting edges DataFrame."""
    try:
        return EdgeSchema.validate(df, lazy=True)
    except pa.errors.SchemaErrors as e:
        print(f"Edges validation failed:")
        for error in e.failure_cases:
            print(f"  - {error}")
        raise


def validate_qb_props(df: pd.DataFrame) -> pd.DataFrame:
    """Validate QB props odds DataFrame."""
    try:
        return QBPropsOddsSchema.validate(df, lazy=True)
    except pa.errors.SchemaErrors as e:
        print(f"QB props validation failed:")
        for error in e.failure_cases:
            print(f"  - {error}")
        raise


def validate_defense_ratings(df: pd.DataFrame) -> pd.DataFrame:
    """Validate defense ratings DataFrame."""
    try:
        return DefenseRatingsSchema.validate(df, lazy=True)
    except pa.errors.SchemaErrors as e:
        print(f"Defense ratings validation failed:")
        for error in e.failure_cases:
            print(f"  - {error}")
        raise