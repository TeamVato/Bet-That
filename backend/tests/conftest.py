"""Shared test fixtures and configuration for backend tests."""

import sqlite3
import tempfile
from pathlib import Path
from typing import Generator

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from api.database import Base, get_db
from api.main import app


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


@pytest.fixture
def test_db() -> Generator[Session, None, None]:
    """Create a test database session for FastAPI testing"""
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)

    # Create engine and session
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Cleanup
        if db_path.exists():
            db_path.unlink()


def override_get_db(test_db: Session):
    """Override get_db dependency for testing"""

    def _override():
        try:
            yield test_db
        finally:
            pass  # Session management handled by fixture

    return _override


from typing import Generator

@pytest.fixture
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with overridden database dependency"""
    app.dependency_overrides[get_db] = override_get_db(test_db)

    with TestClient(app) as test_client:
        yield test_client

    # Clean up overrides
    app.dependency_overrides.clear()
