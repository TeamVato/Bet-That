import os
import sqlite3

import pandas as pd


EXPORT_PATH = "storage/exports/edges_latest.csv"
DB_PATH = "storage/odds.db"


def main() -> None:
    assert os.path.exists(EXPORT_PATH), f"missing {EXPORT_PATH}"

    df = pd.read_csv(EXPORT_PATH)
    assert "season" in df.columns, "season column missing in edges export"
    assert df["season"].notna().any(), "season is all NA in edges export"

    with sqlite3.connect(DB_PATH) as con:
        cols = {row[1] for row in con.execute("PRAGMA table_info(odds_csv_raw);").fetchall()}
    assert "season" in cols, "odds_csv_raw.season column missing"

    print("SMOKE OK: season present in DB and export.")


if __name__ == "__main__":
    main()
