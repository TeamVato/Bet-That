# jobs/import_odds_from_csv.py
# Robust CSV -> SQLite importer with progress logs and SQLite lock handling
from __future__ import annotations
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd

from engine.odds_normalizer import normalize_long_odds
from engine.week_populator import populate_week_from_schedule

UTC = timezone.utc

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
  pos TEXT,
  implied_prob REAL,
  fair_prob REAL,
  overround REAL,
  is_stale INTEGER,
  fair_decimal REAL,
  x_used INTEGER,
  x_remaining INTEGER,
  season INTEGER,
  ingest_source TEXT
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
    MAX(pos) AS pos,
    MAX(CASE WHEN LOWER(side) = 'over' THEN odds END) AS over_odds,
    MAX(CASE WHEN LOWER(side) = 'under' THEN odds END) AS under_odds,
    MAX(updated_at) AS updated_at,
    MAX(event_id) AS event_id,
    MAX(commence_time) AS commence_time,
    MAX(home_team) AS home_team,
    MAX(away_team) AS away_team,
    -- Add critical join keys for EdgeEngine
    MAX(season) AS season,
    NULL AS week,  -- Will be populated by post-processing
    NULL AS team_code,  -- Will be populated by post-processing
    NULL AS opponent_def_code,  -- Will be populated by post-processing
    MAX(is_stale) AS is_stale
  FROM filtered
  GROUP BY player, market, book, line
)
SELECT * FROM wide;
"""




def dedupe_latest(df: pd.DataFrame, subset: list[str], *, sort_col: str | None = None) -> pd.DataFrame:
    """Return the latest rows per subset columns, keeping the most recent updated_at."""
    if df.empty or not subset:
        return df
    working = df.copy()
    if sort_col and sort_col in working.columns:
        working = working.sort_values(sort_col)
    return working.drop_duplicates(subset, keep="last")




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
    "over_odds, under_odds, book, updated_at, pos, implied_prob, fair_prob, overround, is_stale, fair_decimal, "
    "x_used, x_remaining, season, ingest_source"
    ") VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
)


def _resolve_csv_path() -> Path:
    return Path(os.getenv("CSV_PATH", str(DEFAULT_CSV_PATH)))


def _resolve_stale_minutes() -> int:
    return int(os.getenv("STALE_MINUTES", "120"))


def _populate_join_keys(con: sqlite3.Connection) -> None:
    """Populate week, team_code, and opponent_def_code in current_best_lines."""
    from utils.teams import parse_event_id, normalize_team_code
    from engine.season import infer_season

    # Get rows that need join key population
    cur = con.execute("""
        SELECT rowid, event_id, home_team, away_team, season
        FROM current_best_lines
        WHERE event_id IS NOT NULL
    """)
    rows = cur.fetchall()

    updates = []
    for rowid, event_id, home_team, away_team, season in rows:
        try:
            # Parse event_id for date and team info
            game_date, away_parsed, home_parsed = parse_event_id(event_id)

            # Use parsed teams if available, fall back to stored teams
            away_final = normalize_team_code(away_parsed or away_team)
            home_final = normalize_team_code(home_parsed or home_team)

            # Infer week from game_date and season (basic estimation)
            week = None
            if game_date and season:
                try:
                    # Simple week estimation - NFL season typically starts in September
                    import datetime
                    date_obj = datetime.datetime.strptime(game_date, "%Y-%m-%d")
                    # Week 1 typically starts around Sept 5-12
                    # This is a rough approximation - real schedule data would be better
                    if date_obj.month == 9:
                        week = max(1, (date_obj.day - 5) // 7 + 1)
                    elif date_obj.month == 10:
                        week = min(8, (date_obj.day + 25) // 7 + 1)
                    elif date_obj.month == 11:
                        week = min(12, (date_obj.day + 30) // 7 + 1)
                    elif date_obj.month == 12:
                        week = min(18, (date_obj.day + 34) // 7 + 1)
                    elif date_obj.month == 1:  # January playoffs
                        week = min(22, 18 + date_obj.day // 7 + 1)
                except (ValueError, AttributeError):
                    pass

            # For now, we'll set team_code and opponent_def_code to None
            # These will be populated by EdgeEngine logic during edge computation
            updates.append((week, None, None, rowid))

        except Exception as e:
            print(f"     Warning: Failed to parse event_id {event_id}: {e}")
            updates.append((None, None, None, rowid))

    # Batch update the join keys
    if updates:
        con.executemany("""
            UPDATE current_best_lines
            SET week = ?, team_code = ?, opponent_def_code = ?
            WHERE rowid = ?
        """, updates)

        populated_weeks = sum(1 for week, _, _, _ in updates if week is not None)
        print(f"     Populated week for {populated_weeks}/{len(updates)} rows")


def _populate_week_from_schedule(con: sqlite3.Connection) -> None:
    """Populate week column in current_best_lines using schedule data."""
    import os

    sched_csv = os.getenv("SCHEDULE_CSV", "tests/fixtures/schedule_2025_mini.csv")
    if not Path(sched_csv).exists():
        print(f"     Warning: Schedule CSV not found at {sched_csv}")
        return

    try:
        # Load current_best_lines data
        lines_df = pd.read_sql("SELECT * FROM current_best_lines", con)
        if lines_df.empty:
            return

        # Load schedule data
        schedule_df = pd.read_csv(sched_csv)

        # Ensure week column exists in DataFrame
        if "week" not in lines_df.columns:
            lines_df["week"] = pd.NA

        before_missing = lines_df["week"].isna().sum()

        # Populate week using the enhanced helper
        lines_df = populate_week_from_schedule(lines_df, schedule_df)

        # Extract detailed match statistics
        stats = getattr(lines_df, '_week_population_stats', {
            'stage1_count': 0, 'stage2_count': 0, 'total_filled': 0, 'total_rows': len(lines_df)
        })

        stage1_count = stats['stage1_count']
        stage2_count = stats['stage2_count']
        total_filled = stats['total_filled']
        total_rows = stats['total_rows']

        if total_filled > 0:
            # Update the database with new week data
            con.execute("DELETE FROM current_best_lines")  # Clear and rebuild
            lines_df.to_sql("current_best_lines", con, if_exists="append", index=False)
            print(f"     Populated week for {total_filled}/{total_rows} rows (stage1 {stage1_count}, stage2 {stage2_count})")
        else:
            print(f"     No week data populated from schedule (0/{total_rows} rows matched)")

    except Exception as e:
        import traceback
        print(f"     Warning: Schedule week population failed ({e})")
        print(f"     Debug traceback: {traceback.format_exc()}")


def _ensure_columns(con: sqlite3.Connection) -> None:
    cur = con.execute("PRAGMA table_info(odds_csv_raw);")
    cols = {row[1] for row in cur.fetchall()}
    optional_cols = {
        "season": "INTEGER",
        "side": "TEXT",
        "odds": "INTEGER",
        "pos": "TEXT",
        "implied_prob": "REAL",
        "fair_prob": "REAL",
        "overround": "REAL",
        "is_stale": "INTEGER",
        "fair_decimal": "REAL",
        "ingest_source": "TEXT",
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

        history_dir = Path("storage/imports/history")
        history_dir.mkdir(parents=True, exist_ok=True)
        snapshot_name = datetime.now(UTC).strftime("odds_raw_%Y%m%d.csv.gz")
        snapshot_path = history_dir / snapshot_name
        try:
            df.to_csv(snapshot_path, index=False, compression="gzip")
            print(f"     Saved raw snapshot to {snapshot_path}")
        except Exception as err:
            print(f"     Warning: failed to write raw snapshot ({err})")

        raw_rows = len(df)
        df = normalize_long_odds(df, stale_minutes=stale_minutes)
        df["ingest_source"] = "csv"

        if "pos" not in df.columns:
            df["pos"] = None
        pos_missing = df["pos"].isna() | (df["pos"].astype(str).str.strip() == "")
        if pos_missing.any():
            market_lower = df.get("market", "").astype(str).str.lower()
            df.loc[pos_missing & market_lower.str.contains("pass"), "pos"] = "QB"
            df.loc[
                pos_missing & market_lower.str.contains("rush|rushing|carry|attempt"),
                "pos",
            ] = "RB"
            df.loc[
                pos_missing & market_lower.str.contains("rec|receiv|recept|catch"),
                "pos",
            ] = "WR"
            df.loc[
                pos_missing & market_lower.str.contains(r"\\bte\\b|tight[-_\s]?end", regex=True),
                "pos",
            ] = "TE"

        dedupe_cols = [
            "event_id",
            "player",
            "market",
            "book",
            "side",
            "line",
            "updated_at",
        ]
        available_cols = [c for c in dedupe_cols if c in df.columns]
        if available_cols:
            df = dedupe_latest(df, available_cols, sort_col="updated_at")
        deduped_rows = len(df)
        stale_series = pd.to_numeric(df.get("is_stale"), errors="coerce")
        stale_rows = int(stale_series.fillna(0).astype(int).sum()) if not stale_series.empty else 0
        source_counts = df["ingest_source"].value_counts(dropna=False).to_dict()
        print(
            "     Row counts → raw: {raw} | deduped: {deduped} | stale flagged: {stale} | by source: {sources}".format(
                raw=raw_rows,
                deduped=deduped_rows,
                stale=stale_rows,
                sources=source_counts,
            )
        )

        expected_cols = [
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
            "pos",
            "implied_prob",
            "fair_prob",
            "overround",
            "is_stale",
            "fair_decimal",
            "x_used",
            "x_remaining",
            "season",
            "ingest_source",
        ]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = pd.NA
        df = df[expected_cols]

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

        print("     Populating join keys (week, team_code, opponent_def_code) ...")
        _populate_join_keys(con)

        print("     Populating week from schedule data ...")
        _populate_week_from_schedule(con)

        print("[5/5] Done. Rows loaded:", total)
    finally:
        con.close()
    print(f"Total time: {time.perf_counter() - t0:.2f}s")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted."); sys.exit(130)
