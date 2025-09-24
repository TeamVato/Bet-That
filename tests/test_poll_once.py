import os
import sqlite3
from unittest import mock

import pandas as pd

from jobs import poll_odds


def test_poll_once_normalizes_and_writes(tmp_path, monkeypatch):
    dbdir = tmp_path / "storage"
    dbdir.mkdir(parents=True, exist_ok=True)
    db = dbdir / "odds.db"
    monkeypatch.setenv("ODDS_API_KEYS", "k1")

    sample = {
        "json": [
            {
                "id": "EVT1",
                "commence_time": "2025-09-20T16:00:00Z",
                "home_team": "KC",
                "away_team": "BUF",
                "bookmakers": [
                    {
                        "key": "dk",
                        "last_update": "2025-09-20T15:55:00Z",
                        "markets": [
                            {
                                "key": "player_props",
                                "outcomes": [
                                    {
                                        "name": "Over",
                                        "price": -110,
                                        "point": 285.5,
                                        "description": "Patrick Mahomes",
                                    },
                                    {
                                        "name": "Under",
                                        "price": -110,
                                        "point": 285.5,
                                        "description": "Patrick Mahomes",
                                    },
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
    }

    with mock.patch.object(poll_odds, "fetch_markets", return_value=sample):
        # Redirect DB path for this test
        with mock.patch.object(poll_odds, "DB", str(db)):
            # Run once (simulate args)
            with mock.patch("sys.argv", ["poll_odds.py", "--once", "--dry-run"]):
                # Dry run should not write
                poll_odds.main()
            with mock.patch("sys.argv", ["poll_odds.py", "--once"]):
                poll_odds.main()

    assert db.exists()
    with sqlite3.connect(db) as con:
        cur = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='odds_csv_raw'"
        )
        assert cur.fetchone() is not None
        df = pd.read_sql("SELECT * FROM odds_csv_raw", con)
    assert len(df) > 0
    assert df["implied_prob"].notna().any()
    assert df["fair_prob"].notna().any()
    assert df["overround"].notna().any()
    assert "is_stale" in df.columns

