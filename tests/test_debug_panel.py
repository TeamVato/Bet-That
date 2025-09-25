import sqlite3

import pandas as pd

from app.debug_panel import (
    count_rows,
    counts_by,
    edges_quality,
    edges_weather_coverage,
    max_updated,
    odds_staleness,
    table_exists,
)


def _mkdb(tmp_path):
    db_path = tmp_path / "debug.db"
    con = sqlite3.connect(db_path)
    con.executescript(
        """
        CREATE TABLE odds_csv_raw (book TEXT, updated_at TEXT);
        INSERT INTO odds_csv_raw VALUES
            ('draftkings','2025-09-25T01:00:00Z'),
            ('fanduel','2025-09-25T02:00:00Z');

        CREATE TABLE current_best_lines (stale INTEGER, updated_at TEXT);
        INSERT INTO current_best_lines VALUES
            (0,'2025-09-25T02:10:00Z'),
            (1,'2025-09-25T02:20:00Z');

        CREATE TABLE edges (
            event_id TEXT,
            opponent_def_code TEXT,
            def_tier TEXT,
            def_score REAL,
            updated_at TEXT
        );
        INSERT INTO edges VALUES ('EV1', NULL, NULL, NULL, '2025-09-25T02:30:00Z');

        CREATE TABLE weather (event_id TEXT, game_id TEXT, updated_at TEXT);
        INSERT INTO weather VALUES ('EV1', 'G1', '2025-09-25T02:40:00Z');
        """
    )
    con.commit()
    con.close()
    return db_path


def test_basic_counts(tmp_path):
    db_path = _mkdb(tmp_path)
    con = sqlite3.connect(db_path)
    try:
        assert table_exists(con, "weather") is True
        assert count_rows(con, "odds_csv_raw") == 2
        assert count_rows(con, "edges") == 1
        assert max_updated(con, "edges") == '2025-09-25T02:30:00Z'
        df = counts_by(con, "odds_csv_raw", "book")
        assert not df.empty
        assert set(df["key"].tolist()) == {"draftkings", "fanduel"}
    finally:
        con.close()


def test_quality_and_staleness(tmp_path):
    db_path = _mkdb(tmp_path)
    con = sqlite3.connect(db_path)
    try:
        quality = edges_quality(con)
        assert quality["edges_rows"] == 1
        assert quality["missing_def_code"] == 1
        staleness = odds_staleness(con)
        assert staleness == {"fresh": 1, "stale": 1}
        coverage = edges_weather_coverage(con)
        assert coverage == {"edges_with_weather": 1, "edges_total": 1}
    finally:
        con.close()


def test_counts_by_missing_table(tmp_path):
    db_path = tmp_path / "missing.db"
    con = sqlite3.connect(db_path)
    try:
        df = counts_by(con, "does_not_exist", "foo")
        assert isinstance(df, pd.DataFrame)
        assert df.empty
    finally:
        con.close()
