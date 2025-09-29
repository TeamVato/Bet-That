"""Shared test fixtures and configuration for backend tests."""

import sqlite3
import tempfile
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)

    yield db_path

    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def sample_props_data():
    """Sample props data for testing."""
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
                "pos": "QB",
            }
        ]
    )


@pytest.fixture
def sample_projections_data():
    """Sample projections data for testing."""
    return pd.DataFrame(
        [
            {
                "event_id": "2025-01-01-KC-BUF",
                "player": "Patrick Mahomes",
                "mu": 285.0,
                "sigma": 45.0,
                "season": 2025,
                "week": 1,
            }
        ]
    )


@pytest.fixture
def odds_database(temp_db):
    """Create a test database with odds schema."""
    con = sqlite3.connect(temp_db)

    # Create basic odds table structure
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS odds (
            id INTEGER PRIMARY KEY,
            event_id TEXT,
            player TEXT,
            market TEXT,
            line REAL,
            over_odds INTEGER,
            under_odds INTEGER,
            book TEXT,
            updated_at TEXT
        )
    """
    )

    # Insert sample data
    con.execute(
        """
        INSERT INTO odds (event_id, player, market, line, over_odds, under_odds, book, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            "test-game",
            "Test Player",
            "player_pass_yds",
            250.5,
            -110,
            -110,
            "draftkings",
            "2025-01-01T12:00:00Z",
        ),
    )

    con.commit()
    con.close()

    return temp_db
