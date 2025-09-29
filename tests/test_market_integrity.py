import sqlite3

import pandas as pd


def test_no_duplicate_book_lines():
    with sqlite3.connect("storage/odds.db") as con:
        df = pd.read_sql(
            """
            SELECT event_id,market,book,line,side,MAX(updated_at) as updated_at, COUNT(*) c
            FROM odds_csv_raw
            GROUP BY 1,2,3,4,5
            HAVING c>1
            """,
            con,
        )
    assert len(df) == 0, f"Duplicate rows found: {len(df)}"


def test_overround_bounds():
    with sqlite3.connect("storage/odds.db") as con:
        df = pd.read_sql(
            "SELECT overround FROM odds_csv_raw WHERE overround IS NOT NULL",
            con,
        )
    if df.empty:
        return
    assert (df["overround"].between(1.00, 1.15)).all(), "Overround out of bounds detected"
