"""Build QB projections and compute edges from props odds."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from adapters.nflverse_provider import build_event_lookup, get_player_game_logs, get_schedules
from adapters.odds.csv_props_provider import CsvQBPropsAdapter
from db.migrate import migrate, parse_database_url
from engine.edge_engine import EdgeEngine, EdgeEngineConfig
from models.qb_projection import ProjectionConfig, build_qb_projections


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
    if not database_path.exists():
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
    engine.persist_edges(edges_df)
    engine.export(edges_df)

    print("Edge computation complete.")


if __name__ == "__main__":
    main()
