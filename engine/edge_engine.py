"""Edge computation by combining model projections with sportsbook odds."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from scipy.stats import norm

from engine import odds_math


@dataclass
class EdgeEngineConfig:
    database_path: Path
    export_dir: Path = Path("storage/exports")
    kelly_cap: float = 0.05


class EdgeEngine:
    """Compute edges for QB prop markets."""

    def __init__(self, config: EdgeEngineConfig) -> None:
        self.config = config
        self.config.export_dir.mkdir(parents=True, exist_ok=True)

    def _prepare_dataframe(self, props_df: pd.DataFrame, projections_df: pd.DataFrame) -> pd.DataFrame:
        merged = props_df.merge(
            projections_df,
            on=["event_id", "player"],
            how="left",
            suffixes=("_props", "_proj"),
        )
        merged["mu"] = merged["mu"].fillna(merged["line"])
        merged["sigma"] = merged["sigma"].fillna(55.0)
        merged["sigma"] = merged["sigma"].clip(lower=35.0)
        return merged

    def compute_edges(self, props_df: pd.DataFrame, projections_df: pd.DataFrame) -> pd.DataFrame:
        df = self._prepare_dataframe(props_df, projections_df)
        rows = []
        for _, row in df.iterrows():
            if pd.isna(row.get("over_odds")) or pd.isna(row.get("under_odds")):
                continue
            mu = float(row.get("mu"))
            sigma = float(row.get("sigma"))
            line = float(row.get("line"))
            season_val = row.get("season_proj")
            if pd.isna(season_val):
                season_val = row.get("season_props")
            season_val = int(season_val) if pd.notna(season_val) else None
            week_val = row.get("week_proj")
            if pd.isna(week_val):
                week_val = row.get("week_props")
            week_val = int(week_val) if pd.notna(week_val) else None
            opponent_def_code = row.get("def_team_proj")
            if pd.isna(opponent_def_code):
                opponent_def_code = row.get("def_team_props")
            if pd.isna(opponent_def_code):
                opponent_def_code = None
            if sigma <= 0:
                sigma = 55.0
            distribution = norm(loc=mu, scale=sigma)
            p_over = float(1 - distribution.cdf(line))
            p_under = float(1 - p_over)
            over_odds = int(row.get("over_odds"))
            under_odds = int(row.get("under_odds"))
            implied_probs = {
                "over": odds_math.american_to_implied_prob(over_odds),
                "under": odds_math.american_to_implied_prob(under_odds),
            }
            fair_pairs, overround = odds_math.devig_proportional_from_decimal(
                [
                    odds_math.american_to_decimal(over_odds),
                    odds_math.american_to_decimal(under_odds),
                ]
            )
            fair_probs = {}
            fair_decimals = {}
            for side, pair in zip(("over", "under"), fair_pairs):
                prob, decimal_price = pair
                fair_probs[side] = prob
                fair_decimals[side] = decimal_price
            ev_over = odds_math.ev_per_dollar(p_over, over_odds)
            ev_under = odds_math.ev_per_dollar(p_under, under_odds)
            kelly_over = min(
                self.config.kelly_cap,
                odds_math.kelly_fraction(p_over, over_odds),
            )
            kelly_under = min(
                self.config.kelly_cap,
                odds_math.kelly_fraction(p_under, under_odds),
            )
            if ev_over >= ev_under:
                best_side = "over"
                best_odds = over_odds
                model_p = p_over
                ev = ev_over
                kelly = kelly_over
            else:
                best_side = "under"
                best_odds = under_odds
                model_p = p_under
                ev = ev_under
                kelly = kelly_under
            strategy = "AltQB" if abs(line - mu) >= 10 else "BaselineQB"
            implied_best = implied_probs.get(best_side)
            fair_best = fair_probs.get(best_side)
            edge_prob = model_p - implied_best if implied_best is not None else None
            edge_fair = model_p - fair_best if fair_best is not None else None
            is_stale_val = row.get("is_stale")
            if (pd.isna(is_stale_val) or is_stale_val is None) and "is_stale_props" in row.index:
                is_stale_val = row.get("is_stale_props")
            if pd.isna(is_stale_val):
                is_stale_val = None
            else:
                is_stale_val = int(is_stale_val)
            rows.append(
                {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "event_id": row.get("event_id"),
                    "book": row.get("book"),
                    "player": row.get("player"),
                    "market": row.get("market"),
                    "line": line,
                    "odds_side": best_side,
                    "odds": best_odds,
                    "model_p": model_p,
                    "season": season_val,
                    "week": week_val,
                    "opponent_def_code": opponent_def_code,
                    "ev_per_dollar": ev,
                    "kelly_frac": kelly,
                    "strategy_tag": strategy,
                    "mu": mu,
                    "sigma": sigma,
                    "p_over": p_over,
                    "p_under": p_under,
                    "implied_prob_over": implied_probs.get("over"),
                    "implied_prob_under": implied_probs.get("under"),
                    "fair_prob_over": fair_probs.get("over"),
                    "fair_prob_under": fair_probs.get("under"),
                    "fair_decimal_over": fair_decimals.get("over"),
                    "fair_decimal_under": fair_decimals.get("under"),
                    "overround": overround if overround else None,
                    "implied_prob": implied_best,
                    "fair_prob": fair_best,
                    "edge_prob": edge_prob,
                    "edge_fair": edge_fair,
                    "is_stale": is_stale_val,
                }
            )
        edges_df = pd.DataFrame(rows)
        return edges_df

    def persist_edges(self, edges_df: pd.DataFrame) -> None:
        if edges_df.empty:
            print("No edges to persist.")
            return
        with sqlite3.connect(self.config.database_path) as conn:
            cursor = conn.cursor()
            # Ensure optional columns exist for enriched metadata
            existing_cols = {row[1] for row in cursor.execute("PRAGMA table_info(edges)")}
            alter_statements = []
            if "season" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN season INT")
            if "week" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN week INT")
            if "opponent_def_code" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN opponent_def_code TEXT")
            if "def_tier" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN def_tier TEXT")
            if "def_score" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN def_score REAL")
            if "implied_prob" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN implied_prob REAL")
            if "fair_prob" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN fair_prob REAL")
            if "overround" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN overround REAL")
            if "is_stale" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN is_stale INTEGER")
            if "edge_prob" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN edge_prob REAL")
            if "edge_fair" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN edge_fair REAL")
            if "p_model_shrunk" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN p_model_shrunk REAL")
            if "implied_prob_over" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN implied_prob_over REAL")
            if "implied_prob_under" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN implied_prob_under REAL")
            if "fair_prob_over" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN fair_prob_over REAL")
            if "fair_prob_under" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN fair_prob_under REAL")
            if "fair_decimal_over" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN fair_decimal_over REAL")
            if "fair_decimal_under" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN fair_decimal_under REAL")
            for statement in alter_statements:
                cursor.execute(statement)
            def _coerce(value):
                return None if pd.isna(value) else value
            insert_columns = [
                "created_at",
                "event_id",
                "book",
                "player",
                "market",
                "line",
                "odds_side",
                "odds",
                "model_p",
                "p_model_shrunk",
                "ev_per_dollar",
                "kelly_frac",
                "strategy_tag",
                "season",
                "week",
                "opponent_def_code",
                "def_tier",
                "def_score",
                "implied_prob",
                "fair_prob",
                "overround",
                "is_stale",
                "edge_prob",
                "edge_fair",
                "implied_prob_over",
                "implied_prob_under",
                "fair_prob_over",
                "fair_prob_under",
                "fair_decimal_over",
                "fair_decimal_under",
            ]
            placeholders = ", ".join(["?"] * len(insert_columns))
            insert_sql = f"INSERT INTO edges ({', '.join(insert_columns)}) VALUES ({placeholders})"
            for row in edges_df.to_dict("records"):
                cursor.execute(
                    insert_sql,
                    (
                        row["created_at"],
                        row["event_id"],
                        row["book"],
                        row["player"],
                        row["market"],
                        row["line"],
                        row["odds_side"],
                        row["odds"],
                        row["model_p"],
                        _coerce(row.get("p_model_shrunk")),
                        row["ev_per_dollar"],
                        row["kelly_frac"],
                        row["strategy_tag"],
                        _coerce(row.get("season")),
                        _coerce(row.get("week")),
                        _coerce(row.get("opponent_def_code")),
                        _coerce(row.get("def_tier")),
                        _coerce(row.get("def_score")),
                        _coerce(row.get("implied_prob")),
                        _coerce(row.get("fair_prob")),
                        _coerce(row.get("overround")),
                        _coerce(row.get("is_stale")),
                        _coerce(row.get("edge_prob")),
                        _coerce(row.get("edge_fair")),
                        _coerce(row.get("implied_prob_over")),
                        _coerce(row.get("implied_prob_under")),
                        _coerce(row.get("fair_prob_over")),
                        _coerce(row.get("fair_prob_under")),
                        _coerce(row.get("fair_decimal_over")),
                        _coerce(row.get("fair_decimal_under")),
                    ),
                )
            conn.commit()
        print(f"Inserted {len(edges_df)} edges into the database")

    def export(self, edges_df: pd.DataFrame) -> None:
        if edges_df.empty:
            print("No edges to export.")
            return
        export_df = edges_df.copy()
        if "season" not in export_df.columns:
            export_df["season"] = pd.NA
        for col in ("def_tier", "def_score"):
            if col not in export_df.columns:
                export_df[col] = pd.NA
        export_cols = list(export_df.columns)
        if "season" not in export_cols:
            export_cols.append("season")
        for col in ("def_tier", "def_score"):
            if col not in export_cols:
                export_cols.append(col)
        export_df = export_df.loc[:, export_cols]
        csv_path = self.config.export_dir / "edges_latest.csv"
        parquet_path = self.config.export_dir / "edges_latest.parquet"
        export_df.to_csv(csv_path, index=False)
        try:
            export_df.to_parquet(parquet_path, index=False)
        except Exception as exc:
            print(f"Failed to write parquet export: {exc}")
        print(f"Exports written to {csv_path} and {parquet_path}")
