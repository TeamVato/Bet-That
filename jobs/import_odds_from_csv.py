# jobs/import_odds_from_csv.py
# Robust CSV -> SQLite importer with progress logs and SQLite lock handling
import os, sys, time, sqlite3
from pathlib import Path
from typing import List, Tuple

import pandas as pd

DB = Path("storage/odds.db")
CSV_PATH = Path(os.getenv("CSV_PATH", "storage/imports/odds_snapshot.csv"))
BATCH_SIZE = int(os.getenv("CSV_BATCH_SIZE", "1000"))
LOCK_RETRIES = int(os.getenv("SQLITE_LOCK_RETRIES", "10"))
LOCK_SLEEP = float(os.getenv("SQLITE_LOCK_SLEEP", "0.5"))

DDL_RAW = """
CREATE TABLE IF NOT EXISTS odds_csv_raw (
  event_id TEXT,
  commence_time TEXT,
  home_team TEXT,
  away_team TEXT,
  player TEXT,
  market TEXT,
  line REAL,
  over_odds INTEGER,
  under_odds INTEGER,
  book TEXT,
  updated_at TEXT,
  x_used INTEGER,
  x_remaining INTEGER,
  season INTEGER
);
"""

DDL_BEST = """
DROP TABLE IF EXISTS current_best_lines;
CREATE TABLE current_best_lines AS
WITH ranked AS (
  SELECT
    player, market, book, line, over_odds, under_odds, updated_at, event_id, home_team, away_team,
    ROW_NUMBER() OVER (
      PARTITION BY player, market
      ORDER BY ABS(COALESCE(line, 9999)) ASC,
               COALESCE(under_odds, -99999) DESC,
               COALESCE(over_odds, -99999) DESC,
               datetime(updated_at) DESC
    ) AS rnk
  FROM odds_csv_raw
)
SELECT * FROM ranked WHERE rnk = 1;
"""


def infer_season_series(commence_series: pd.Series | None) -> pd.Series:
    """Vectorized season inference from commence timestamps.

    Robustly parses ISO8601 strings, coercing invalid values to ``NaT`` and
    returning a nullable integer Series where August–December map to the same
    calendar year and January–July map to the previous year.
    """

    if commence_series is None:
        return pd.Series(pd.NA, dtype="Int64")

    ts = pd.to_datetime(commence_series, utc=True, errors="coerce")
    years = ts.dt.year
    seasons = years.where(ts.dt.month >= 8, years - 1)
    return seasons.astype("Int64")


def infer_season(commence_ts: str | None) -> int | None:
    """Scalar helper that reuses :func:`infer_season_series`."""

    if commence_ts is None:
        return None
    series = infer_season_series(pd.Series([commence_ts]))
    value = series.iloc[0] if not series.empty else pd.NA
    if pd.isna(value):
        return None
    return int(value)

def _insert_with_retry(con: sqlite3.Connection, sql: str, rows: List[Tuple]):
    attempt = 0
    while True:
        try:
            con.executemany(sql, rows)
            return
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if "locked" in msg or "busy" in msg:
                if attempt >= LOCK_RETRIES: raise
                attempt += 1
                time.sleep(LOCK_SLEEP * attempt)
            else:
                raise

INSERT_SQL = (
    "INSERT INTO odds_csv_raw ("
    "event_id, commence_time, home_team, away_team, player, market, line, "
    "over_odds, under_odds, book, updated_at, x_used, x_remaining, season"
    ") VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
)


def main():
    t0 = time.perf_counter()
    if not CSV_PATH.exists():
        raise SystemExit(f"Missing CSV at {CSV_PATH}. Put your Sheets export there or set CSV_PATH.")

    DB.parent.mkdir(parents=True, exist_ok=True)
    print(f"[1/5] Opening DB at {DB} ...")
    con = sqlite3.connect(DB, timeout=10.0, isolation_level=None)  # autocommit
    try:
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("PRAGMA busy_timeout=10000;")  # 10s

        print("[2/5] Ensuring tables exist ...")
        con.executescript(DDL_RAW)
        cur = con.execute("PRAGMA table_info(odds_csv_raw);")
        cols = {row[1] for row in cur.fetchall()}
        if "season" not in cols:
            con.execute("ALTER TABLE odds_csv_raw ADD COLUMN season INTEGER;")

        print("[3/5] Loading CSV from", CSV_PATH)
        df = pd.read_csv(CSV_PATH)
        if df.columns.empty:
            raise SystemExit("CSV appears to have no header row.")
        print("     Detected columns:", ", ".join(map(str, df.columns.tolist())))

        if "season" in df.columns:
            df["season"] = pd.to_numeric(df["season"], errors="coerce").astype("Int64")
        elif "commence_time" in df.columns:
            df["season"] = infer_season_series(df["commence_time"])
        else:
            df["season"] = pd.Series(pd.NA, index=df.index, dtype="Int64")

        if "line" in df.columns:
            df["line"] = pd.to_numeric(df["line"], errors="coerce")
        for col in ("over_odds", "under_odds", "x_used", "x_remaining"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

        required_cols = [
            "event_id",
            "commence_time",
            "home_team",
            "away_team",
            "player",
            "market",
            "line",
            "over_odds",
            "under_odds",
            "book",
            "updated_at",
            "x_used",
            "x_remaining",
            "season",
        ]
        for col in required_cols:
            if col not in df.columns:
                df[col] = None
        df = df[required_cols]
        df = df.astype(object)
        df = df.where(pd.notna(df), None)

        con.execute("BEGIN IMMEDIATE;")   # take write lock
        con.execute("DELETE FROM odds_csv_raw;")

        rows: List[Tuple] = []
        total = 0
        for row in df.itertuples(index=False, name=None):
            rows.append(row)
            if len(rows) >= BATCH_SIZE:
                _insert_with_retry(con, INSERT_SQL, rows)
                total += len(rows)
                rows.clear()
                print(f"     Inserted {total} rows ...")

        if rows:
            _insert_with_retry(con, INSERT_SQL, rows)
            total += len(rows)
            print(f"     Inserted {total} rows (final batch) ...")

        con.execute("COMMIT;")

        print("[4/5] Refreshing current_best_lines ...")
        con.executescript(DDL_BEST)
        print("[5/5] Done. Rows loaded:", total)
    finally:
        con.close()
    print(f"Total time: {time.perf_counter() - t0:.2f}s")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted."); sys.exit(130)
