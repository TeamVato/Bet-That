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
        optional_tables = {
            "scheme": "team_week_scheme",
            "weather": "weather",
            "context_notes": "context_notes",
            "wr_cb": "wr_cb_public",
            "injuries": "injuries",
        }
        extras: dict[str, pd.DataFrame] = {}
        for key, table in optional_tables.items():
            try:
                extras[key] = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            except Exception:
                extras[key] = pd.DataFrame()
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
        **extras,
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


def ensure_context_notes_table(database_path: Path) -> None:
    with sqlite3.connect(database_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS context_notes (
                event_id TEXT,
                note TEXT,
                source_url TEXT,
                created_at TEXT
            )
            """
        )


def fetch_context_notes(database_path: Path, event_id: object) -> pd.DataFrame:
    if event_id is None or pd.isna(event_id):
        return pd.DataFrame()
    ensure_context_notes_table(database_path)
    with sqlite3.connect(database_path) as conn:
        notes = pd.read_sql_query(
            "SELECT event_id, note, source_url, created_at FROM context_notes WHERE event_id = ? ORDER BY datetime(created_at) DESC",
            conn,
            params=(str(event_id),),
        )
    return notes


def add_context_note(database_path: Path, event_id: object, note: str, source_url: str) -> None:
    ensure_context_notes_table(database_path)
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    with sqlite3.connect(database_path) as conn:
        conn.execute(
            "INSERT INTO context_notes (event_id, note, source_url, created_at) VALUES (?, ?, ?, ?)",
            (str(event_id), note, source_url or None, timestamp),
        )


def render_matchup_expander(
    row: pd.Series,
    data: dict[str, pd.DataFrame],
    database_path: Path,
) -> None:
    event_id = row.get("event_id")
    player = row.get("player") or "Unknown player"
    market = row.get("market") or "Unknown market"
    label = f"Matchup: {player} · {market}"

    scheme_df = data.get("scheme", pd.DataFrame())
    weather_df = data.get("weather", pd.DataFrame())
    injuries_df = data.get("injuries", pd.DataFrame())
    wr_cb_df = data.get("wr_cb", pd.DataFrame())

    def_tier = row.get("def_tier") or "n/a"
    def_score = row.get("def_score")
    def_score_display = f"{def_score:.2f}" if isinstance(def_score, (int, float)) and not np.isnan(def_score) else "n/a"

    with st.expander(label, expanded=False):
        def_col, scheme_col, wr_cb_col, inj_col = st.columns(4)

        # Defense card
        def_metrics = [
            f"Tier: **{def_tier}**" if def_tier != "n/a" else "Tier: n/a",
            f"Score: **{def_score_display}**",
        ]
        if "is_stale" in row and not pd.isna(row.get("is_stale")):
            freshness = "Stale" if int(row.get("is_stale", 0)) else "Fresh"
            def_metrics.append(f"Status: **{freshness}**")
        def_col.markdown("**Defense**")
        def_col.markdown("\n".join(f"- {metric}" for metric in def_metrics))

        # Scheme card placeholder (requires team_week_scheme ingestion)
        scheme_col.markdown("**Scheme & Tendencies**")
        scheme_info = "n/a"
        if not scheme_df.empty:
            offense_team = row.get("team") or row.get("team_code")
            season = row.get("season")
            week = row.get("week")
            if offense_team in (None, "") and isinstance(event_id, str) and "-" in event_id:
                parts = event_id.split("-")
                if len(parts) >= 4:
                    offense_team = parts[2]
            filtered = scheme_df.copy()
            if offense_team and "team" in filtered.columns:
                filtered = filtered[filtered["team"] == offense_team]
            if "season" in filtered.columns and not pd.isna(season):
                filtered = filtered[filtered["season"] == season]
            if "week" in filtered.columns and not pd.isna(week):
                filtered = filtered[filtered["week"] == week]
            if not filtered.empty:
                scheme_row = filtered.iloc[-1]
                proe = scheme_row.get("proe")
                ed_pass = scheme_row.get("ed_pass_rate")
                pace = scheme_row.get("pace")
                lines = []
                if proe is not None and not pd.isna(proe):
                    lines.append(f"PROE: **{float(proe):+.1f}%**")
                if ed_pass is not None and not pd.isna(ed_pass):
                    lines.append(f"Early-down pass rate: **{float(ed_pass):.1f}%**")
                if pace is not None and not pd.isna(pace):
                    lines.append(f"Pace: **{float(pace):.2f} plays/min**")
                if lines:
                    scheme_info = "\n".join(f"- {line}" for line in lines)
        if scheme_info == "n/a":
            scheme_col.caption("No scheme metrics yet. Run team_week_scheme ingestion.")
        else:
            scheme_col.markdown(scheme_info)

        # WR/CB matchup card (display-only)
        wr_cb_col.markdown("**WR/CB Context**")
        wr_cb_info = "No matchup notes found."
        if not wr_cb_df.empty and event_id is not None:
            candidates = wr_cb_df[wr_cb_df.get("event_id") == event_id]
            if candidates.empty and player:
                candidates = wr_cb_df[wr_cb_df.get("player") == player]
            if not candidates.empty:
                top = candidates.iloc[0]
                blurb = top.get("note") or top.get("summary")
                link = top.get("source_url") or top.get("url")
                parts = []
                if isinstance(blurb, str) and blurb.strip():
                    parts.append(blurb.strip())
                if isinstance(link, str) and link.strip():
                    parts.append(f"[Source]({link.strip()})")
                if parts:
                    wr_cb_info = "\n\n".join(parts)
        wr_cb_col.markdown(wr_cb_info)

        # Injuries & Weather card
        inj_col.markdown("**Injuries & Weather**")
        info_lines: list[str] = []
        if not injuries_df.empty and event_id is not None:
            match = injuries_df[injuries_df.get("event_id") == event_id]
            if match.empty and player:
                match = injuries_df[injuries_df.get("player") == player]
            if not match.empty:
                for _, inj in match.iloc[:3].iterrows():
                    status = inj.get("status") or inj.get("designation")
                    desc = inj.get("note") or inj.get("description")
                    who = inj.get("player") or inj.get("name")
                    info_lines.append(f"{who or 'Player'}: {status or 'status n/a'} ({desc or 'n/a'})")
        if not weather_df.empty and event_id is not None:
            weather_match = weather_df[weather_df.get("event_id") == event_id]
            if weather_match.empty and isinstance(event_id, str):
                weather_match = weather_df[weather_df.get("game_id") == event_id]
            if not weather_match.empty:
                weather_row = weather_match.iloc[-1]
                temp = weather_row.get("temp_f")
                wind = weather_row.get("wind_mph")
                precip = weather_row.get("precip")
                indoor = weather_row.get("indoor")
                weather_parts = []
                if temp is not None and not pd.isna(temp):
                    weather_parts.append(f"Temp {float(temp):.0f}°F")
                if wind is not None and not pd.isna(wind):
                    weather_parts.append(f"Wind {float(wind):.0f} mph")
                if precip:
                    weather_parts.append(str(precip))
                if indoor in (1, True, "1", "Y", "y"):
                    weather_parts.append("Indoor")
                if weather_parts:
                    info_lines.append("Weather: " + ", ".join(weather_parts))
        if not info_lines:
            inj_col.caption("No injury or weather updates yet.")
        else:
            inj_col.markdown("\n".join(f"- {line}" for line in info_lines))

        # Context notes
        st.markdown("**Context notes**")
        existing_notes = fetch_context_notes(database_path, event_id)
        if not existing_notes.empty:
            display_notes = existing_notes.rename(
                columns={
                    "note": "Note",
                    "source_url": "Source",
                    "created_at": "Created",
                }
            )[["Note", "Source", "Created"]]
            st.table(display_notes)
        with st.form(key=f"context_note_form_{row.get('row_id')}"):
            note_text = st.text_area("Add note", key=f"note_input_{row.get('row_id')}")
            link_input = st.text_input("Source link (optional)", key=f"link_input_{row.get('row_id')}")
            submitted = st.form_submit_button("Save note")
            if submitted:
                if not note_text.strip():
                    st.warning("Note cannot be empty.")
                else:
                    add_context_note(database_path, event_id, note_text.strip(), link_input.strip())
                    st.success("Saved context note.")
                    st.experimental_rerun()

def _nz(value: object, default: object) -> object:
    """Return default when value is None/NA/NaN; otherwise value."""
    if value is None or value is pd.NA:
        return default
    if isinstance(value, float) and np.isnan(value):
        return default
    return value


def _as_bool01(value: object) -> int:
    """Coerce truthy values to 1 or 0 with NA-safe fallback."""
    value = _nz(value, 0)
    try:
        return 1 if bool(int(value)) else 0
    except Exception:
        return 1 if bool(value) else 0


def infer_position_bucket(market: object) -> str:
    """Rudimentary market-to-position mapping for top plays tabs."""
    if not isinstance(market, str):
        return "Other"
    text = market.lower()
    if "tight end" in text or " te" in text or text.startswith("te "):
        return "TE"
    if "passing" in text or "pass" in text:
        return "QB"
    if any(keyword in text for keyword in ("rushing", "rush", "carr", "attempt")):
        return "RB"
    if any(keyword in text for keyword in ("receiving", "reception", "targets", "yard", "longest reception")):
        return "WR"
    return "Other"


def compute_confidence(row: pd.Series) -> float:
    stale_raw = row.get("is_stale")
    stale_flag = _as_bool01(stale_raw)
    if stale_flag == 1:
        fresh = 0.0
    elif pd.isna(stale_raw):
        fresh = 0.8
    else:
        fresh = 1.0

    sigma = _nz(row.get("sigma"), 55.0)
    try:
        sigma = float(sigma)
    except (TypeError, ValueError):
        sigma = 55.0
    variance_score = 1.0 - min(1.0, max(0.0, (sigma - 25.0) / 60.0))

    p_model = _nz(row.get("p_model_shrunk"), row.get("model_p"))
    p_model = _nz(p_model, None)
    implied = _nz(row.get("implied_prob"), row.get("fair_prob"))
    implied = _nz(implied, None)

    agree = 0.5
    try:
        if p_model is not None and implied is not None:
            agree = 1.0 - min(1.0, abs(float(p_model) - float(implied)) * 2.0)
    except (TypeError, ValueError):
        agree = 0.5

    raw_conf = 0.5 * float(fresh) + 0.3 * float(variance_score) + 0.2 * float(agree)
    return float(np.clip(raw_conf, 0.0, 1.0))


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
    if "is_best" not in subset.columns:
        subset["is_best"] = False
    else:
        mask = subset["is_best"].isna()
        if mask.any():
            subset.loc[mask, "is_best"] = False
        subset["is_best"] = subset["is_best"].astype(bool)
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
    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
    csv_path = export_dir / f"{prefix}_{timestamp}.csv"
    parquet_path = export_dir / f"{prefix}_{timestamp}.parquet"
    card_df.to_csv(csv_path, index=False)
    try:
        card_df.to_parquet(parquet_path, index=False)
    except Exception:
        parquet_path = Path()
    return csv_path, parquet_path


def render_app() -> None:
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
    edges_view = edges_view.copy()
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
    for col in ("team", "home_team", "away_team", "game_date"):
        if col not in edges_view.columns:
            edges_view[col] = None
    if "is_home" not in edges_view.columns:
        edges_view["is_home"] = pd.NA
    for col in ("ci_width", "p_model_shrunk", "model_p", "p_model", "implied_prob", "is_home"):
        if col in edges_view.columns:
            edges_view[col] = pd.to_numeric(edges_view[col], errors="coerce")
    edges_view["def_score"] = pd.to_numeric(edges_view["def_score"], errors="coerce")
    if "is_stale" in edges_view.columns:
        edges_view["is_stale"] = (
            pd.to_numeric(edges_view["is_stale"], errors="coerce").fillna(0).astype("int8")
        )
    else:
        edges_view["is_stale"] = 0
    if "is_home" in edges_view.columns:
        edges_view["is_home"] = pd.to_numeric(edges_view["is_home"], errors="coerce")
    edges_view["line"] = pd.to_numeric(edges_view.get("line"), errors="coerce")
    edges_view["odds"] = pd.to_numeric(edges_view.get("odds"), errors="coerce")
    if "p_model_shrunk" not in edges_view.columns:
        edges_view["p_model_shrunk"] = edges_view.get("model_p")
    edges_view["shrink_pct"] = (
        (edges_view.get("model_p") - edges_view.get("p_model_shrunk")).fillna(0.0) * 100.0
    )
    edges_view["decimal_odds"] = edges_view.get("odds").apply(safe_decimal_from_american)
    edges_view["confidence"] = edges_view.apply(compute_confidence, axis=1)
    edges_view["position_bucket"] = edges_view.get("market").apply(infer_position_bucket)
    if "is_home" in edges_view.columns:
        edges_view["home_side"] = edges_view["is_home"].map({1: "Home", 0: "Away"}).fillna("n/a")
    else:
        edges_view["home_side"] = "n/a"

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

    display_cols = [
        "player",
        "team",
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
        "opponent_def_code",
        "home_side",
        "home_team",
        "away_team",
        "game_date",
    ]
    for col in ["def_tier", "def_score"]:
        if col in edges_view.columns and col not in display_cols:
            display_cols.append(col)
    for col in ("implied_prob", "fair_prob", "overround", "is_stale"):
        if col in edges_view.columns and col not in display_cols:
            display_cols.append(col)

    position_columns = [
        "player",
        "team",
        "market",
        "line",
        "book",
        "odds_side",
        "odds",
        "model_p",
        "p_model_shrunk",
        "ev_per_dollar",
        "kelly_frac",
        "confidence",
        "def_tier",
        "opponent_def_code",
        "home_side",
        "home_team",
        "away_team",
        "game_date",
    ]

    tabs = st.tabs(["By Position", "By Sportsbook", "All edges"])
    position_tab, sportsbook_tab, all_edges_tab = tabs

    def _apply_def_tier_filter(df: pd.DataFrame, stingy: bool, generous: bool) -> pd.DataFrame:
        if stingy and generous:
            tiers = {"stingy", "generous"}
            return df[df["def_tier"].astype(str).str.lower().isin(tiers)]
        if stingy:
            return df[df["def_tier"].astype(str).str.lower() == "stingy"]
        if generous:
            return df[df["def_tier"].astype(str).str.lower() == "generous"]
        return df

    def _apply_position_preset(df: pd.DataFrame, position: str, preset: str) -> pd.DataFrame:
        if preset == "RB unders vs top-5 stingy run D" and position == "RB":
            working = df.copy()
            working = working[working["odds_side"].astype(str).str.lower() == "under"]
            working = working[working["def_tier"].astype(str).str.lower() == "stingy"]
            if "def_score" in working.columns:
                working = working.sort_values("def_score", ascending=True)
            return working.head(5)
        if preset == "WR unders vs top-5 stingy WR D" and position == "WR":
            working = df.copy()
            working = working[working["odds_side"].astype(str).str.lower() == "under"]
            working = working[working["def_tier"].astype(str).str.lower() == "stingy"]
            if "def_score" in working.columns:
                working = working.sort_values("def_score", ascending=True)
            return working.head(5)
        return df

    with position_tab:
        st.subheader("Top plays by position")
        if edges_view.empty:
            st.info("No edges available with the current filters.")
        else:
            col1, col2, col3 = st.columns([1, 1, 2])
            show_stingy = col1.checkbox("Only vs stingy defenses", value=False, key="pos_stingy")
            show_generous = col2.checkbox("Only vs generous defenses", value=False, key="pos_generous")
            preset_choice = col3.selectbox(
                "Preset filters",
                ["None", "RB unders vs top-5 stingy run D", "WR unders vs top-5 stingy WR D"],
                index=0,
            )

            position_tabs = st.tabs(["QB", "RB", "WR", "TE"])
            for position_name, tab in zip(["QB", "RB", "WR", "TE"], position_tabs):
                with tab:
                    subset = edges_view[edges_view["position_bucket"] == position_name].copy()
                    subset = _apply_def_tier_filter(subset, show_stingy, show_generous)
                    subset = _apply_position_preset(subset, position_name, preset_choice)
                    subset = subset.sort_values("ev_per_dollar", ascending=False)
                    display_df = subset[position_columns].copy()
                    numeric_cols = [
                        "line",
                        "odds",
                        "model_p",
                        "p_model_shrunk",
                        "ev_per_dollar",
                        "kelly_frac",
                        "confidence",
                    ]
                    for col in numeric_cols:
                        if col in display_df.columns:
                            display_df[col] = pd.to_numeric(display_df[col], errors="coerce")
                    display_df = display_df.head(25)
                    if display_df.empty:
                        st.caption("No plays for this position with the current filters.")
                    else:
                        st.dataframe(display_df.round(3), use_container_width=True)

    with sportsbook_tab:
        st.subheader("Top plays by sportsbook")
        if edges_view.empty:
            st.info("No edges available with the current filters.")
        else:
            books = sorted(edges_view["book"].dropna().unique())
            if not books:
                st.caption("No sportsbook metadata available.")
            else:
                selected_book = st.selectbox("Sportsbook", books, index=0)
                book_view = edges_view[edges_view["book"] == selected_book].copy()
                book_view = book_view.sort_values("ev_per_dollar", ascending=False)
                book_display = book_view[position_columns].head(25).copy()
                for col in (
                    "line",
                    "odds",
                    "model_p",
                    "p_model_shrunk",
                    "ev_per_dollar",
                    "kelly_frac",
                    "confidence",
                ):
                    if col in book_display.columns:
                        book_display[col] = pd.to_numeric(book_display[col], errors="coerce")
                if book_display.empty:
                    st.caption("No plays for this book with the current filters.")
                else:
                    st.dataframe(book_display.round(3), use_container_width=True)

    with all_edges_tab:
        st.subheader("Edges (QB/RB/WR props)")
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
        if "home_side" in table_data.columns:
            column_config["home_side"] = st.column_config.TextColumn(
                "Home/Away",
                help="Indicator whether the listed offense is at home or on the road.",
            )
        if "game_date" in table_data.columns:
            column_config["game_date"] = st.column_config.TextColumn(
                "Game Date",
                help="ISO date of the matchup (if known).",
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

    st.subheader("Matchup drill-down")
    if edges_view.empty:
        st.info("No edges to inspect.")
    else:
        matchup_source = selected_edges if not selected_edges.empty else edges_view.head(5)
        for _, matchup_row in matchup_source.iterrows():
            render_matchup_expander(matchup_row, data, database_path)

    st.subheader("Line shopping across books")
    if odds_raw.empty:
        st.info("Run the odds poller/importer to populate raw odds snapshots for line shopping.")
    else:
        st.caption(
            "Expand a row to inspect every book for that player prop. ⭐ marks the best available price per side."
        )
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
                display_cols_inner = [
                    "best_flag",
                    "book",
                    "side",
                    "odds",
                    "decimal_odds",
                    "implied_prob",
                    "fair_prob",
                    "updated_at",
                ]
                st.dataframe(view[display_cols_inner])
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


if __name__ == "__main__":
    render_app()
