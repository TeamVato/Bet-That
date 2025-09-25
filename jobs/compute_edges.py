"""Build QB projections and compute edges from props odds."""
from __future__ import annotations

import datetime
import subprocess
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import os
import sqlite3

import pandas as pd
from dotenv import load_dotenv

from adapters.nflverse_provider import build_event_lookup, get_player_game_logs, get_schedules
from adapters.odds.csv_props_provider import CsvQBPropsAdapter
from db.migrate import migrate, parse_database_url
from engine.edge_engine import EdgeEngine, EdgeEngineConfig
from models.qb_projection import ProjectionConfig, build_qb_projections
from engine.season import infer_season, infer_season_series
from utils.teams import normalize_team_code

def _env_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "y", "yes", "on"}


def ensure_defense_ratings_latest_view(database_path: Path) -> None:
    """Create or refresh the view exposing the latest defensive tiers per season."""

    if not database_path.exists():
        return
    with sqlite3.connect(database_path) as con:
        cur = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='defense_ratings'"
        )
        if cur.fetchone() is None:
            return
        cols = {row[1] for row in con.execute("PRAGMA table_info(defense_ratings)")}
        select_cols = [
            "r.defteam",
            "r.season",
            "r.pos",
            "r.week",
            "r.score",
            "r.tier",
        ]
        if "score_adj" in cols:
            select_cols.append("r.score_adj")
        else:
            select_cols.append("NULL AS score_adj")
        if "tier_adj" in cols:
            select_cols.append("r.tier_adj")
        else:
            select_cols.append("NULL AS tier_adj")
        select_sql = ",\n                   ".join(select_cols)
        con.execute("DROP VIEW IF EXISTS defense_ratings_latest")
        con.execute(
            f"""
            CREATE VIEW defense_ratings_latest AS
            SELECT {select_sql}
            FROM defense_ratings AS r
            WHERE COALESCE(r.week, -1) = (
                SELECT COALESCE(MAX(r2.week), -1)
                FROM defense_ratings AS r2
                WHERE r2.defteam = r.defteam
                  AND r2.season = r.season
                  AND r2.pos = r.pos
            )
            """
        )


def ensure_defense_ratings_artifacts(database_path: Path) -> bool:
    """Ensure defense_ratings table (and view) exist; optionally build on demand."""

    def _table_exists(path: Path, table: str) -> bool:
        if not path.exists():
            return False
        with sqlite3.connect(path) as con:
            cur = con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table,),
            )
            return cur.fetchone() is not None

    if _table_exists(database_path, "defense_ratings"):
        ensure_defense_ratings_latest_view(database_path)
        return True

    if _env_truthy(os.getenv("BUILD_DEFENSE_RATINGS_ON_DEMAND")):
        builder = Path(__file__).resolve().parents[1] / "jobs" / "build_defense_ratings.py"
        print(
            "Defense ratings missing; running jobs/build_defense_ratings.py (BUILD_DEFENSE_RATINGS_ON_DEMAND=1)."
        )
        try:
            subprocess.run([sys.executable, str(builder)], check=True)
        except subprocess.CalledProcessError as exc:
            print(f"Failed to build defense ratings on demand ({exc}).")
            return False
        ensure_defense_ratings_latest_view(database_path)
        return _table_exists(database_path, "defense_ratings")

    print(
        "Warning: defense_ratings table not found. Run `python jobs/build_defense_ratings.py` "
        "or set BUILD_DEFENSE_RATINGS_ON_DEMAND=1 to generate it."
    )
    return False


def current_season(now: datetime.datetime | None = None) -> int:
    now = now or datetime.datetime.now()
    return now.year if now.month >= 8 else now.year - 1


def ensure_edges_season(
    edges_df: pd.DataFrame, props_df: pd.DataFrame, database_path: Path
) -> pd.DataFrame:
    if "season" not in edges_df.columns:
        edges_df["season"] = pd.Series(index=edges_df.index, dtype="Int64")
    missing_mask = edges_df["season"].isna()
    if missing_mask.any():
        if "season" in props_df.columns:
            props_lookup = (
                props_df.dropna(subset=["season"])
                .drop_duplicates(subset=["event_id"])
                .set_index("event_id")["season"]
                .to_dict()
            )
            if props_lookup:
                edges_df.loc[missing_mask, "season"] = edges_df.loc[missing_mask, "event_id"].map(props_lookup)
                missing_mask = edges_df["season"].isna()
        if missing_mask.any():
            try:
                with sqlite3.connect(database_path) as con:
                    raw_df = pd.read_sql_query(
                        "SELECT event_id, commence_time, season FROM odds_csv_raw",
                        con,
                    )
            except sqlite3.DatabaseError:
                raw_df = pd.DataFrame()
            if not raw_df.empty:
                if "season" not in raw_df.columns:
                    raw_df["season"] = pd.NA
                needs_infer = raw_df["season"].isna()
                if needs_infer.any():
                    inferred = infer_season_series(raw_df.loc[needs_infer, "commence_time"])
                    raw_df.loc[needs_infer, "season"] = inferred
                raw_lookup = (
                    raw_df.dropna(subset=["season"])
                    .drop_duplicates(subset=["event_id"])
                    .set_index("event_id")["season"]
                    .to_dict()
                )
                if raw_lookup:
                    edges_df.loc[missing_mask, "season"] = edges_df.loc[missing_mask, "event_id"].map(raw_lookup)
                    missing_mask = edges_df["season"].isna()
    if edges_df["season"].isna().all():
        fallback = current_season()
        edges_df["season"] = fallback
    else:
        if edges_df["season"].isna().any():
            fallback = current_season()
            edges_df["season"] = edges_df["season"].fillna(fallback)
    return edges_df


def apply_defense_defaults(edges_df: pd.DataFrame) -> pd.DataFrame:
    """Ensure defense metadata columns exist with neutral defaults."""
    result = edges_df.copy()
    if "def_tier" in result.columns:
        result["def_tier"] = result["def_tier"].fillna("neutral")
    else:
        result["def_tier"] = "neutral"
    if "def_score" in result.columns:
        result["def_score"] = pd.to_numeric(result["def_score"], errors="coerce").fillna(0.0)
    else:
        result["def_score"] = 0.0
    return result


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
    # Optional market-aware shrinkage toward consensus
    try:
        from engine.shrinkage import consensus_prob, shrink_to_market

        if not edges_df.empty and "model_p" in edges_df.columns:
            p_cons = consensus_prob(edges_df)
            weight = float(os.getenv("SHRINK_TO_MARKET_WEIGHT", "0.35"))
            edges_df["p_model_shrunk"] = shrink_to_market(edges_df["model_p"], p_cons, weight)
    except Exception:
        pass
    edges_df = ensure_edges_season(edges_df, props_df, database_path)
    for col in ("season", "week"):
        if col in edges_df.columns:
            edges_df[col] = pd.to_numeric(edges_df[col], errors="coerce").astype("Int64")
    if "opponent_def_code" in edges_df.columns:
        edges_df["opponent_def_code"] = edges_df["opponent_def_code"].apply(normalize_team_code)

    ratings_available = ensure_defense_ratings_artifacts(database_path)
    if ratings_available:
        try:
            with sqlite3.connect(database_path) as con:
                dr = pd.read_sql("SELECT * FROM defense_ratings", con)
            dr["season"] = pd.to_numeric(dr["season"], errors="coerce").astype("Int64")
            dr["week"] = pd.to_numeric(dr["week"], errors="coerce").astype("Int64")
            dr["defteam"] = dr["defteam"].apply(normalize_team_code)
            qb_ratings = dr.loc[dr["pos"] == "QB_PASS"].copy()
            if "score_adj" in qb_ratings.columns:
                qb_ratings["score_effective"] = qb_ratings["score_adj"].combine_first(qb_ratings["score"])
            else:
                qb_ratings["score_effective"] = qb_ratings["score"]
            if "tier_adj" in qb_ratings.columns:
                qb_ratings["tier_effective"] = qb_ratings["tier_adj"].combine_first(qb_ratings["tier"])
            else:
                qb_ratings["tier_effective"] = qb_ratings["tier"]
            qb_ratings = qb_ratings[[
                "defteam",
                "season",
                "week",
                "tier_effective",
                "score_effective",
            ]]
            edges_df = (
                edges_df.merge(
                    qb_ratings,
                    how="left",
                    left_on=["opponent_def_code", "season", "week"],
                    right_on=["defteam", "season", "week"],
                )
                .rename(columns={"tier_effective": "def_tier", "score_effective": "def_score"})
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
                    (row["defteam"], row["season"]): row["tier_effective"]
                    for _, row in latest.iterrows()
                }
                score_lookup = {
                    (row["defteam"], row["season"]): row["score_effective"]
                    for _, row in latest.iterrows()
                }
                for idx in edges_df.index[missing_mask]:
                    key = (edges_df.at[idx, "opponent_def_code"], edges_df.at[idx, "season"])
                    if key in tier_lookup:
                        edges_df.at[idx, "def_tier"] = tier_lookup[key]
                        edges_df.at[idx, "def_score"] = score_lookup[key]
                if missing_mask.any():
                    try:
                        with sqlite3.connect(database_path) as con:
                            latest_view = pd.read_sql(
                                "SELECT defteam, season, pos, tier, score, score_adj, tier_adj FROM defense_ratings_latest",
                                con,
                            )
                    except Exception:
                        latest_view = pd.DataFrame()
                    if not latest_view.empty:
                        qb_latest = latest_view.loc[latest_view["pos"] == "QB_PASS"].copy()
                        if "score_adj" in qb_latest.columns:
                            qb_latest["score_effective"] = qb_latest["score_adj"].combine_first(
                                qb_latest["score"]
                            )
                        else:
                            qb_latest["score_effective"] = qb_latest["score"]
                        if "tier_adj" in qb_latest.columns:
                            qb_latest["tier_effective"] = qb_latest["tier_adj"].combine_first(
                                qb_latest["tier"]
                            )
                        else:
                            qb_latest["tier_effective"] = qb_latest["tier"]
                        qb_latest = (
                            qb_latest.drop_duplicates(subset=["defteam", "season"], keep="last")
                        )
                        tier_lookup.update(
                            {
                                (row["defteam"], row["season"]): row["tier_effective"]
                                for _, row in qb_latest.iterrows()
                            }
                        )
                        score_lookup.update(
                            {
                                (row["defteam"], row["season"]): row["score_effective"]
                                for _, row in qb_latest.iterrows()
                            }
                        )
                        for idx in edges_df.index[missing_mask]:
                            key = (
                                edges_df.at[idx, "opponent_def_code"],
                                edges_df.at[idx, "season"],
                            )
                            if key in tier_lookup and pd.isna(edges_df.at[idx, "def_tier"]):
                                edges_df.at[idx, "def_tier"] = tier_lookup[key]
                                edges_df.at[idx, "def_score"] = score_lookup[key]
        except Exception as exc:
            print(f"Warning: unable to merge defense ratings ({exc})")

    edges_df = apply_defense_defaults(edges_df)
    engine.persist_edges(edges_df)
    engine.export(edges_df)

    print("Edge computation complete.")


if __name__ == "__main__":
    main()
