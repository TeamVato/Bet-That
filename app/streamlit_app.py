"""Streamlit app for exploring betting edges and odds history."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from engine import steam_detector
from utils.time import utc_now_iso


def get_database_path() -> Path:
    load_dotenv()
    url = os.getenv("DATABASE_URL", "sqlite:///storage/odds.db")
    from db.migrate import parse_database_url

    return parse_database_url(url)


@st.cache_data(ttl=60)
def load_tables(database_path: Path) -> dict[str, pd.DataFrame]:
    with sqlite3.connect(database_path) as conn:
        edges = pd.read_sql_query("SELECT * FROM edges", conn)
        props = pd.read_sql_query("SELECT * FROM qb_props_odds", conn)
        projections = pd.read_sql_query("SELECT * FROM projections_qb", conn)
        best_lines = pd.read_sql_query("SELECT * FROM current_best_lines", conn)
        snapshots = pd.read_sql_query("SELECT * FROM odds_snapshots", conn)
    edges = edges.merge(
        props[["event_id", "player", "season", "def_team"]].drop_duplicates(),
        on=["event_id", "player"],
        how="left",
    )
    return {
        "edges": edges,
        "props": props,
        "projections": projections,
        "best_lines": best_lines,
        "snapshots": snapshots,
    }


def export_picks(df: pd.DataFrame) -> Path:
    export_dir = Path("storage/exports")
    export_dir.mkdir(parents=True, exist_ok=True)
    path = export_dir / "picks_latest.csv"
    df.to_csv(path, index=False)
    return path


def append_bets_log(database_path: Path, picks_df: pd.DataFrame) -> None:
    if picks_df.empty:
        return
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        for _, row in picks_df.iterrows():
            cursor.execute(
                """
                INSERT INTO bets_log (
                    placed_at, event_id, book, player, market, line, odds_side, odds,
                    stake, model_p, ev_per_dollar, kelly_frac, strategy_tag, note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    utc_now_iso(),
                    row.get("event_id"),
                    row.get("book"),
                    row.get("player"),
                    row.get("market"),
                    row.get("line"),
                    row.get("odds_side"),
                    row.get("odds"),
                    0.0,
                    row.get("model_p"),
                    row.get("ev_per_dollar"),
                    row.get("kelly_frac"),
                    row.get("strategy_tag"),
                    "Exported from Streamlit",
                ),
            )
        conn.commit()


st.set_page_config(page_title="NFL Edge Finder", layout="wide")
st.title("🏈 NFL Betting Edge Finder")

try:
    database_path = get_database_path()
except Exception as exc:
    st.error(f"Failed to resolve DATABASE_URL: {exc}")
    st.stop()

if not database_path.exists():
    st.warning("Database not found. Run `python db/migrate.py` and the jobs first.")
    st.stop()

data = load_tables(database_path)
edges = data["edges"]
props = data["props"]
projections = data["projections"]
best_lines = data["best_lines"]
snapshots = data["snapshots"]

if props[["season", "def_team"]].isna().any().any():
    st.warning("Some props are missing season or opponent team metadata. Update the CSV for better projections.")

season_options = sorted({int(s) for s in props["season"].dropna().unique()})
selected_seasons = st.sidebar.multiselect("Season filter", season_options, default=season_options)
odds_min, odds_max = st.sidebar.slider("Odds range (American)", -400, 400, (-250, 250))
min_ev = st.sidebar.slider("Minimum EV per $1", -1.0, 1.0, 0.0, step=0.01)
show_best_only = st.sidebar.checkbox("Show only best-priced edges", value=True)

edges_view = edges.copy()
if selected_seasons:
    edges_view = edges_view[edges_view["season"].isin(selected_seasons)]
edges_view = edges_view[(edges_view["odds"] >= odds_min) & (edges_view["odds"] <= odds_max)]
edges_view = edges_view[edges_view["ev_per_dollar"] >= min_ev]
if show_best_only:
    edges_view = edges_view.sort_values("ev_per_dollar", ascending=False).drop_duplicates(["event_id", "player", "market"])

st.subheader("Edges (QB props)")
st.dataframe(edges_view[[
    "player",
    "market",
    "line",
    "book",
    "odds_side",
    "odds",
    "model_p",
    "ev_per_dollar",
    "kelly_frac",
    "strategy_tag",
]].round({"model_p": 3, "ev_per_dollar": 3, "kelly_frac": 3}))

if st.button("Export today's picks"):
    export_path = export_picks(edges_view)
    append_bets_log(database_path, edges_view)
    st.success(f"Exported {len(edges_view)} picks to {export_path}")

st.subheader("Line shopping across books")
if best_lines.empty:
    st.info("Run the odds poller to populate current best lines.")
else:
    st.dataframe(best_lines)

st.subheader("Steam alerts")
if snapshots.empty:
    st.info("Steam alerts require at least two odds snapshots.")
else:
    alerts = steam_detector.detect_steam(snapshots)
    if alerts.empty:
        st.success("No steam detected in the most recent snapshots.")
    else:
        st.dataframe(alerts)

st.caption("Exports are saved under storage/exports/. Use jobs/export_bi.py for BI snapshots.")
