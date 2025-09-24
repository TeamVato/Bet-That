"""Streamlit app for exploring betting edges and odds history."""
from __future__ import annotations

import datetime
import os
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from engine import steam_detector
from engine.odds_math import american_to_decimal
from engine.portfolio import greedy_select, kelly_fraction
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
        try:
            odds_raw = pd.read_sql_query("SELECT * FROM odds_csv_raw", conn)
        except Exception:
            odds_raw = pd.DataFrame()
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
        "odds_raw": odds_raw,
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


def safe_decimal_from_american(val: object) -> float | None:
    if pd.isna(val) or val is None:
        return None
    try:
        return american_to_decimal(int(val))
    except Exception:
        return None


def compute_confidence(row: pd.Series) -> float:
    fresh = 0.0
    stale_val = row.get("is_stale")
    if stale_val in (1, "1"):
        fresh = 0.0
    elif pd.isna(stale_val):
        fresh = 0.8
    else:
        fresh = 1.0

    sigma = row.get("sigma", 55.0)
    try:
        sigma = float(sigma)
    except (TypeError, ValueError):
        sigma = 55.0
    variance_score = 1.0 - min(1.0, max(0.0, (sigma - 25.0) / 60.0))

    p_model = row.get("p_model_shrunk")
    if pd.isna(p_model) or p_model is None:
        p_model = row.get("model_p")
    implied = row.get("implied_prob")
    if pd.isna(implied) or implied is None:
        implied = row.get("fair_prob")
    if pd.isna(p_model) or pd.isna(implied) or p_model is None or implied is None:
        agree = 0.5
    else:
        agree = 1.0 - min(1.0, abs(float(p_model) - float(implied)) * 2.0)

    return float(np.clip(0.5 * fresh + 0.3 * variance_score + 0.2 * agree, 0.0, 1.0))


def build_line_shopping_table(
    odds_raw: pd.DataFrame, row: pd.Series
) -> tuple[pd.DataFrame, dict[str, float]]:
    if odds_raw.empty:
        return pd.DataFrame(), {}
    line_val = row.get("line")
    try:
        line_val = float(line_val)
    except (TypeError, ValueError):
        line_val = None

    working = odds_raw.copy()
    working["line_numeric"] = pd.to_numeric(working.get("line"), errors="coerce")

    mask = (
        (working.get("event_id") == row.get("event_id"))
        & (working.get("player") == row.get("player"))
        & (working.get("market") == row.get("market"))
    )
    if line_val is not None:
        mask &= working["line_numeric"] == line_val

    subset = working.loc[mask, ["book", "side", "odds", "implied_prob", "fair_prob", "updated_at"]]
    if subset.empty:
        return subset, {}

    subset = subset.copy()
    subset["side"] = subset["side"].astype(str).str.title()

    subset["decimal_odds"] = subset["odds"].apply(safe_decimal_from_american)
    subset = subset.sort_values(["side", "decimal_odds"], ascending=[True, False])

    consensus: dict[str, float] = {}
    for side, group in subset.groupby("side"):
        probs = group["fair_prob"].dropna()
        if probs.empty:
            probs = group["implied_prob"].dropna()
        consensus[side] = float(probs.mean()) if not probs.empty else None
        best_decimal = group["decimal_odds"].max()
        subset.loc[group.index, "is_best"] = group["decimal_odds"] == best_decimal
    subset["is_best"] = subset.get("is_best", False).fillna(False)
    subset["best_flag"] = subset["is_best"].map(lambda x: "⭐" if x else "")
    return subset, consensus


def prepare_card_dataframe(
    df: pd.DataFrame, bankroll: float, fraction: float
) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    card = df.copy()

    card["decimal_odds"] = card["odds"].apply(safe_decimal_from_american)
    card["kelly_b"] = card["decimal_odds"].apply(lambda d: None if d is None else d - 1.0)

    def compute_stake(row: pd.Series) -> float:
        b = row.get("kelly_b")
        if b is None:
            return 0.0
        p_val = row.get("p_model_shrunk")
        if pd.isna(p_val) or p_val is None:
            p_val = row.get("model_p")
        if pd.isna(p_val) or p_val is None:
            return 0.0
        return bankroll * kelly_fraction(float(p_val), float(b), fraction)

    card["stake"] = card.apply(compute_stake, axis=1)
    ev_series = pd.to_numeric(card.get("ev_per_dollar"), errors="coerce").fillna(0.0)
    card["expected_value"] = card["stake"] * ev_series
    return card


def export_card(card_df: pd.DataFrame, prefix: str = "card") -> tuple[Path, Path]:
    export_dir = Path("storage/exports")
    export_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    csv_path = export_dir / f"{prefix}_{timestamp}.csv"
    parquet_path = export_dir / f"{prefix}_{timestamp}.parquet"
    card_df.to_csv(csv_path, index=False)
    try:
        card_df.to_parquet(parquet_path, index=False)
    except Exception:
        parquet_path = Path()
    return csv_path, parquet_path


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
odds_raw = data.get("odds_raw", pd.DataFrame())

if props[["season", "def_team"]].isna().any().any():
    st.warning("Some props are missing season or opponent team metadata. Update the CSV for better projections.")

season_options = sorted({int(s) for s in props["season"].dropna().unique()})
selected_seasons = st.sidebar.multiselect("Season filter", season_options, default=season_options)
odds_min, odds_max = st.sidebar.slider("Odds range (American)", -400, 400, (-250, 250))
min_ev = st.sidebar.slider("Minimum EV per $1", -1.0, 1.0, 0.0, step=0.01)
stale_minutes_default = int(os.getenv("STALE_MINUTES", "120"))
hide_stale = st.sidebar.checkbox(
    f"Hide stale lines (> {stale_minutes_default} min)", value=True
)
show_best_only = st.sidebar.checkbox("Show only best-priced edges", value=True)
bankroll = st.sidebar.number_input("Bankroll ($)", min_value=0.0, value=1000.0, step=50.0)
kelly_fraction_input = st.sidebar.slider("Kelly fraction", 0.0, 1.0, 0.25, 0.05)
max_auto = st.sidebar.slider("Max picks (auto card)", 1, 20, 5)
st.sidebar.markdown("### Defense filter")
only_generous = st.sidebar.checkbox("Only vs generous defenses", value=False)

edges_view = edges.copy().reset_index(drop=True)
edges_view["row_id"] = edges_view.index
current_year = datetime.datetime.now().year
fallback_season = current_year if datetime.datetime.now().month >= 8 else current_year - 1
if "season" not in edges_view.columns:
    edges_view["season"] = fallback_season
elif edges_view["season"].isna().all():
    edges_view["season"] = fallback_season
for col in ("def_tier", "def_score"):
    if col not in edges_view.columns:
        edges_view[col] = None
edges_view["def_score"] = pd.to_numeric(edges_view["def_score"], errors="coerce")
if "is_stale" in edges_view.columns:
    edges_view["is_stale"] = pd.to_numeric(edges_view["is_stale"], errors="coerce").astype("Int64")
else:
    edges_view["is_stale"] = pd.Series(pd.NA, index=edges_view.index, dtype="Int64")
edges_view["line"] = pd.to_numeric(edges_view.get("line"), errors="coerce")
edges_view["odds"] = pd.to_numeric(edges_view.get("odds"), errors="coerce")
if "p_model_shrunk" not in edges_view.columns:
    edges_view["p_model_shrunk"] = edges_view.get("model_p")
edges_view["shrink_pct"] = (
    (edges_view.get("model_p") - edges_view.get("p_model_shrunk")).fillna(0.0) * 100.0
)
edges_view["decimal_odds"] = edges_view.get("odds").apply(safe_decimal_from_american)
edges_view["confidence"] = edges_view.apply(compute_confidence, axis=1)

if selected_seasons:
    edges_view = edges_view[edges_view["season"].isin(selected_seasons)]
edges_view = edges_view[(edges_view["odds"] >= odds_min) & (edges_view["odds"] <= odds_max)]
edges_view = edges_view[edges_view["ev_per_dollar"] >= min_ev]
if hide_stale:
    edges_view = edges_view[edges_view["is_stale"].fillna(0) == 0]
if only_generous:
    edges_view = edges_view.loc[edges_view["def_tier"] == "generous"]
if show_best_only:
    edges_view = edges_view.sort_values("ev_per_dollar", ascending=False).drop_duplicates([
        "event_id",
        "player",
        "market",
    ])

st.subheader("Edges (QB/RB/WR props)")
display_cols = [
    "player",
    "market",
    "line",
    "book",
    "odds_side",
    "odds",
    "decimal_odds",
    "model_p",
    "p_model_shrunk",
    "shrink_pct",
    "confidence",
    "ev_per_dollar",
    "kelly_frac",
    "strategy_tag",
]
for col in ["def_tier", "def_score"]:
    if col in edges_view.columns and col not in display_cols:
        display_cols.append(col)
for col in ("implied_prob", "fair_prob", "overround", "is_stale"):
    if col in edges_view.columns and col not in display_cols:
        display_cols.append(col)
table_data = edges_view[display_cols].copy()
for prob_col in ("implied_prob", "fair_prob", "overround"):
    if prob_col in table_data.columns:
        table_data[prob_col] = pd.to_numeric(table_data[prob_col], errors="coerce")
round_map = {
    "model_p": 3,
    "p_model_shrunk": 3,
    "ev_per_dollar": 3,
    "kelly_frac": 3,
    "confidence": 3,
}
for prob_col in ("implied_prob", "fair_prob", "overround"):
    if prob_col in table_data.columns:
        round_map[prob_col] = 3
if "def_score" in table_data.columns:
    round_map["def_score"] = 3
table_data = table_data.round(round_map)

editor_df = table_data.copy()
editor_df.insert(0, "Select", False)
editor_df.index = edges_view["row_id"]

column_config = {
    "decimal_odds": st.column_config.NumberColumn(
        "decimal_odds",
        help="Sportsbook decimal odds derived from the American price.",
        format="%.3f",
    ),
    "confidence": st.column_config.ProgressColumn(
        "Confidence",
        help="Blend of freshness, uncertainty and market agreement (higher is better).",
        min_value=0.0,
        max_value=1.0,
        format="%.0f%%",
    ),
    "shrink_pct": st.column_config.NumberColumn(
        "Shrink Δ (bps)",
        help="Difference between raw and market-shrunk probabilities (basis points).",
        format="%.1f",
    ),
}
if "def_score" in table_data.columns:
    column_config["def_score"] = st.column_config.NumberColumn(
        "def_score",
        help="Higher means more generous defense over recent games; 0 = league average.",
        format="%.3f",
    )

editor_result = st.data_editor(
    editor_df,
    column_config=column_config,
    hide_index=True,
    num_rows="dynamic",
    use_container_width=True,
    key="edges_editor",
)

selected_ids = editor_result.index[editor_result["Select"] == True].tolist()
selected_edges = edges_view[edges_view["row_id"].isin(selected_ids)]

if st.button("Export today's picks"):
    export_path = export_picks(edges_view)
    append_bets_log(database_path, edges_view)
    st.success(f"Exported {len(edges_view)} picks to {export_path}")

st.subheader("My Card")
card_df = prepare_card_dataframe(selected_edges, bankroll, kelly_fraction_input)
if card_df.empty:
    st.info("Select rows in the table above to build your card.")
else:
    summary_cols = [
        "player",
        "market",
        "line",
        "book",
        "odds_side",
        "decimal_odds",
        "p_model_shrunk",
        "stake",
        "expected_value",
    ]
    st.metric(
        "Total Stake",
        f"${card_df['stake'].sum():,.2f}",
        help="Sum of fractional Kelly stakes across selected edges.",
    )
    st.dataframe(card_df[summary_cols].round(3))
    if st.button("Export selected card"):
        csv_path, parquet_path = export_card(card_df, prefix="card_selected")
        st.success(f"Exported card to {csv_path}")

if st.sidebar.button("Auto-build card") and not edges_view.empty:
    auto_source = edges_view.copy()
    auto_source["EV"] = auto_source["ev_per_dollar"]
    auto_selected = greedy_select(auto_source, max_n=max_auto)
    st.session_state["auto_card"] = prepare_card_dataframe(
        auto_selected, bankroll, kelly_fraction_input
    )

auto_card = st.session_state.get("auto_card")
if isinstance(auto_card, pd.DataFrame) and not auto_card.empty:
    st.subheader("Auto-built card suggestion")
    summary_cols = [
        "player",
        "market",
        "line",
        "book",
        "odds_side",
        "decimal_odds",
        "p_model_shrunk",
        "stake",
        "expected_value",
    ]
    st.metric(
        "Auto Card Stake",
        f"${auto_card['stake'].sum():,.2f}",
        help="Total stake recommended by the greedy selector.",
    )
    st.dataframe(auto_card[summary_cols].round(3))
    if st.button("Export auto card"):
        csv_path, parquet_path = export_card(auto_card, prefix="card_auto")
        st.success(f"Exported auto card to {csv_path}")

st.subheader("Line shopping across books")
if odds_raw.empty:
    st.info("Run the odds poller/importer to populate raw odds snapshots for line shopping.")
else:
    st.caption("Expand a row to inspect every book for that player prop. ⭐ marks the best available price per side.")
    max_rows = min(len(edges_view), 20)
    for _, row in edges_view.head(max_rows).iterrows():
        view, consensus = build_line_shopping_table(odds_raw, row)
        if view.empty:
            continue
        label = f"{row.get('player')} · {row.get('market')} · {row.get('line')} ({row.get('book')})"
        with st.expander(label):
            consensus_parts = []
            for side, val in consensus.items():
                if val is None:
                    continue
                consensus_parts.append(f"{side}: {val*100:.1f}%")
            if consensus_parts:
                st.caption("Consensus fair probability → " + " | ".join(consensus_parts))
            display_cols = [
                "best_flag",
                "book",
                "side",
                "odds",
                "decimal_odds",
                "implied_prob",
                "fair_prob",
                "updated_at",
            ]
            st.dataframe(view[display_cols])
    if not best_lines.empty:
        st.markdown("#### Current best lines summary")
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
