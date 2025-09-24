import os
import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))


def test_stale_flag_column_exists():
    os.environ["CSV_PATH"] = "tests/fixtures/odds_sample_two_way.csv"
    os.environ["STALE_MINUTES"] = "120"
    import jobs.import_odds_from_csv as mod

    mod.main()
    with sqlite3.connect("storage/odds.db") as con:
        df = pd.read_sql("SELECT is_stale FROM odds_csv_raw LIMIT 10", con)
    assert "is_stale" in df.columns
