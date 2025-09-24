# jobs/import_odds_from_csv.py
# Robust CSV -> SQLite importer with progress logs and SQLite lock handling
import os
import sys
import csv
import time
import sqlite3
from pathlib import Path
from typing import Iterable, List, Tuple

DB = Path("storage/odds.db")
CSV_PATH = Path(os.getenv("CSV_PATH", "storage/imports/odds_snapshot.csv"))
BATCH_SIZE = int(os.getenv("CSV_BATCH_SIZE", "1000"))
LOCK_RETRIES = int(os.getenv("SQLITE_LOCK_RETRIES", "10"))
LOCK_SLEEP = float(os.getenv("SQLITE_LOCK_SLEEP", "0.5"))

DDL_RAW = \
"""
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
  x_remaining INTEGER
);
"""

DDL_BEST = \
"""
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


def _to_float(v):
    if v is None:
        return None
    v = str(v).strip()
    if v in ("", "null", "None"):
        return None
    try:
        return float(v)
    except Exception:
        return None


def _to_int(v):
    if v is None:
        return None
    v = str(v).strip()
    if v in ("", "null", "None"):
        return None
    try:
        return int(v)
    except Exception:
        return None


def _insert_with_retry(con: sqlite3.Connection, sql: str, rows: List[Tuple]):
    attempt = 0
    while True:
        try:
            con.executemany(sql, rows)
            return
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if "locked" in msg or "busy" in msg:
                if attempt >= LOCK_RETRIES:
                    raise
                attempt += 1
                time.sleep(LOCK_SLEEP * attempt)
            else:
                raise


def main():
    t0 = time.perf_counter()
    if not CSV_PATH.exists():
        raise SystemExit(f"Missing CSV at {CSV_PATH}. Put your Sheets export there or set CSV_PATH.")

    DB.parent.mkdir(parents=True, exist_ok=True)
    print(f"[1/5] Opening DB at {DB} ...")
    con = sqlite3.connect(DB, timeout=10.0, isolation_level=None)  # autocommit mode
    try:
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("PRAGMA busy_timeout=10000;")  # 10s busy timeout on locked db

        print("[2/5] Ensuring tables exist ...")
        con.executescript(DDL_RAW)

        print("[3/5] Loading CSV from", CSV_PATH)
        with open(CSV_PATH, newline='', encoding='utf-8') as f:
            rdr = csv.DictReader(f)
            field_preview = rdr.fieldnames
            if not field_preview:
                raise SystemExit("CSV appears to have no header row.")
            print("     Detected columns:", ", ".join(field_preview))

            # Replace snapshot
            con.execute("BEGIN IMMEDIATE;")  # take write lock, fail fast if another writer holds it
            con.execute("DELETE FROM odds_csv_raw;")

            rows: List[Tuple] = []
            total = 0
            for r in rdr:
                rows.append(
                    (
                        r.get("event_id"),
                        r.get("commence_time"),
                        r.get("home_team"),
                        r.get("away_team"),
                        r.get("player"),
                        r.get("market"),
                        _to_float(r.get("line")),
                        _to_int(r.get("over_odds")),
                        _to_int(r.get("under_odds")),
                        r.get("book"),
                        r.get("updated_at"),
                        _to_int(r.get("x_used")),
                        _to_int(r.get("x_remaining")),
                    )
                )
                if len(rows) >= BATCH_SIZE:
                    _insert_with_retry(con, "INSERT INTO odds_csv_raw VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
                    total += len(rows)
                    print(f"     Inserted {total} rows ...")
                    rows.clear()

            if rows:
                _insert_with_retry(con, "INSERT INTO odds_csv_raw VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
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
        print("Interrupted.")
        sys.exit(130)
