from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sqlite3
import time
from typing import Any, Dict, List, Optional

import requests

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
            book TEXT,
            updated_at TEXT
        )
        """
    )


def upsert_rows(con: sqlite3.Connection, rows: List[Dict[str, Any]]):
    # Minimal upsert: append raw rows; importer still provides full normalization
    ensure_odds_table(con)
    # Add new columns if missing
    existing = {r[1] for r in con.execute("PRAGMA table_info(odds_csv_raw)")}
    needed = {
        "season": "INT",
        "implied_prob": "REAL",
        "overround": "REAL",
        "fair_prob": "REAL",
        "is_stale": "INTEGER",
    }
    for col, typ in needed.items():
        if col not in existing:
            con.execute(f"ALTER TABLE odds_csv_raw ADD COLUMN {col} {typ}")
    # Insert
    if not rows:
        return
    cols = [
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
    ]
    placeholders = ",".join(["?"] * len(cols))
    con.executemany(
        f"INSERT INTO odds_csv_raw ({','.join(cols)}) VALUES ({placeholders})",
        [tuple(r.get(c) for c in cols) for r in rows],
    )


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

    def do_once():
        key = select_key(con, keys)
        if not key:
            raise SystemExit("No enabled key available")
        if args.dry_run:
            print(
                f"Would poll with key: {key} markets={args.markets} books={args.bookmakers}"
            )
            return
        tries = 0
        while True:
            tries += 1
            try:
                payload = fetch_markets(
                    key, sport_key, args.region, args.markets, args.bookmakers, args.timeout
                )
                remaining = payload["headers"].get("x-requests-remaining")
                try:
                    remaining = int(remaining)
                except Exception:
                    remaining = None
                record_usage(con, key, remaining)
                rows = normalize_rows(payload)
                upsert_rows(con, rows)
                print(f"Fetched {len(rows)} outcomes.")
                return
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

    if args.once or args.interval <= 0:
        do_once()
    else:
        while True:
            do_once()
            time.sleep(args.interval)


if __name__ == "__main__":
    main()

