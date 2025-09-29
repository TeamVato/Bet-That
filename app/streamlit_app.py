"""Streamlit app for exploring betting edges and odds history."""

from __future__ import annotations

import datetime
import os
import sqlite3
from collections.abc import Sequence
from contextlib import closing
from dataclasses import replace
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from app.debug_panel import (
    _connect,
    active_env_settings,
    count_rows,
    counts_by,
    edges_quality,
    edges_weather_coverage,
    max_updated,
    odds_staleness,
)
from app.ui_badges import context_key, is_why_open, render_header_with_badge
from app.why_empty import Filters as EmptyFilters
from app.why_empty import explain_empty
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
        context_expected = {
            "scheme": ["team", "season", "week", "proe", "ed_pass_rate", "pace"],
            "weather": ["event_id", "game_id", "temp_f", "wind_mph", "precip", "indoor"],
            "wr_cb": ["event_id", "player", "note", "summary", "source_url", "url"],
            "injuries": [
                "event_id",
                "player",
                "status",
                "designation",
                "note",
                "description",
                "name",
            ],
            "context_notes": ["event_id", "note", "source_url", "created_at"],
        }
        for key, expected_cols in context_expected.items():
            df_ref = extras.get(key)
            if df_ref is None or df_ref.empty:
                extras[key] = pd.DataFrame(
                    {col: pd.Series(dtype="object") for col in expected_cols}
                )
                continue
            missing_cols = [col for col in expected_cols if col not in df_ref.columns]
            for col in missing_cols:
                df_ref[col] = pd.NA
            extras[key] = df_ref
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


def _safe_filter(df: pd.DataFrame | None, col: str, value: object) -> pd.DataFrame:
    """Return an empty frame instead of raising when the column is missing."""
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame(columns=[col])
    if col not in df.columns:
        return df.iloc[0:0]
    return df.loc[df[col].eq(value)]


def _coalesce(*vals, default=None):
    """Return the first value that is not NA/None/empty-string."""
    for v in vals:
        if v is None:
            continue
        try:
            if pd.isna(v):
                continue
        except Exception:
            pass
        if isinstance(v, str) and not v.strip():
            continue
        return v
    return default


def _coalesce_na(*values, default=""):
    """Return the first non-null/non-NA string value from the given values."""
    for value in values:
        if value is None:
            continue
        try:
            if pd.isna(value):
                continue
        except Exception:
            pass
        if isinstance(value, str):
            return value
        # Convert non-string values to string if they're not null/NA
        return str(value)
    return default


def _str_eq(a, b):
    """Case-insensitive, NA-safe equality for strings."""
    a = _coalesce(a, default="")
    b = _coalesce(b, default="")
    return str(a).strip().lower() == str(b).strip().lower()


def _infer_current_season(reference: datetime.datetime | None = None) -> int:
    """Infer the current NFL season (year) based on today's date."""
    ref = reference or datetime.datetime.now(datetime.timezone.utc)
    return ref.year if ref.month >= 8 else ref.year - 1


def _load_available_seasons(database_path: Path, edges_df: pd.DataFrame) -> list[int]:
    """
    Load available seasons from defense_ratings and edges_df.
    Returns sorted list in descending order with proper Int64 casting and NA handling.
    """
    seasons: set[int] = set()

    # Query defense_ratings seasons from SQLite
    try:
        with sqlite3.connect(database_path) as conn:
            defense_df = pd.read_sql_query("SELECT DISTINCT season FROM defense_ratings", conn)
            if not defense_df.empty and "season" in defense_df.columns:
                # Cast to Int64, drop NA, convert to int
                defense_seasons = pd.to_numeric(defense_df["season"], errors="coerce").astype(
                    "Int64"
                )
                seasons.update(int(s) for s in defense_seasons.dropna().unique())
    except Exception:
        pass

    # Union with edges_df seasons if present
    if isinstance(edges_df, pd.DataFrame) and "season" in edges_df.columns:
        try:
            # Cast to Int64, drop NA, convert to int
            edges_seasons = pd.to_numeric(edges_df["season"], errors="coerce").astype("Int64")
            seasons.update(int(s) for s in edges_seasons.dropna().unique())
        except Exception:
            pass

    # If empty, return current season
    if not seasons:
        seasons.add(_infer_current_season())

    # Sort in descending order (most recent first)
    return sorted(seasons, reverse=True)


def apply_season_filter(
    edges_df: pd.DataFrame, selected: Sequence[int], available_seasons: list[int]
) -> pd.DataFrame:
    """Return a copy filtered by selected seasons, handling NA safely."""
    if not isinstance(edges_df, pd.DataFrame):
        return pd.DataFrame()
    result = edges_df.copy()
    if "season" not in result.columns or not selected:
        return result

    try:
        safe_selected = [int(s) for s in selected]
    except Exception:
        return result

    # Coerce season to Int64 for consistent handling
    season_series = pd.to_numeric(result["season"], errors="coerce").astype("Int64")

    # NA-safe membership: include NA values if "All" seasons are selected
    all_selected = len(safe_selected) == len(available_seasons)
    if all_selected:
        # When all seasons selected, include both matching seasons and NA values
        mask = season_series.isin(safe_selected) | season_series.isna()
    else:
        # When specific seasons selected, only include matching seasons (exclude NA)
        mask = season_series.isin(safe_selected)

    return result.loc[mask].copy()


def render_debug_panel(
    database_path: Path,
    edges_df: pd.DataFrame,
    filter_state: dict,
) -> None:
    """Render the debug panel with lightweight diagnostics when enabled."""

    env_settings = active_env_settings()
    with closing(_connect(str(database_path))) as con:
        debug_expander = st.expander("🔎 Debug Panel", expanded=True)
        with debug_expander:
            st.markdown("#### Data Sources")
            data_sources = {
                "db_path": str(database_path),
                "tables": {
                    "odds_csv_raw": count_rows(con, "odds_csv_raw"),
                    "current_best_lines": count_rows(con, "current_best_lines"),
                    "edges": count_rows(con, "edges"),
                    "defense_ratings": count_rows(con, "defense_ratings"),
                    "weather": count_rows(con, "weather"),
                    "injuries": count_rows(con, "injuries"),
                },
                "max_updated": {
                    "odds_csv_raw": max_updated(con, "odds_csv_raw"),
                    "current_best_lines": max_updated(con, "current_best_lines"),
                    "edges": max_updated(con, "edges"),
                    "weather": max_updated(con, "weather"),
                },
            }
            st.write(data_sources)

            st.markdown("#### Coverage")
            odds_by_book = counts_by(con, "odds_csv_raw", "book").rename(columns={"key": "book"})
            if odds_by_book.empty:
                st.caption("No odds CSV rows grouped by sportsbook yet.")
            else:
                st.caption("Odds by sportsbook")
                st.dataframe(odds_by_book, width="stretch")

            edges_season_db = counts_by(con, "edges", "season").rename(columns={"key": "season"})
            if not edges_season_db.empty:
                st.caption("Edges (database) by season")
                st.dataframe(edges_season_db, width="stretch")

            defense_season_db = counts_by(con, "defense_ratings", "season").rename(
                columns={"key": "season"}
            )
            if not defense_season_db.empty:
                st.caption("Defense ratings by season")
                st.dataframe(defense_season_db, width="stretch")

            if not edges_df.empty:
                if "season" in edges_df.columns:
                    season_counts = (
                        edges_df.assign(season=_display_season(edges_df["season"]))
                        .groupby("season")
                        .size()
                        .reset_index(name="count")
                        .sort_values("count", ascending=False)
                    )
                    st.caption("Edges (current view) by season")
                    st.dataframe(season_counts, width="stretch")
                if "pos" in edges_df.columns:
                    pos_counts = (
                        edges_df.assign(pos=edges_df["pos"].fillna("Unknown"))
                        .groupby("pos")
                        .size()
                        .reset_index(name="count")
                        .sort_values("count", ascending=False)
                    )
                    st.caption("Edges (current view) by position")
                    st.dataframe(pos_counts, width="stretch")

            st.markdown("#### Staleness")
            st.write({**odds_staleness(con), "STALE_MINUTES": env_settings["STALE_MINUTES"]})

            st.markdown("#### Joins & Quality")
            quality_data = edges_quality(con)
            st.write(quality_data)

            # Join key coverage analysis for current view
            if not edges_df.empty:
                st.caption("Join key coverage (current view)")
                total_edges = len(edges_df)

                coverage_stats = {}
                for key_col in ["season", "week", "opponent_def_code"]:
                    if key_col in edges_df.columns:
                        non_null = (~edges_df[key_col].isna()).sum()
                        coverage_stats[key_col] = (
                            f"{non_null}/{total_edges} ({non_null/total_edges*100:.1f}%)"
                        )
                    else:
                        coverage_stats[key_col] = "column missing"

                # Complete join key coverage
                if all(col in edges_df.columns for col in ["season", "week", "opponent_def_code"]):
                    complete_keys = (
                        (~edges_df["season"].isna())
                        & (~edges_df["week"].isna())
                        & (~edges_df["opponent_def_code"].isna())
                    ).sum()
                    coverage_stats["complete_join_keys"] = (
                        f"{complete_keys}/{total_edges} ({complete_keys/total_edges*100:.1f}%)"
                    )

                st.json(coverage_stats)

                # Defense ratings merge success
                if "def_tier" in edges_df.columns:
                    successful_joins = (~edges_df["def_tier"].isna()).sum()
                    st.caption(
                        f"Defense ratings merge success: {successful_joins}/{total_edges} ({successful_joins/total_edges*100:.1f}%)"
                    )

                    if successful_joins < total_edges:
                        unmatched = edges_df[edges_df["def_tier"].isna()]
                        if not unmatched.empty:
                            missing_reasons = {}
                            missing_reasons["missing_season"] = unmatched["season"].isna().sum()
                            missing_reasons["missing_week"] = unmatched["week"].isna().sum()
                            missing_reasons["missing_opponent_def_code"] = (
                                unmatched["opponent_def_code"].isna().sum()
                            )

                            # Show sample of unmatched opponent codes
                            unmatched_codes = unmatched[unmatched["opponent_def_code"].notna()][
                                "opponent_def_code"
                            ].unique()
                            if len(unmatched_codes) > 0:
                                missing_reasons["unmatched_opponent_codes_sample"] = sorted(
                                    unmatched_codes
                                )[:10]

                            st.caption("Unmatched join analysis:")
                            st.json(missing_reasons)
            st.write(edges_weather_coverage(con))

            st.markdown("#### Filters (effective)")
            st.write(filter_state)

            st.markdown("#### Environment")
            st.write(env_settings)


def render_empty_explainer(
    edges_source: pd.DataFrame,
    filters_obj: EmptyFilters,
    database_path: Path,
    force_open: bool,
    ctx_key: str,
) -> None:
    """Render the explainer, optionally forced open via the context key."""

    tips = explain_empty(edges_source, filters_obj, database_path)
    with st.expander("ℹ️ Why is this empty (or limited)?", expanded=force_open):
        for line in tips.get("tips", []):
            st.write(line)
        for extra in tips.get("extras", []):
            st.caption(extra)
    if force_open:
        st.session_state[ctx_key] = False


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
    filters: Optional[EmptyFilters] = None,
    edges_source: Optional[pd.DataFrame] = None,
) -> None:
    event_id = row.get("event_id")
    player = _coalesce(row.get("player"), default="Unknown player")
    market = _coalesce(row.get("market"), default="Unknown market")
    label = f"Matchup: {player} · {market}"
    ctx_drawer = context_key("matchup", event_id or player)

    scheme_df = data.get("scheme", pd.DataFrame())
    weather_df = data.get("weather", pd.DataFrame())
    injuries_df = data.get("injuries", pd.DataFrame())
    wr_cb_df = data.get("wr_cb", pd.DataFrame())

    def_tier = _coalesce(row.get("def_tier"), default="n/a")
    def_score = row.get("def_score")
    def_score_display = (
        f"{def_score:.2f}"
        if isinstance(def_score, (int, float)) and not np.isnan(def_score)
        else "n/a"
    )

    with st.expander(label, expanded=False):
        render_header_with_badge("Matchup context", None, ctx_drawer)
        if filters is not None and edges_source is not None and is_why_open(ctx_drawer):
            render_empty_explainer(
                edges_source,
                filters,
                database_path,
                force_open=True,
                ctx_key=ctx_drawer,
            )
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
            offense_team = _coalesce(row.get("team"), row.get("team_code"))
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
            candidates = _safe_filter(wr_cb_df, "event_id", event_id)
            if candidates.empty and player:
                candidates = _safe_filter(wr_cb_df, "player", player)
            if not candidates.empty:
                top = candidates.iloc[0]
                blurb = _coalesce(top.get("note"), top.get("summary"), default="")
                link = _coalesce(top.get("source_url"), top.get("url"), default="")
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
        weather_caption: str | None = None
        if not injuries_df.empty and event_id is not None:
            match = _safe_filter(injuries_df, "event_id", event_id)
            if match.empty and player:
                match = _safe_filter(injuries_df, "player", player)
            if not match.empty:
                for _, inj in match.iloc[:3].iterrows():
                    status = _coalesce_na(
                        inj.get("status"),
                        inj.get("designation"),
                        default="(status unknown)",
                    )
                    who = _coalesce_na(inj.get("player"), inj.get("name"), default="Player")
                    note = _coalesce_na(inj.get("notes"), inj.get("comment"), default="")
                    desc = _coalesce_na(
                        inj.get("note"),
                        inj.get("description"),
                        inj.get("detail"),
                        default="",
                    )
                    side = _coalesce_na(inj.get("side"), default="")
                    team = _coalesce_na(inj.get("team"), inj.get("club"), default="")
                    details = [
                        str(val).strip()
                        for val in (team, side, note, desc)
                        if isinstance(val, str) and val.strip()
                    ]
                    detail_text = f" ({'; '.join(details)})" if details else ""
                    info_lines.append(f"{who}: {status}{detail_text}")

        if event_id is None or pd.isna(event_id):
            weather_caption = "No weather context found for this matchup yet."
        elif weather_df is None or weather_df.empty:
            weather_caption = "No weather context found for this matchup yet."
        else:
            key_col = (
                "event_id"
                if "event_id" in weather_df.columns
                else ("game_id" if "game_id" in weather_df.columns else None)
            )
            if key_col is None:
                weather_caption = "No weather context found for this matchup yet."
            else:
                try:
                    wmatch = weather_df.loc[weather_df[key_col].eq(event_id)]
                except Exception:
                    wmatch = pd.DataFrame()
                if wmatch.empty:
                    weather_caption = "No weather context found for this matchup yet."
                else:
                    weather_row = wmatch.iloc[-1]
                    temp = weather_row.get("temp_f")
                    wind = weather_row.get("wind_mph")
                    precip = _coalesce(weather_row.get("precip"), default="")
                    indoor = weather_row.get("indoor")
                    weather_parts = []
                    if temp is not None and not pd.isna(temp):
                        weather_parts.append(f"Temp {float(temp):.0f}°F")
                    if wind is not None and not pd.isna(wind):
                        weather_parts.append(f"Wind {float(wind):.0f} mph")
                    if isinstance(precip, str) and precip.strip():
                        weather_parts.append(precip.strip())
                    elif precip not in (None, "") and not pd.isna(precip):
                        weather_parts.append(str(precip))
                    if indoor in (1, True, "1", "Y", "y"):
                        weather_parts.append("Indoor")
                    if weather_parts:
                        info_lines.append("Weather: " + ", ".join(weather_parts))

        if not info_lines:
            if weather_caption:
                inj_col.caption(weather_caption)
            else:
                inj_col.caption("No injury or weather updates yet.")
            if filters is not None and edges_source is not None:
                render_empty_explainer(
                    edges_source,
                    filters,
                    database_path,
                    force_open=True,
                    ctx_key=ctx_drawer,
                )
        else:
            inj_col.markdown("\n".join(f"- {line}" for line in info_lines))
            if weather_caption and all(not line.startswith("Weather:") for line in info_lines):
                inj_col.caption(weather_caption)

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
        # Create unique keys based on event_id and player to avoid duplicates
        event_id_safe = str(row.get("event_id", "no_event")).replace("-", "_").replace(" ", "_")
        player_safe = str(row.get("player", "no_player")).replace(" ", "_").replace("-", "_")
        row_id_safe = str(row.get("row_id", "no_row"))
        unique_id = f"{event_id_safe}_{player_safe}_{row_id_safe}"
        with st.form(key=f"context_note_form_{unique_id}"):
            note_text = st.text_area("Add note", key=f"note_input_{unique_id}")
            link_input = st.text_input("Source link (optional)", key=f"link_input_{unique_id}")
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


def _display_season(series: pd.Series) -> pd.Series:
    """Cast nullable Int64 series to string with 'Unknown' for NA values."""
    if series.empty:
        return series
    # Convert to string first to handle nullable Int64 dtype
    str_series = series.astype(str)
    # Replace 'nan' and '<NA>' string representations with 'Unknown'
    return str_series.replace(["nan", "<NA>", "None"], "Unknown")


def _coalesce_na(*vals, default=""):
    """Return the first non-NA, non-None, non-empty string value."""
    for val in vals:
        if val is None or val is pd.NA:
            continue
        if isinstance(val, float) and np.isnan(val):
            continue
        str_val = str(val).strip()
        if str_val and str_val.lower() not in ("none", "nan", "<na>"):
            return str_val
    return default


def _safe_filter(df: pd.DataFrame, col: str, value) -> pd.DataFrame:
    """Filter DataFrame by column value, returning empty DataFrame if column doesn't exist."""
    if df.empty:
        # Return empty DataFrame with the expected column structure
        return pd.DataFrame(columns=[col] if col else [])
    if col not in df.columns:
        return pd.DataFrame(columns=df.columns)
    return df[df[col] == value]


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
    if any(
        keyword in text
        for keyword in ("receiving", "reception", "targets", "yard", "longest reception")
    ):
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


def prepare_card_dataframe(df: pd.DataFrame, bankroll: float, fraction: float) -> pd.DataFrame:
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
    edges = data["edges"].copy()
    props = data["props"]
    projections = data["projections"]
    best_lines = data["best_lines"]
    snapshots = data["snapshots"]
    odds_raw = data.get("odds_raw", pd.DataFrame())
    base_edges_count = len(edges)

    # Ensure pos column exists and is normalized
    if "pos" not in edges.columns:
        edges["pos"] = pd.NA
    edges["pos"] = edges["pos"].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})

    # Fill missing positions from market inference as fallback
    if "market" in edges.columns:
        missing_pos = edges["pos"].isna()
        if missing_pos.any():
            inferred = edges.loc[missing_pos, "market"].apply(infer_position_bucket)
            edges.loc[missing_pos, "pos"] = inferred.replace("Other", pd.NA)

    # Normalize position values to uppercase
    edges["pos"] = edges["pos"].apply(lambda val: val.upper() if isinstance(val, str) else val)

    if props[["season", "def_team"]].isna().any().any():
        st.warning(
            "Some props are missing season or opponent team metadata. Update the CSV for better projections."
        )

    available_seasons = _load_available_seasons(database_path, edges)
    selected_seasons = st.sidebar.multiselect(
        "Season filter",
        options=available_seasons,
        key="season_filter",
        help="Select seasons to analyze. Empty selection will show no data.",
    )
    if hasattr(st.sidebar, "toggle"):
        debug_mode = st.sidebar.toggle("Debug mode", value=False, key="debug_mode_toggle")
    else:
        debug_mode = st.sidebar.checkbox("Debug mode", value=False, key="debug_mode_toggle")
    odds_min, odds_max = st.sidebar.slider("Odds range (American)", -400, 400, (-250, 250))
    min_ev = st.sidebar.slider("Minimum EV per $1", -1.0, 1.0, 0.0, step=0.01)
    # Freshness controls - upcoming games only, optional staleness
    st.sidebar.markdown("### Freshness controls")

    # Hide past games by commence_time (default True)
    hide_past_games = st.sidebar.checkbox(
        "Hide past games", value=True, help="Only show games with commence_time >= now (UTC)"
    )

    # Optional staleness filter toggle
    stale_odds_toggle = st.sidebar.checkbox(
        "Filter by odds staleness",
        value=False,
        help="Enable filtering based on how long ago odds were updated",
    )

    # Staleness threshold slider (only enabled when toggle is on)
    stale_minutes_default = int(os.getenv("STALE_MINUTES", "120"))
    staleness_minutes = st.sidebar.slider(
        "Staleness threshold (minutes)",
        min_value=30,
        max_value=480,
        value=stale_minutes_default,
        step=15,
        disabled=not stale_odds_toggle,
        help="Hide odds older than this threshold (only when staleness filter is enabled)",
    )
    show_best_only = st.sidebar.checkbox("Show only best-priced edges", value=True)
    bankroll = st.sidebar.number_input("Bankroll ($)", min_value=0.0, value=1000.0, step=50.0)
    kelly_fraction_input = st.sidebar.slider("Kelly fraction", 0.0, 1.0, 0.25, 0.05)
    max_auto = st.sidebar.slider("Max picks (auto card)", 1, 20, 5)
    st.sidebar.markdown("### Defense filter")
    only_generous = st.sidebar.checkbox("Only vs generous defenses", value=False)

    edges_view = edges.copy().reset_index(drop=True)
    edges_view = edges_view.copy()

    filters_base = EmptyFilters(
        seasons=list(selected_seasons) if selected_seasons else [],
        odds_min=int(odds_min),
        odds_max=int(odds_max),
        ev_min=float(min_ev),
        hide_stale=bool(stale_odds_toggle),
        best_priced_only=bool(show_best_only),
    )

    if "season" not in edges_view.columns:
        edges_view["season"] = pd.Series(pd.NA, index=edges_view.index)

    edges_view = apply_season_filter(edges_view, selected_seasons, available_seasons)

    # Also apply season filtering to best_lines for summary display
    if not best_lines.empty and "season" in best_lines.columns:
        best_lines = apply_season_filter(best_lines, selected_seasons, available_seasons)

    # Handle empty season selection
    if not selected_seasons:
        st.info(
            "💡 Select one or more seasons from the sidebar to view edges and analyze betting opportunities."
        )
        st.stop()

    if "season" in edges_view.columns:
        season_numeric = pd.to_numeric(edges_view["season"], errors="coerce")
        try:
            edges_view["season"] = season_numeric.astype("Int64")
        except Exception:
            edges_view["season"] = season_numeric

    # Position column should already be processed from edges DataFrame
    if "pos" not in edges_view.columns:
        edges_view["pos"] = pd.NA

    edges_view["row_id"] = edges_view.index
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
        edges_view.get("model_p") - edges_view.get("p_model_shrunk")
    ).fillna(0.0) * 100.0
    edges_view["decimal_odds"] = edges_view.get("odds").apply(safe_decimal_from_american)

    # Numeric defaults to avoid NA-related crashes in compute_confidence
    num_defaults = {
        "model_p": 0.5,
        "market_p": 0.5,
        "ev_per_dollar": 0.0,
        "minutes_since_update": 9999.0,
        "kelly_frac": 0.0,
    }
    for k, v in num_defaults.items():
        if k in edges_view.columns:
            edges_view[k] = pd.to_numeric(edges_view[k], errors="coerce").fillna(v)

    edges_view["confidence"] = edges_view.apply(compute_confidence, axis=1)

    # Apply freshness filters in order: upcoming -> staleness
    import datetime

    current_time = datetime.datetime.now(datetime.timezone.utc)

    # Filter 1: Hide past games by commence_time (UTC)
    if hide_past_games and "commence_time" in edges_view.columns:

        def is_upcoming_game(commence_time):
            if pd.isna(commence_time) or commence_time is None:
                return True  # Keep games without commence_time
            try:
                if isinstance(commence_time, str):
                    game_time = datetime.datetime.fromisoformat(
                        commence_time.replace("Z", "+00:00")
                    )
                else:
                    game_time = pd.to_datetime(commence_time, utc=True)
                return game_time >= current_time
            except Exception:
                return True  # Keep if can't parse

        before_upcoming = len(edges_view)
        edges_view = edges_view[edges_view["commence_time"].apply(is_upcoming_game)]
        upcoming_filtered = before_upcoming - len(edges_view)
    else:
        upcoming_filtered = 0

    # Filter 2: Optional staleness filter (only if toggle enabled)
    if stale_odds_toggle and "updated_at" in edges_view.columns:

        def is_fresh_odds(updated_at):
            if pd.isna(updated_at) or updated_at is None:
                return False  # Remove odds without update time
            try:
                if isinstance(updated_at, str):
                    update_time = datetime.datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                else:
                    update_time = pd.to_datetime(updated_at, utc=True)
                delta_minutes = (current_time - update_time).total_seconds() / 60.0
                return delta_minutes <= staleness_minutes
            except Exception:
                return False  # Remove if can't parse

        before_staleness = len(edges_view)
        edges_view = edges_view[edges_view["updated_at"].apply(is_fresh_odds)]
        staleness_filtered = before_staleness - len(edges_view)
    else:
        staleness_filtered = 0

    # Use pos column directly as position_bucket, strict filtering to QB/RB/WR only
    def normalize_position(pos_val):
        if not isinstance(pos_val, str) or not pos_val.strip():
            return None
        pos_clean = pos_val.strip().upper()
        # Only allow QB, RB, WR per user requirements
        return pos_clean if pos_clean in {"QB", "RB", "WR"} else None

    edges_view["position_bucket"] = edges_view["pos"].apply(normalize_position)
    if "is_home" in edges_view.columns:
        edges_view["home_side"] = edges_view["is_home"].map({1: "Home", 0: "Away"}).fillna("n/a")
    else:
        edges_view["home_side"] = "n/a"

    edges_view = edges_view[(edges_view["odds"] >= odds_min) & (edges_view["odds"] <= odds_max)]
    edges_view = edges_view[edges_view["ev_per_dollar"] >= min_ev]
    if hide_stale:
        if "is_stale_custom" in edges_view.columns:
            edges_view = edges_view[edges_view["is_stale_custom"].fillna(0) == 0]
        else:
            edges_view = edges_view[edges_view["is_stale"].fillna(0) == 0]
    if only_generous:
        edges_view = edges_view.loc[edges_view["def_tier"] == "generous"]
    if show_best_only:
        edges_view = edges_view.sort_values("ev_per_dollar", ascending=False).drop_duplicates(
            [
                "event_id",
                "player",
                "market",
            ]
        )

    ctx_main = context_key("edges", "main")

    filter_state = {
        "season_selected": list(selected_seasons),
        "odds_range": [odds_min, odds_max],
        "min_ev_per_dollar": min_ev,
        "hide_past_games": hide_past_games,
        "stale_odds_toggle": stale_odds_toggle,
        "staleness_minutes": staleness_minutes,
        "only_generous_defenses": only_generous,
        "best_priced_only": show_best_only,
        "rows_before_filters": base_edges_count,
        "rows_after_filters": len(edges_view),
        "rows_excluded": max(base_edges_count - len(edges_view), 0),
        "upcoming_filtered": upcoming_filtered,
        "staleness_filtered": staleness_filtered,
    }
    if debug_mode:
        render_debug_panel(database_path, edges_view, filter_state)

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

    # Freshness is now handled by the upcoming games filter and optional staleness toggle

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
    selected_edges = edges_view.iloc[0:0]

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
            render_empty_explainer(
                edges,
                filters_base,
                database_path,
                force_open=True,
                ctx_key=context_key("edges", "position_overview"),
            )
        else:
            col1, col2, col3 = st.columns([1, 1, 2])
            show_stingy = col1.checkbox("Only vs stingy defenses", value=False, key="pos_stingy")
            show_generous = col2.checkbox(
                "Only vs generous defenses", value=False, key="pos_generous"
            )
            preset_choice = col3.selectbox(
                "Preset filters",
                ["None", "RB unders vs top-5 stingy run D", "WR unders vs top-5 stingy WR D"],
                index=0,
            )

            # Always render QB, RB, WR tabs regardless of available data
            tab_labels = ["QB", "RB", "WR"]
            position_tabs = st.tabs(tab_labels)
            for position_name, tab in zip(tab_labels, position_tabs):
                with tab:
                    subset = edges_view[edges_view["position_bucket"] == position_name].copy()
                    subset = _apply_def_tier_filter(subset, show_stingy, show_generous)
                    subset = _apply_position_preset(subset, position_name, preset_choice)
                    subset = subset.sort_values("ev_per_dollar", ascending=False)
                    ctx_pos = context_key("edges", "pos", position_name)

                    if subset.empty:
                        st.info(f"No {position_name} edges available with current filters.")
                        render_empty_explainer(
                            edges_view, filters_base, database_path, False, ctx_pos
                        )
                        continue

                    render_header_with_badge(position_name, subset, ctx_pos)

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
                    if display_df.empty or is_why_open(ctx_pos):
                        render_empty_explainer(
                            edges,
                            replace(filters_base, pos=position_name),
                            database_path,
                            force_open=is_why_open(ctx_pos) or display_df.empty,
                            ctx_key=ctx_pos,
                        )
                    if not display_df.empty:
                        st.dataframe(display_df.round(3), width="stretch")

    with sportsbook_tab:
        st.subheader("Top plays by sportsbook")
        if edges_view.empty:
            st.info("No edges available with the current filters.")
            render_empty_explainer(
                edges,
                filters_base,
                database_path,
                force_open=True,
                ctx_key=context_key("edges", "book_overview"),
            )
        else:
            books_in_view = sorted(
                [
                    b
                    for b in edges_view.get("book", pd.Series(dtype=str)).dropna().unique().tolist()
                    if b
                ]
            )
            fallback_books = [
                "DraftKings",
                "FanDuel",
                "BetMGM",
                "Caesars",
                "PointsBet",
                "ESPN BET",
            ]
            books = books_in_view if books_in_view else fallback_books
            selected_book = st.selectbox("Sportsbook", options=books, index=0)

            if "book" in edges_view.columns:
                sb_df = edges_view[edges_view["book"] == selected_book]
            else:
                sb_df = edges_view.iloc[0:0]

            ctx_book = context_key("edges", "book", selected_book)
            render_header_with_badge(selected_book, sb_df, ctx_book)

            if sb_df.empty or is_why_open(ctx_book):
                render_empty_explainer(
                    edges,
                    replace(filters_base, book=selected_book),
                    database_path,
                    force_open=is_why_open(ctx_book) or sb_df.empty,
                    ctx_key=ctx_book,
                )

            if not sb_df.empty:
                book_view = sb_df.copy().sort_values("ev_per_dollar", ascending=False)
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
                if book_display.empty or is_why_open(ctx_book):
                    render_empty_explainer(
                        edges,
                        replace(filters_base, book=selected_book),
                        database_path,
                        force_open=is_why_open(ctx_book) or book_display.empty,
                        ctx_key=ctx_book,
                    )
                if not book_display.empty:
                    st.dataframe(book_display.round(3), width="stretch")

    with all_edges_tab:
        render_header_with_badge("Edges (QB/RB/WR props)", edges_view, ctx_main)
        if edges_view.empty or is_why_open(ctx_main):
            if edges_view.empty:
                st.info("No edges match the active filters.")
            render_empty_explainer(
                edges,
                filters_base,
                database_path,
                force_open=is_why_open(ctx_main) or edges_view.empty,
                ctx_key=ctx_main,
            )

        if not edges_view.empty:
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
            # Freshness is now handled by upcoming games filter and staleness toggle

            editor_result = st.data_editor(
                editor_df,
                column_config=column_config,
                hide_index=True,
                num_rows="dynamic",
                width="stretch",
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
                st.dataframe(card_df[summary_cols].round(3), width="stretch")
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
        st.dataframe(auto_card[summary_cols].round(3), width="stretch")
        if st.button("Export auto card"):
            csv_path, parquet_path = export_card(auto_card, prefix="card_auto")
            st.success(f"Exported auto card to {csv_path}")

    st.subheader("Matchup drill-down")
    if edges_view.empty:
        st.info("No edges to inspect.")
    else:
        matchup_source = selected_edges if not selected_edges.empty else edges_view.head(5)
        for _, matchup_row in matchup_source.iterrows():
            render_matchup_expander(
                matchup_row,
                data,
                database_path,
                filters=filters_base,
                edges_source=edges,
            )

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
            label = (
                f"{row.get('player')} · {row.get('market')} · {row.get('line')} ({row.get('book')})"
            )
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
                ]
                st.dataframe(view[display_cols_inner], width="stretch")
        if not best_lines.empty:
            st.markdown("#### Current best lines summary")
            st.dataframe(best_lines, width="stretch")

    st.subheader("Steam alerts")
    if snapshots.empty:
        st.info("Steam alerts require at least two odds snapshots.")
    else:
        alerts = steam_detector.detect_steam(snapshots)
        if alerts.empty:
            st.success("No steam detected in the most recent snapshots.")
        else:
            st.dataframe(alerts, width="stretch")

        st.caption(
            "Exports are saved under storage/exports/. Use jobs/export_bi.py for BI snapshots."
        )


if __name__ == "__main__":
    render_app()
