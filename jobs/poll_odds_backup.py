from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests

from utils.odds import american_to_decimal, implied_from_decimal, proportional_devig_two_way

DB = "storage/odds.db"
USAGE_JSON = "storage/odds_api_usage.json"


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def get_keys() -> List[str]:
    val = os.getenv("ODDS_API_KEYS", "").strip()
    return [k.strip() for k in val.split(",") if k.strip()]


def ensure_usage_table(con: sqlite3.Connection):
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS odds_api_usage (
          key TEXT PRIMARY KEY,
          last_used TEXT,
          req_today INT DEFAULT 0,
          req_month INT DEFAULT 0,
          last_remaining INT,
          disabled INT DEFAULT 0,
          disabled_until TEXT
        );
        """
    )


def load_usage_json() -> Dict[str, Any]:
    try:
        with open(USAGE_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"keys": {}}


def save_usage_json(data: Dict[str, Any]):
    os.makedirs(os.path.dirname(USAGE_JSON), exist_ok=True)
    with open(USAGE_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def select_key(con: sqlite3.Connection, keys: List[str]) -> Optional[str]:
    if not keys:
        return None
    rows = {k: {"disabled": 0, "last_remaining": 0, "req_month": 0} for k in keys}
    placeholders = ",".join(["?"] * len(keys))
    cur = con.execute(
        f"SELECT key, disabled, last_remaining, req_month FROM odds_api_usage WHERE key IN ({placeholders})",
        keys,
    )
    for k, dis, rem, mon in cur.fetchall():
        rows[k] = {"disabled": dis or 0, "last_remaining": rem or 0, "req_month": mon or 0}
    candidates = [k for k in keys if rows.get(k, {}).get("disabled", 0) == 0]
    if not candidates:
        return None
    candidates.sort(key=lambda k: (-rows[k]["last_remaining"], rows[k]["req_month"], k))
    return candidates[0]


def record_usage(con: sqlite3.Connection, key: str, remaining: Optional[int]):
    con.execute(
        """
        INSERT INTO odds_api_usage(key,last_used,req_today,req_month,last_remaining,disabled)
        VALUES(?,?,?,?,?,0)
        ON CONFLICT(key) DO UPDATE SET
          last_used=excluded.last_used,
          req_today=COALESCE(odds_api_usage.req_today,0)+1,
          req_month=COALESCE(odds_api_usage.req_month,0)+1,
          last_remaining=?
        """,
        (key, now_utc().isoformat(), 1, 1, remaining, remaining),
    )


def fetch_markets(
    key: str, sport_key: str, region: str, markets: str, bookmakers: str, timeout: int = 15
) -> Dict[str, Any]:
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {"apiKey": key, "regions": region, "markets": markets, "bookmakers": bookmakers}
    r = requests.get(url, params=params, timeout=timeout)
    if r.status_code in (401, 403, 429):
        raise RuntimeError(f"auth_or_quota: {r.status_code} {r.text}")
    r.raise_for_status()
    return {"json": r.json(), "headers": r.headers}


def normalize_rows(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    now = now_utc().isoformat()
    for ev in payload.get("json", []):
        event_id = ev.get("id")
        commence_time = ev.get("commence_time")
        home_team = ev.get("home_team")
        away_team = ev.get("away_team")
        for bk in ev.get("bookmakers", []):
            book = bk.get("key")
            updated_at = bk.get("last_update") or now
            for mk in bk.get("markets", []):
                market = mk.get("key")
                for out in mk.get("outcomes", []):
                    side = out.get("name")  # Over/Under or selection name
                    odds_american = out.get("price")
                    line = out.get("point")
                    player = out.get("description") or out.get("player")
                    rows.append(
                        dict(
                            event_id=event_id,
                            commence_time=commence_time,
                            home_team=home_team,
                            away_team=away_team,
                            player=player,
                            market=market,
                            line=line,
                            side=side,
                            odds=odds_american,
                            book=book,
                            updated_at=updated_at,
                        )
                    )
    return rows


def ensure_odds_table(con: sqlite3.Connection) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS odds_csv_raw (
            event_id TEXT,
            commence_time TEXT,
            home_team TEXT,
            away_team TEXT,
            player TEXT,
            market TEXT,
            line REAL,
            side TEXT,
            odds INT,
            pos TEXT,
            book TEXT,
            updated_at TEXT,
            ingest_source TEXT
        )
        """
    )


def upsert_rows(
    con: sqlite3.Connection,
    rows: List[Dict[str, Any]],
    *,
    stale_minutes: Optional[int] = None,
) -> pd.DataFrame | None:
    from engine.odds_normalizer import normalize_long_odds

    ensure_odds_table(con)
    if not rows:
        return None

    df = pd.DataFrame(rows)
    if df.empty:
        return None

    minutes = stale_minutes if stale_minutes is not None else int(os.getenv("STALE_MINUTES", "120"))
    normalized = normalize_long_odds(
        df,
        stale_minutes=minutes,
        now_ts=pd.Timestamp(now_utc()),
    )
    if normalized is None:
        normalized = df
    normalized["ingest_source"] = "odds_api"

    if "pos" not in normalized.columns:
        normalized["pos"] = None
    pos_missing = normalized["pos"].isna() | (normalized["pos"].astype(str).str.strip() == "")
    if pos_missing.any():
        market_lower = normalized.get("market", "").astype(str).str.lower()
        normalized.loc[pos_missing & market_lower.str.contains("pass"), "pos"] = "QB"
        normalized.loc[
            pos_missing & market_lower.str.contains("rush|rushing|carry|attempt"),
            "pos",
        ] = "RB"
        normalized.loc[
            pos_missing & market_lower.str.contains("rec|receiv|recept|catch"),
            "pos",
        ] = "WR"
        normalized.loc[
            pos_missing & market_lower.str.contains(r"\\bte\\b|tight[-_\s]?end", regex=True),
            "pos",
        ] = "TE"

    raw_rows = len(normalized)
    dedupe_cols = [
        "event_id",
        "player",
        "market",
        "book",
        "side",
        "line",
        "updated_at",
    ]
    available_cols = [c for c in dedupe_cols if c in normalized.columns]
    if available_cols:
        normalized = normalized.sort_values("updated_at").drop_duplicates(
            available_cols, keep="last"
        )
    deduped_rows = len(normalized)
    stale_rows = int(
        normalized.get("is_stale", pd.Series(dtype="float64")).fillna(0).astype(int).sum()
    )
    source_counts = normalized["ingest_source"].value_counts(dropna=False).to_dict()
    print(
        "Upsert rows → raw: {raw} | deduped: {deduped} | stale flagged: {stale} | by source: {sources}".format(
            raw=raw_rows,
            deduped=deduped_rows,
            stale=stale_rows,
            sources=source_counts,
        )
    )

    existing = {row[1] for row in con.execute("PRAGMA table_info(odds_csv_raw)")}
    for col in normalized.columns:
        if col not in existing:
            if col in {"line"}:
                col_type = "REAL"
            elif col in {"odds", "x_used", "x_remaining", "season", "is_stale"}:
                col_type = "INT"
            elif col in {"implied_prob", "fair_prob", "overround", "fair_decimal"}:
                col_type = "REAL"
            else:
                col_type = "TEXT"
            con.execute(f"ALTER TABLE odds_csv_raw ADD COLUMN {col} {col_type}")

    cols = normalized.columns.tolist()
    placeholders = ",".join(["?"] * len(cols))
    delete_sql = (
        "DELETE FROM odds_csv_raw WHERE event_id=? AND market=? AND book=? AND side=? "
        "AND ((line IS NULL AND ? IS NULL) OR line=?)"
    )
    for row in normalized.itertuples(index=False):
        key = (row.event_id, row.market, row.book, row.side, row.line, row.line)
        con.execute(delete_sql, key)
        con.execute(
            f"INSERT INTO odds_csv_raw ({','.join(cols)}) VALUES ({placeholders})",
            tuple(getattr(row, col) for col in cols),
        )
    return normalized


def ensure_closing_tables(con: sqlite3.Connection) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS closing_lines (
          closing_id INTEGER PRIMARY KEY AUTOINCREMENT,
          event_id TEXT NOT NULL,
          market TEXT NOT NULL,
          side TEXT NOT NULL,
          line REAL,
          book TEXT NOT NULL,
          odds_decimal REAL,
          odds_american INTEGER,
          implied_prob REAL,
          overround REAL,
          fair_prob_close REAL,
          ts_close TIMESTAMP NOT NULL,
          is_primary INTEGER DEFAULT 0,
          ingest_source TEXT,
          source_run_id TEXT,
          raw_payload_hash TEXT
        );
        """
    )
    con.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_closing_lines_key
          ON closing_lines(event_id, market, side, line, book);
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS clv_log (
          clv_id INTEGER PRIMARY KEY AUTOINCREMENT,
          edge_id TEXT,
          bet_id TEXT,
          event_id TEXT NOT NULL,
          market TEXT NOT NULL,
          side TEXT NOT NULL,
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
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    con.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_clv_log_event_market ON clv_log(event_id, market, side);
        """
    )


def _safe_decimal(odds: Any) -> float | None:
    try:
        if odds is None or pd.isna(odds):
            return None
        return float(american_to_decimal(int(odds)))
    except Exception:
        return None


def _safe_implied(decimal_odds: float | None) -> float | None:
    try:
        if decimal_odds is None or pd.isna(decimal_odds):
            return None
        return float(implied_from_decimal(float(decimal_odds)))
    except Exception:
        return None


def _normalize_side(value: Any) -> str:
    text = (str(value) if value is not None else "").strip().lower()
    if "over" in text:
        return "over"
    if "under" in text:
        return "under"
    return text


def _coerce_optional(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        return value
    return value


def write_closing_snapshot(
    con: sqlite3.Connection,
    normalized: pd.DataFrame | None,
    *,
    ts_run: dt.datetime,
    primary_book: str,
    source_label: str = "odds_api",
    run_id: str | None = None,
) -> Tuple[int, float]:
    if normalized is None or normalized.empty:
        return 0, 0.0

    working = normalized.copy()
    required_cols = {"event_id", "market", "side", "book", "updated_at"}
    if not required_cols.issubset(working.columns):
        return 0, 0.0

    working = working.dropna(subset=list(required_cols))
    if working.empty:
        return 0, 0.0

    working["updated_at"] = pd.to_datetime(working["updated_at"], errors="coerce", utc=True)
    working = working[working["updated_at"].notna()]
    if working.empty:
        return 0, 0.0

    if "commence_time" in working.columns:
        working["commence_ts"] = pd.to_datetime(working["commence_time"], errors="coerce", utc=True)
    else:
        working["commence_ts"] = pd.NaT

    key_cols = ["event_id", "market", "side", "line", "book"]
    selections: list[pd.Series] = []
    for _, group in working.groupby(key_cols, dropna=False):
        group = group.sort_values("updated_at")
        commence = group["commence_ts"].dropna().max()
        choice = None
        if pd.notna(commence):
            before = group[group["updated_at"] <= commence]
            if not before.empty:
                choice = before.iloc[-1]
            else:
                fallback_cutoff = commence - pd.Timedelta(minutes=2)
                fallback = group[group["updated_at"] <= fallback_cutoff]
                if not fallback.empty:
                    choice = fallback.iloc[-1]
        if choice is None:
            choice = group.iloc[-1]
        selections.append(choice)

    if not selections:
        return 0, 0.0

    closing_df = pd.DataFrame(selections).reset_index(drop=True)
    closing_df["line"] = pd.to_numeric(closing_df.get("line"), errors="coerce")
    closing_df["odds"] = pd.to_numeric(closing_df.get("odds"), errors="coerce")
    closing_df["odds_decimal"] = closing_df["odds"].apply(_safe_decimal)
    closing_df["implied_prob"] = closing_df["odds_decimal"].apply(_safe_implied)
    closing_df["side_norm"] = closing_df["side"].apply(_normalize_side)
    closing_df["fair_prob_close"] = pd.NA
    closing_df["overround"] = pd.NA

    grouped = closing_df.groupby(["event_id", "market", "line", "book"], dropna=False)
    for _, group in grouped:
        over_idx = group[group["side_norm"] == "over"].index
        under_idx = group[group["side_norm"] == "under"].index
        if len(over_idx) == 1 and len(under_idx) == 1:
            over_prob = closing_df.loc[over_idx[0], "implied_prob"]
            under_prob = closing_df.loc[under_idx[0], "implied_prob"]
            if pd.notna(over_prob) and pd.notna(under_prob) and over_prob >= 0 and under_prob >= 0:
                fair_over, fair_under = proportional_devig_two_way(
                    float(over_prob), float(under_prob)
                )
                overround = float(over_prob + under_prob)
                closing_df.loc[over_idx[0], "fair_prob_close"] = fair_over
                closing_df.loc[under_idx[0], "fair_prob_close"] = fair_under
                closing_df.loc[[over_idx[0], under_idx[0]], "overround"] = overround

    coverage = 0.0
    pair_counts = grouped["side_norm"].nunique()
    if len(pair_counts) > 0:
        coverage = float((pair_counts >= 2).sum() / len(pair_counts))

    ensure_closing_tables(con)

    delete_sql = "DELETE FROM closing_lines WHERE event_id=? AND market=? AND side=? AND ((line IS NULL AND ? IS NULL) OR line=?) AND book=?"
    insert_sql = """
        INSERT INTO closing_lines (
            event_id, market, side, line, book,
            odds_decimal, odds_american, implied_prob, overround,
            fair_prob_close, ts_close, is_primary,
            ingest_source, source_run_id, raw_payload_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

    run_identifier = run_id or f"poll/{ts_run.isoformat()}"
    primary_book_normalized = (primary_book or "").strip().lower()
    inserted = 0

    for row in closing_df.to_dict("records"):
        odds_american = row.get("odds")
        if pd.notna(odds_american):
            try:
                odds_american = int(odds_american)
            except Exception:
                odds_american = None
        else:
            odds_american = None

        ts_close = row.get("updated_at")
        if isinstance(ts_close, pd.Timestamp):
            ts_close = ts_close.to_pydatetime().isoformat()

        line_value = _coerce_optional(row.get("line"))
        odds_decimal = _coerce_optional(row.get("odds_decimal"))
        implied_prob = _coerce_optional(row.get("implied_prob"))
        overround_val = _coerce_optional(row.get("overround"))
        fair_prob_close = _coerce_optional(row.get("fair_prob_close"))

        is_primary = (
            1
            if primary_book_normalized
            and str(row.get("book", "")).strip().lower() == primary_book_normalized
            else 0
        )
        payload_hash = hashlib.sha256(
            json.dumps(row, default=str, sort_keys=True).encode()
        ).hexdigest()

        delete_params = (
            row.get("event_id"),
            row.get("market"),
            row.get("side"),
            line_value,
            line_value,
            row.get("book"),
        )
        params = (
            row.get("event_id"),
            row.get("market"),
            row.get("side"),
            line_value,
            row.get("book"),
            odds_decimal,
            odds_american,
            implied_prob,
            overround_val,
            fair_prob_close,
            ts_close,
            is_primary,
            source_label,
            run_identifier,
            payload_hash,
        )
        con.execute(delete_sql, delete_params)
        con.execute(insert_sql, params)
        inserted += 1

    return inserted, coverage

    existing = {r[1] for r in con.execute("PRAGMA table_info(odds_csv_raw)")}
    for col in normalized.columns:
        if col not in existing:
            if col in {"line"}:
                col_type = "REAL"
            elif col in {"odds", "x_used", "x_remaining", "season", "is_stale"}:
                col_type = "INT"
            elif col in {"implied_prob", "fair_prob", "overround", "fair_decimal"}:
                col_type = "REAL"
            else:
                col_type = "TEXT"
            con.execute(f"ALTER TABLE odds_csv_raw ADD COLUMN {col} {col_type}")

    cols = normalized.columns.tolist()
    placeholders = ",".join(["?"] * len(cols))
    delete_sql = (
        "DELETE FROM odds_csv_raw WHERE event_id=? AND market=? AND book=? AND side=? "
        "AND ((line IS NULL AND ? IS NULL) OR line=?)"
    )
    for row in normalized.itertuples(index=False):
        key = (row.event_id, row.market, row.book, row.side, row.line, row.line)
        con.execute(delete_sql, key)
        con.execute(
            f"INSERT INTO odds_csv_raw ({','.join(cols)}) VALUES ({placeholders})",
            tuple(getattr(row, col) for col in cols),
        )
    return normalized


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="Poll once and exit")
    ap.add_argument("--interval", type=int, default=0, help="Poll every N seconds (dev only)")
    ap.add_argument("--sport", default="nfl")
    ap.add_argument("--region", default=os.getenv("ODDS_REGION", "us"))
    ap.add_argument("--markets", default=os.getenv("ODDS_MARKETS", "player_props"))
    ap.add_argument(
        "--bookmakers", default=os.getenv("ODDS_BOOKMAKERS", "draftkings,fanduel,betmgm")
    )
    ap.add_argument("--timeout", type=int, default=int(os.getenv("ODDS_TIMEOUT", "15")))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--primary-book", default=os.getenv("CLOSING_PRIMARY_BOOK", "dk"))
    args = ap.parse_args()

    sport_key = "americanfootball_nfl"  # NFL only

    keys = get_keys()
    if not keys:
        raise SystemExit("Set ODDS_API_KEYS='k1,k2,...'")

    os.makedirs("storage", exist_ok=True)
    con = sqlite3.connect(DB, timeout=10.0, isolation_level=None)
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA busy_timeout=10000;")
    ensure_usage_table(con)

    def do_once(run_tag: str) -> Tuple[int, int, float]:
        key = select_key(con, keys)
        if not key:
            raise SystemExit("No enabled key available")
        if args.dry_run:
            print(f"Would poll with key: {key} markets={args.markets} books={args.bookmakers}")
            return 0, 0, 0.0
        tries = 0
        while True:
            tries += 1
            try:
                payload = fetch_markets(
                    key, sport_key, args.region, args.markets, args.bookmakers, args.timeout
                )
                headers = payload.get("headers") or {}
                remaining = headers.get("x-requests-remaining")
                try:
                    remaining = int(remaining)
                except Exception:
                    remaining = None
                record_usage(con, key, remaining)
                rows = normalize_rows(payload)
                normalized = upsert_rows(con, rows)
                ts_run = now_utc()
                inserted, coverage = write_closing_snapshot(
                    con,
                    normalized,
                    ts_run=ts_run,
                    primary_book=args.primary_book,
                    run_id=run_tag,
                )
                print(
                    "Fetched {count} outcomes. Closing rows={inserted} coverage={coverage:.1%}".format(
                        count=len(rows), inserted=inserted, coverage=coverage
                    )
                )
                return len(rows), inserted, coverage
            except Exception as e:
                msg = str(e).lower()
                if "auth_or_quota" in msg:
                    until = (now_utc() + dt.timedelta(hours=24)).isoformat()
                    con.execute(
                        """
                        INSERT INTO odds_api_usage(key,disabled,disabled_until)
                        VALUES(?,?,?)
                        ON CONFLICT(key) DO UPDATE SET disabled=1, disabled_until=?
                        """,
                        (key, 1, until, until),
                    )
                    key = select_key(con, keys)
                    if not key:
                        raise
                    continue
                if tries < 3:
                    time.sleep(2 ** (tries - 1))
                    continue
                raise

    run_start = now_utc()
    banner = (
        "=== Bet-That Poll Start @ {ts} | markets={markets} | region={region} | books={books} ==="
    ).format(
        ts=run_start.isoformat(),
        markets=args.markets,
        region=args.region,
        books=args.bookmakers,
    )
    print(banner)

    run_tag_base = f"poll::{run_start.isoformat()}"

    if args.once or args.interval <= 0:
        fetched, closing_rows, coverage = do_once(run_tag_base)
        run_end = now_utc()
        print(
            "=== Bet-That Poll Complete @ {ts} | fetched={fetched} | closing_rows={closing} | coverage={coverage:.1%} ===".format(
                ts=run_end.isoformat(),
                fetched=fetched,
                closing=closing_rows,
                coverage=coverage,
            )
        )
    else:
        iteration = 0
        while True:
            iteration += 1
            fetched, closing_rows, coverage = do_once(f"{run_tag_base}#{iteration}")
            loop_end = now_utc()
            print(
                "=== Bet-That Poll Loop @ {ts} | iter={iter} | fetched={fetched} | closing_rows={closing} | coverage={coverage:.1%} ===".format(
                    ts=loop_end.isoformat(),
                    iter=iteration,
                    fetched=fetched,
                    closing=closing_rows,
                    coverage=coverage,
                )
            )
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
