#!/usr/bin/env python3
"""
Seed a minimal, self-contained 2025 smoke dataset into storage/odds.db.

What this does:
- Ensures the DB exists at storage/odds.db
- Adds missing columns to `current_best_lines` that the edges pipeline uses: season, week, team_code, pos, is_stale
- Inserts ONE RB odds row for a 2025 KC @ LV game, with week=1, pos='RB', team_code='KC'
- Ensures `defense_ratings` exists and has (season, week, opponent_def_code), then inserts a LV row for 2025 wk1
- Prints a tiny summary so you can confirm it stuck
Then:
- Run:  ./BetThat
- In the UI, select season 2025 → you should see at least one RB record in By Position
"""

import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.environ.get("ODDS_DB", "storage/odds.db")

# Smoke game / rows (choose RB to prove non-QB positions render)
SEASON = 2025
WEEK = 1
HOME = "KC"
AWAY = "LV"
EVENT_ID = "2025-09-07-kc-lv"  # format your EdgeEngine/event parser recognizes
PLAYER = "Isiah Pacheco"
POS = "RB"
MARKET = "player_rush_yds"       # map to one of your supported/normalized markets
LINE = 65.5
OVER = -110
UNDER = -110
BOOK = "draftkings"
UPDATED_AT = datetime.now(timezone.utc).isoformat(timespec="seconds")
TEAM_CODE = HOME                # smoke row from KC side; opponent should be inferred as LV
OPP_DEF_CODE = AWAY             # used in defense_ratings row

def col_exists(conn, table, col):
    cur = conn.execute(f"PRAGMA table_info({table})")
    return any(row[1] == col for row in cur.fetchall())

def table_exists(conn, table):
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (table,)
    )
    return cur.fetchone() is not None

def ensure_table(conn, create_sql):
    # create_sql must be a full CREATE TABLE IF NOT EXISTS ...
    conn.execute(create_sql)

def ensure_column(conn, table, col, decl):
    # add missing column safely
    if not col_exists(conn, table, col):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl}")

def upsert_defense_ratings(conn):
    # Ensure minimal defense_ratings schema with keys needed for join
    ensure_table(
        conn,
        """
        CREATE TABLE IF NOT EXISTS defense_ratings (
            season INTEGER,
            week   INTEGER,
            defteam TEXT,
            pos TEXT,
            score REAL,
            tier TEXT,
            score_adj REAL,
            tier_adj TEXT,
            created_at TEXT
        )
        """,
    )
    # Add missing columns if table already existed with a different shape
    for col, decl in [
        ("season", "INTEGER"),
        ("week", "INTEGER"),
        ("defteam", "TEXT"),
        ("pos", "TEXT"),
        ("score", "REAL"),
        ("tier", "TEXT"),
        ("score_adj", "REAL"),
        ("tier_adj", "TEXT"),
        ("created_at", "TEXT"),
    ]:
        ensure_column(conn, "defense_ratings", col, decl)

    # Insert defense rating for LV (opponent team) for QB_PASS position
    conn.execute(
        """
        INSERT INTO defense_ratings (season, week, defteam, pos, score, tier, score_adj, tier_adj, created_at)
        SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM defense_ratings
            WHERE season=? AND week=? AND defteam=? AND pos=?
        )
        """,
        (SEASON, WEEK, OPP_DEF_CODE, "QB_PASS", 0.6, "neutral", 0.65, "neutral", UPDATED_AT,
         SEASON, WEEK, OPP_DEF_CODE, "QB_PASS"),
    )

def upsert_current_best_lines(conn):
    if not table_exists(conn, "current_best_lines"):
        # Create a minimal superset schema used by edges
        conn.execute(
            """
            CREATE TABLE current_best_lines (
                event_id TEXT,
                player   TEXT,
                market   TEXT,
                line     REAL,
                over_odds  INTEGER,
                under_odds INTEGER,
                book     TEXT,
                updated_at TEXT,

                -- keys used by filters/joins:
                season   INTEGER,
                week     INTEGER,
                team_code TEXT,
                opponent_def_code TEXT, -- optional (EdgeEngine may infer)
                pos      TEXT,
                is_stale INTEGER DEFAULT 0,
                home_team TEXT,
                away_team TEXT
            )
            """
        )
    else:
        # Make sure needed columns exist (no-ops if already present)
        ensure_column(conn, "current_best_lines", "season", "INTEGER")
        ensure_column(conn, "current_best_lines", "week", "INTEGER")
        ensure_column(conn, "current_best_lines", "team_code", "TEXT")
        ensure_column(conn, "current_best_lines", "opponent_def_code", "TEXT")
        ensure_column(conn, "current_best_lines", "pos", "TEXT")
        ensure_column(conn, "current_best_lines", "is_stale", "INTEGER")
        ensure_column(conn, "current_best_lines", "home_team", "TEXT")
        ensure_column(conn, "current_best_lines", "away_team", "TEXT")

    # Insert smoke row (avoid duplicates)
    conn.execute(
        """
        INSERT INTO current_best_lines (
            event_id, player, market, line, over_odds, under_odds, book, updated_at,
            season, week, team_code, opponent_def_code, pos, is_stale, home_team, away_team
        )
        SELECT ?, ?, ?, ?, ?, ?, ?, ?,
               ?, ?, ?, ?, ?, 0, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM current_best_lines
            WHERE season=? AND week=? AND event_id=? AND player=? AND market=? AND book=?
        )
        """,
        (
            EVENT_ID, PLAYER, MARKET, LINE, OVER, UNDER, BOOK, UPDATED_AT,
            SEASON, WEEK, TEAM_CODE, OPP_DEF_CODE, POS, HOME, AWAY,
            SEASON, WEEK, EVENT_ID, PLAYER, MARKET, BOOK,
        ),
    )

def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            upsert_defense_ratings(conn)
            upsert_current_best_lines(conn)

        # Tiny summary
        cur = conn.execute(
            "SELECT season, week, COUNT(*) FROM current_best_lines WHERE season=? GROUP BY season, week",
            (SEASON,),
        )
        cbl = cur.fetchall()

        cur = conn.execute(
            "SELECT season, week, defteam, COUNT(*) FROM defense_ratings WHERE season=? GROUP BY season, week, defteam",
            (SEASON,),
        )
        dr = cur.fetchall()

        print(f"\n[✓] Seeded smoke data into {DB_PATH}")
        print("    current_best_lines (2025):", cbl or "0 rows")
        print("    defense_ratings    (2025):", dr or "0 rows")

        # Optional: nudge for next step
        print(
            "\nNext:\n"
            "  1) DEBUG_EDGE_JOINS=1 ./BetThat\n"
            "  2) In the UI, select season 2025 → By Position (RB) should show at least one row.\n"
            "  3) By Sportsbook should list DraftKings.\n"
        )
    finally:
        conn.close()

if __name__ == "__main__":
    main()