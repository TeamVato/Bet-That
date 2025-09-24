"""Build QB projections and compute edges from props odds."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import os
from pathlib import Path
import sqlite3

import pandas as pd
from dotenv import load_dotenv

from adapters.nflverse_provider import build_event_lookup, get_player_game_logs, get_schedules
from adapters.odds.csv_props_provider import CsvQBPropsAdapter
from db.migrate import migrate, parse_database_url
from engine.edge_engine import EdgeEngine, EdgeEngineConfig
from models.qb_projection import ProjectionConfig, build_qb_projections


TEAM_CODE_FIXES = {
    "LVR": "LV",
    "OAK": "LV",
    "STL": "LA",
    "SD": "LAC",
    "SDC": "LAC",
    "WSH": "WAS",
    "JAC": "JAX",
    "KCC": "KC",
    "TBB": "TB",
    "NWE": "NE",
    "GNB": "GB",
}


def normalize_team_code(code: str) -> str:
    if not isinstance(code, str):
        return code
    code = code.strip().upper()
    return TEAM_CODE_FIXES.get(code, code)


def get_database_path() -> Path:
    load_dotenv()
    url = os.getenv("DATABASE_URL", "sqlite:///storage/odds.db")
    return parse_database_url(url)


def persist_projections(projections: pd.DataFrame, database_path: Path) -> None:
    if projections.empty:
        return
    import sqlite3

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        for row in projections.to_dict("records"):
            cursor.execute(
                """
                INSERT OR REPLACE INTO projections_qb (
                    event_id, player, mu, sigma, p_over, season, def_team, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("event_id"),
                    row.get("player"),
                    row.get("mu"),
                    row.get("sigma"),
                    row.get("p_over"),
                    row.get("season"),
                    row.get("def_team"),
                    row.get("updated_at"),
                ),
            )
        conn.commit()


def main() -> None:
    database_path = get_database_path()
    migrate()

    adapter = CsvQBPropsAdapter()
    props_df = adapter.fetch()
    adapter.persist(props_df, database_path)

    seasons_env = os.getenv("DEFAULT_SEASONS", "2023,2024")
    seasons = [int(s.strip()) for s in seasons_env.split(",") if s.strip()]
    schedule = get_schedules(seasons)
    schedule_lookup = build_event_lookup(schedule)
    game_logs = get_player_game_logs(seasons)

    projection_config = ProjectionConfig()
    projections = build_qb_projections(
        props_df,
        game_logs=game_logs,
        schedule_lookup=schedule_lookup,
        config=projection_config,
    )
    persist_projections(projections, database_path)

    engine = EdgeEngine(EdgeEngineConfig(database_path=database_path))
    edges_df = engine.compute_edges(props_df, projections)
    for col in ("season", "week"):
        if col in edges_df.columns:
            edges_df[col] = pd.to_numeric(edges_df[col], errors="coerce").astype("Int64")
    if "opponent_def_code" in edges_df.columns:
        edges_df["opponent_def_code"] = edges_df["opponent_def_code"].apply(normalize_team_code)
    try:
        with sqlite3.connect(database_path) as con:
            dr = pd.read_sql(
                "SELECT defteam, season, week, pos, tier, score FROM defense_ratings",
                con,
            )
        dr["season"] = pd.to_numeric(dr["season"], errors="coerce").astype("Int64")
        dr["week"] = pd.to_numeric(dr["week"], errors="coerce").astype("Int64")
        dr["defteam"] = dr["defteam"].apply(normalize_team_code)
        qb_ratings = dr.loc[dr["pos"] == "QB_PASS", ["defteam", "season", "week", "tier", "score"]]
        edges_df = (
            edges_df.merge(
                qb_ratings,
                how="left",
                left_on=["opponent_def_code", "season", "week"],
                right_on=["defteam", "season", "week"],
            )
            .rename(columns={"tier": "def_tier", "score": "def_score"})
            .drop(columns=["defteam"], errors="ignore")
        )
        missing_mask = (
            edges_df["def_tier"].isna()
            & edges_df["season"].notna()
            & edges_df["opponent_def_code"].notna()
        )
        if missing_mask.any():
            latest = (
                qb_ratings.dropna(subset=["week"])
                .sort_values("week")
                .drop_duplicates(subset=["defteam", "season"], keep="last")
            )
            tier_lookup = {
                (row["defteam"], row["season"]): row["tier"]
                for _, row in latest.iterrows()
            }
            score_lookup = {
                (row["defteam"], row["season"]): row["score"]
                for _, row in latest.iterrows()
            }
            for idx in edges_df.index[missing_mask]:
                key = (edges_df.at[idx, "opponent_def_code"], edges_df.at[idx, "season"])
                if key in tier_lookup:
                    edges_df.at[idx, "def_tier"] = tier_lookup[key]
                    edges_df.at[idx, "def_score"] = score_lookup[key]
    except Exception as exc:
        print(f"Warning: unable to merge defense ratings ({exc})")
    for col in ("def_tier", "def_score"):
        if col not in edges_df.columns:
            edges_df[col] = pd.NA
    if "def_score" in edges_df.columns:
        edges_df["def_score"] = pd.to_numeric(edges_df["def_score"], errors="coerce")
    engine.persist_edges(edges_df)
    engine.export(edges_df)

    print("Edge computation complete.")


if __name__ == "__main__":
    main()
