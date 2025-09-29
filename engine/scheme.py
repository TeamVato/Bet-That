"""Compute team-level scheme metrics (PROE, early-down pass rate, pace)."""

from __future__ import annotations

import datetime
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

try:
    import nfl_data_py as nfl
except ImportError:  # pragma: no cover - optional dependency
    nfl = None  # type: ignore


@dataclass
class SchemeConfig:
    seasons: Iterable[int]
    neutral_downs: tuple[int, ...] = (1, 2, 3)
    early_downs: tuple[int, ...] = (1, 2)


def _load_pbp(seasons: Iterable[int]) -> pd.DataFrame:
    if not nfl:
        raise RuntimeError("nfl_data_py is required to compute scheme metrics")
    seasons = [int(s) for s in seasons]
    if not seasons:
        return pd.DataFrame()
    df = nfl.import_pbp_data(seasons)
    if df.empty:
        return df
    required = {
        "game_id",
        "season",
        "week",
        "posteam",
        "pass",
        "down",
        "ydstogo",
        "yardline_100",
        "game_seconds_remaining",
    }
    missing = required.difference(df.columns)
    if missing:
        raise RuntimeError(f"play-by-play data missing required columns: {sorted(missing)}")
    return df


def _bucket(series: pd.Series, bins: list[float], labels: list[str]) -> pd.Series:
    return pd.cut(series, bins=bins, labels=labels, include_lowest=True, right=False)


def _compute_expected_pass(pbp: pd.DataFrame) -> pd.Series:
    working = pbp.copy()
    working = working.dropna(subset=["down", "ydstogo", "yardline_100"])
    working["down"] = working["down"].astype(int)
    ytg_bins = [0, 2, 5, 8, 12, 20, 1000]
    ytg_labels = ["0-2", "2-5", "5-8", "8-12", "12-20", "20+"]
    yard_bins = [0, 20, 40, 60, 80, 100]
    yard_labels = ["0-20", "20-40", "40-60", "60-80", "80-100"]
    working["ytg_bucket"] = _bucket(working["ydstogo"], ytg_bins, ytg_labels)
    working["yard_bucket"] = _bucket(working["yardline_100"], yard_bins, yard_labels)
    working["pass_flag"] = working["pass"].fillna(0).astype(int)

    avg = (
        working.groupby(["down", "ytg_bucket", "yard_bucket"], observed=True)["pass_flag"]
        .mean()
        .rename("expected")
    )
    lookup = avg.to_dict()

    def _lookup(row) -> float:
        key = (row.get("down"), row.get("ytg_bucket"), row.get("yard_bucket"))
        return lookup.get(key, avg.mean() if not avg.empty else 0.5)

    working["expected_pass"] = working.apply(_lookup, axis=1)
    return working["expected_pass"]


def compute_team_week_scheme(pbp: pd.DataFrame, config: SchemeConfig | None = None) -> pd.DataFrame:
    if pbp.empty:
        return pd.DataFrame(
            columns=["team", "season", "week", "proe", "ed_pass_rate", "pace", "plays"]
        )

    cfg = config or SchemeConfig(seasons=sorted(pbp["season"].dropna().unique()))
    working = pbp.copy()
    working = working.dropna(subset=["posteam", "season", "week", "down"])
    working = working[working["down"].isin(cfg.neutral_downs)]
    if working.empty:
        return pd.DataFrame(
            columns=["team", "season", "week", "proe", "ed_pass_rate", "pace", "plays"]
        )

    working["down"] = working["down"].astype(int)
    working["ydstogo"] = pd.to_numeric(working["ydstogo"], errors="coerce")
    working["yardline_100"] = pd.to_numeric(working["yardline_100"], errors="coerce")
    working = working.dropna(subset=["ydstogo", "yardline_100"])
    working["pass_flag"] = working["pass"].fillna(0).astype(int)

    # Expected pass probability per play
    expected = _compute_expected_pass(working)
    working["expected_pass"] = expected.values

    grouped = working.groupby(["posteam", "season", "week"], observed=True)
    actual_pass = grouped["pass_flag"].mean().rename("pass_rate")
    expected_pass = grouped["expected_pass"].mean().rename("expected_pass")
    play_counts = grouped.size().rename("plays")
    proe = (actual_pass - expected_pass).rename("proe")

    early = working[working["down"].isin(cfg.early_downs)]
    if early.empty:
        early_pass = pd.Series(dtype=float)
    else:
        early_pass = (
            early.groupby(["posteam", "season", "week"], observed=True)["pass_flag"]
            .mean()
            .rename("ed_pass_rate")
        )

    # Pace calculation: seconds per offensive play converted to plays per minute
    pace_df = pbp.copy()
    pace_df = pace_df.dropna(
        subset=["game_id", "posteam", "season", "week", "game_seconds_remaining"]
    )
    pace_df = pace_df.sort_values(
        ["game_id", "posteam", "game_seconds_remaining"], ascending=[True, True, False]
    )
    pace_df["next_sec"] = pace_df.groupby(["game_id", "posteam"])["game_seconds_remaining"].shift(1)
    pace_df["seconds_elapsed"] = pace_df["next_sec"] - pace_df["game_seconds_remaining"]
    pace_df = pace_df[(pace_df["seconds_elapsed"] > 0) & (pace_df["seconds_elapsed"] < 90)]
    pace_group = (
        pace_df.groupby(["posteam", "season", "week"], observed=True)["seconds_elapsed"]
        .mean()
        .rename("avg_sp")
    )
    pace = (60 / pace_group).rename("pace")

    result = (
        pd.concat([actual_pass, expected_pass, proe, early_pass, pace, play_counts], axis=1)
        .reset_index()
        .rename(columns={"posteam": "team"})
    )
    result["proe"] = result["proe"].astype(float)
    result["ed_pass_rate"] = result["ed_pass_rate"].astype(float)
    result["pace"] = result["pace"].astype(float)
    result["plays"] = result["plays"].fillna(0).astype(int)
    result = result.sort_values(["team", "season", "week"]).reset_index(drop=True)
    return result


def build_team_week_scheme(seasons: Iterable[int]) -> pd.DataFrame:
    pbp = _load_pbp(seasons)
    if pbp.empty:
        return pd.DataFrame()
    return compute_team_week_scheme(pbp, SchemeConfig(seasons=seasons))


def persist_team_week_scheme(df: pd.DataFrame, database_path: Path) -> None:
    if df.empty:
        return
    database_path.parent.mkdir(parents=True, exist_ok=True)
    df = df.copy()
    df["season"] = pd.to_numeric(df["season"], errors="coerce").astype("Int64")
    df["week"] = pd.to_numeric(df["week"], errors="coerce").astype("Int64")
    df["updated_at"] = datetime.datetime.utcnow().isoformat()
    records = df[
        ["team", "season", "week", "proe", "ed_pass_rate", "pace", "plays", "updated_at"]
    ].to_dict("records")

    with sqlite3.connect(database_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS team_week_scheme (
                team TEXT,
                season INT,
                week INT,
                proe FLOAT,
                ed_pass_rate FLOAT,
                pace FLOAT,
                plays INT,
                updated_at TEXT,
                PRIMARY KEY (team, season, week)
            )
            """
        )
        conn.executemany(
            """
            INSERT INTO team_week_scheme(team, season, week, proe, ed_pass_rate, pace, plays, updated_at)
            VALUES (:team, :season, :week, :proe, :ed_pass_rate, :pace, :plays, :updated_at)
            ON CONFLICT(team, season, week) DO UPDATE SET
                proe=excluded.proe,
                ed_pass_rate=excluded.ed_pass_rate,
                pace=excluded.pace,
                plays=excluded.plays,
                updated_at=excluded.updated_at
            """,
            records,
        )
        conn.commit()
