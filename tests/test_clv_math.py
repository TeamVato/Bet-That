import math
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from jobs.compute_clv import price_is_better, run as run_clv
from utils import odds


def test_odds_helpers_roundtrip():
    assert pytest.approx(odds.american_to_decimal(-110), rel=1e-6) == 1.909090909
    assert pytest.approx(odds.american_to_decimal(150), rel=1e-6) == 2.5
    assert pytest.approx(odds.implied_from_decimal(2.5), rel=1e-6) == 0.4
    with pytest.raises(ValueError):
        odds.american_to_decimal(0)


def test_logit_bounds():
    val = odds.logit(0.6)
    assert pytest.approx(val, rel=1e-6) == math.log(0.6 / 0.4)
    with pytest.raises(ValueError):
        odds.logit(1.0)
    with pytest.raises(ValueError):
        odds.logit(0.0)


def test_price_is_better_identifies_favorable_line():
    assert price_is_better(-110, -120) == 1  # less negative is better
    assert price_is_better(150, 140) == 1    # larger positive is better
    assert price_is_better(-120, -110) == 0
    assert price_is_better(None, -110) is None
    assert price_is_better(-110, None) is None


def _create_schema(con: sqlite3.Connection) -> None:
    con.execute(
        """
        CREATE TABLE edges (
            edge_id TEXT PRIMARY KEY,
            event_id TEXT,
            market TEXT,
            odds_side TEXT,
            line REAL,
            odds INTEGER,
            fair_prob REAL,
            implied_prob REAL,
            book TEXT
        )
        """
    )
    con.execute(
        """
        CREATE TABLE closing_lines (
            closing_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT,
            market TEXT,
            side TEXT,
            line REAL,
            book TEXT,
            odds_decimal REAL,
            odds_american INTEGER,
            implied_prob REAL,
            overround REAL,
            fair_prob_close REAL,
            ts_close TEXT,
            is_primary INTEGER,
            ingest_source TEXT,
            source_run_id TEXT,
            raw_payload_hash TEXT
        )
        """
    )
    con.execute(
        """
        CREATE TABLE clv_log (
            clv_id INTEGER PRIMARY KEY AUTOINCREMENT,
            edge_id TEXT,
            bet_id TEXT,
            event_id TEXT,
            market TEXT,
            side TEXT,
            line REAL,
            entry_odds INTEGER,
            close_odds INTEGER,
            entry_prob_fair REAL,
            close_prob_fair REAL,
            delta_prob REAL,
            delta_logit REAL,
            clv_cents REAL,
            beat_close INTEGER,
            primary_book TEXT,
            match_tolerance REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def test_compute_clv_writes_entries(tmp_path):
    db_path = tmp_path / "odds.db"
    with sqlite3.connect(db_path) as con:
        _create_schema(con)
        con.execute(
            """
            INSERT INTO edges(edge_id, event_id, market, odds_side, line, odds, fair_prob, implied_prob, book)
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            ("E1", "EVT1", "player_props", "over", 285.5, -110, 0.50, 0.5238, "dk"),
        )
        con.execute(
            """
            INSERT INTO closing_lines(event_id, market, side, line, book, odds_decimal, odds_american,
                                      implied_prob, overround, fair_prob_close, ts_close, is_primary)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                "EVT1",
                "player_props",
                "over",
                285.5,
                "dk",
                odds.american_to_decimal(-120),
                -120,
                odds.implied_from_decimal(odds.american_to_decimal(-120)),
                1.05,
                0.55,
                "2025-09-20T15:56:00Z",
                1,
            ),
        )

    summary = run_clv(db_path, line_tolerance=0.5)
    assert summary.matched == 1
    assert summary.total_edges == 1
    assert summary.coverage == pytest.approx(1.0)
    with sqlite3.connect(db_path) as con:
        rows = con.execute(
            "SELECT edge_id, entry_odds, close_odds, delta_prob, beat_close, match_tolerance FROM clv_log"
        ).fetchall()
    assert len(rows) == 1
    edge_id, entry_odds, close_odds, delta_prob, beat_close, match_tol = rows[0]
    assert edge_id == "E1"
    assert entry_odds == -110
    assert close_odds == -120
    assert pytest.approx(delta_prob, rel=1e-6) == 0.05
    assert beat_close == 1
    assert pytest.approx(match_tol, rel=1e-6) == 0.0
