"""Export tidy CSV/Parquet files for BI tools."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from db.migrate import parse_database_url

EXPORT_DIR = Path("storage/exports")


def get_database_path() -> Path:
    load_dotenv()
    url = os.getenv("DATABASE_URL", "sqlite:///storage/odds.db")
    return parse_database_url(url)


def export_dataframe(df: pd.DataFrame, name: str) -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = EXPORT_DIR / f"{name}.csv"
    parquet_path = EXPORT_DIR / f"{name}.parquet"
    df.to_csv(csv_path, index=False)
    try:
        df.to_parquet(parquet_path, index=False)
    except Exception as exc:
        print(f"Failed to export {name} as Parquet: {exc}")
    print(f"Exported {name} to {csv_path}")


def main() -> None:
    database_path = get_database_path()
    import sqlite3

    with sqlite3.connect(database_path) as conn:
        edges = pd.read_sql_query(
            "SELECT * FROM edges ORDER BY created_at DESC", conn
        )
        best_lines = pd.read_sql_query("SELECT * FROM current_best_lines", conn)
        line_history = pd.read_sql_query(
            """
            SELECT fetched_at, event_id, market_key, bookmaker_key, outcome, price, points
            FROM odds_snapshots
            ORDER BY fetched_at DESC
            """,
            conn,
        )
        qb_props = pd.read_sql_query("SELECT * FROM qb_props_odds", conn)
        projections = pd.read_sql_query("SELECT * FROM projections_qb", conn)

    export_dataframe(edges, "edges_full")
    export_dataframe(best_lines, "current_best_lines")
    export_dataframe(line_history, "line_history")
    export_dataframe(qb_props, "qb_props_odds")
    export_dataframe(projections, "projections_qb")


if __name__ == "__main__":
    main()
