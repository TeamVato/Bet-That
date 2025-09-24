# jobs/import_odds_from_csv.py
# Robust CSV -> SQLite importer with progress logs and SQLite lock handling
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import List, Tuple

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd

from engine.odds_normalizer import normalize_long_odds

DB = Path("storage/odds.db")
DEFAULT_CSV_PATH = Path("storage/imports/odds_snapshot.csv")
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
  side TEXT,
  odds INTEGER,
  over_odds INTEGER,
  under_odds INTEGER,
  book TEXT,
  updated_at TEXT,
  implied_prob REAL,
  fair_prob REAL,
  overround REAL,
  is_stale INTEGER,
  fair_decimal REAL,
  x_used INTEGER,
  x_remaining INTEGER,
  season INTEGER
);
"""

DDL_BEST = """
DROP TABLE IF EXISTS current_best_lines;
CREATE TABLE current_best_lines AS
WITH latest AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY player, market, book, line, side
           ORDER BY datetime(updated_at) DESC
         ) AS rnk
  FROM odds_csv_raw
),
filtered AS (
  SELECT * FROM latest WHERE rnk = 1
),
wide AS (
  SELECT
    player,
    market,
    book,
    line,
    MAX(CASE WHEN LOWER(side) = 'over' THEN odds END) AS over_odds,
    MAX(CASE WHEN LOWER(side) = 'under' THEN odds END) AS under_odds,
    MAX(updated_at) AS updated_at,
    MAX(event_id) AS event_id,
    MAX(home_team) AS home_team,
    MAX(away_team) AS away_team
  FROM filtered
  GROUP BY player, market, book, line
)
SELECT * FROM wide;
"""


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
    "event_id, commence_time, home_team, away_team, player, market, line, side, odds, "
    "over_odds, under_odds, book, updated_at, implied_prob, fair_prob, overround, is_stale, fair_decimal, "
    "x_used, x_remaining, season"
    ") VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
)


def _resolve_csv_path() -> Path:
    return Path(os.getenv("CSV_PATH", str(DEFAULT_CSV_PATH)))


def _resolve_stale_minutes() -> int:
    return int(os.getenv("STALE_MINUTES", "120"))


def _ensure_columns(con: sqlite3.Connection) -> None:
    cur = con.execute("PRAGMA table_info(odds_csv_raw);")
    cols = {row[1] for row in cur.fetchall()}
    optional_cols = {
        "season": "INTEGER",
        "side": "TEXT",
        "odds": "INTEGER",
        "implied_prob": "REAL",
        "fair_prob": "REAL",
        "overround": "REAL",
        "is_stale": "INTEGER",
        "fair_decimal": "REAL",
    }
    for col, col_type in optional_cols.items():
        if col not in cols:
            con.execute(f"ALTER TABLE odds_csv_raw ADD COLUMN {col} {col_type};")


def _wide_to_long(df: pd.DataFrame) -> pd.DataFrame:
    if "side" in df.columns and "odds" in df.columns:
        return df
    if "over_odds" not in df.columns and "under_odds" not in df.columns:
        return df
    records: List[dict] = []
    cols = list(df.columns)
    for row in df.to_dict("records"):
        base = {k: row.get(k) for k in cols if k not in {"over_odds", "under_odds", "side", "odds"}}
        for side, key in (("Over", "over_odds"), ("Under", "under_odds")):
            odds_val = row.get(key)
            if pd.isna(odds_val):
                continue
            rec = base.copy()
            rec["side"] = side
            rec["odds"] = odds_val
            records.append(rec)
    if not records:
        return df
    return pd.DataFrame.from_records(records)

def main():
    t0 = time.perf_counter()
    csv_path = _resolve_csv_path()
    stale_minutes = _resolve_stale_minutes()
    if not csv_path.exists():
        raise SystemExit(
            f"Missing CSV at {csv_path}. Put your Sheets export there or set CSV_PATH."
        )

    DB.parent.mkdir(parents=True, exist_ok=True)
    print(f"[1/5] Opening DB at {DB} ...")
    con = sqlite3.connect(DB, timeout=10.0, isolation_level=None)  # autocommit
    try:
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("PRAGMA busy_timeout=10000;")  # 10s

        print("[2/5] Ensuring tables exist ...")
        con.executescript(DDL_RAW)
        _ensure_columns(con)

        print("[3/5] Loading CSV from", csv_path)
        df = pd.read_csv(csv_path)
        if df.columns.empty:
            raise SystemExit("CSV appears to have no header row.")
        print("     Detected columns:", ", ".join(map(str, df.columns.tolist())))

        df = _wide_to_long(df)

        df = normalize_long_odds(df, stale_minutes=stale_minutes)

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
