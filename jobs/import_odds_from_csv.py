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

from engine.odds_math import (
    american_to_decimal,
    american_to_implied_prob,
    devig_proportional_from_decimal,
)

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


def _normalize_side(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized if not normalized else normalized.title()
    return value


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


def _compute_devig_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df["fair_prob"] = pd.NA
    df["fair_decimal"] = pd.NA
    df["overround"] = pd.NA
    valid = df["odds"].notna()
    if not valid.any():
        return df
    grouped = df.loc[valid].groupby(
        ["event_id", "market", "book", "line"], dropna=False, sort=False
    )
    for _, group in grouped:
        if len(group) < 2:
            continue
        try:
            decimals: List[float] = [american_to_decimal(int(odds)) for odds in group["odds"]]
        except ValueError:
            continue
        pairs, overround = devig_proportional_from_decimal(decimals)
        for (idx, (prob, fair_dec)) in zip(group.index, pairs):
            df.at[idx, "fair_prob"] = prob
            df.at[idx, "fair_decimal"] = fair_dec
            df.at[idx, "overround"] = overround
    return df


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

        if "season" in df.columns:
            df["season"] = pd.to_numeric(df["season"], errors="coerce").astype("Int64")
        elif "commence_time" in df.columns:
            df["season"] = infer_season_series(df["commence_time"])
        else:
            df["season"] = pd.Series(pd.NA, index=df.index, dtype="Int64")

        if "line" in df.columns:
            df["line"] = pd.to_numeric(df["line"], errors="coerce")
        for col in ("odds", "over_odds", "under_odds", "x_used", "x_remaining"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

        df["side"] = df.get("side", pd.Series(pd.NA, index=df.index)).map(_normalize_side)

        required_cols = [
            "event_id",
            "commence_time",
            "home_team",
            "away_team",
            "player",
            "market",
            "line",
            "side",
            "odds",
            "book",
            "updated_at",
            "season",
            "x_used",
            "x_remaining",
        ]
        for col in required_cols:
            if col not in df.columns:
                df[col] = None

        df = df[required_cols]

        updated_at_dt = pd.to_datetime(df["updated_at"], utc=True, errors="coerce")
        df["_updated_at"] = updated_at_dt
        df = df.sort_values("_updated_at")
        dedup_keys = ["event_id", "market", "book", "side", "line"]
        df = df.drop_duplicates(subset=dedup_keys, keep="last")

        df["implied_prob"] = df["odds"].apply(
            lambda o: None if pd.isna(o) else american_to_implied_prob(int(o))
        )

        df = _compute_devig_metrics(df)

        now_utc = pd.Timestamp.utcnow()
        if stale_minutes > 0:
            delta = now_utc - df["_updated_at"]
            stale_series = (delta > pd.to_timedelta(stale_minutes, unit="m")).astype("Int64")
            stale_series[df["_updated_at"].isna()] = pd.NA
        else:
            stale_series = pd.Series(pd.NA, index=df.index, dtype="Int64")
        df["is_stale"] = stale_series

        df["over_odds"] = pd.NA
        df["under_odds"] = pd.NA
        side_lower = df["side"].str.lower()
        over_mask = side_lower == "over"
        under_mask = side_lower == "under"
        df.loc[over_mask, "over_odds"] = df.loc[over_mask, "odds"]
        df.loc[under_mask, "under_odds"] = df.loc[under_mask, "odds"]

        df = df.assign(fair_prob=df["fair_prob"], fair_decimal=df["fair_decimal"], overround=df["overround"])

        df = df[
            [
                "event_id",
                "commence_time",
                "home_team",
                "away_team",
                "player",
                "market",
                "line",
                "side",
                "odds",
                "over_odds",
                "under_odds",
                "book",
                "updated_at",
                "implied_prob",
                "fair_prob",
                "overround",
                "is_stale",
                "fair_decimal",
                "x_used",
                "x_remaining",
                "season",
            ]
        ]

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
