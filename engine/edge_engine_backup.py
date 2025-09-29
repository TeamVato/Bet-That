"""Edge computation by combining model projections with sportsbook odds."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd
from scipy.stats import norm

from engine import odds_math
from utils.teams import infer_is_home, infer_offense_team, normalize_team_code, parse_event_id

SUPPORTED_MARKETS = {
    "player_pass_yds",
    "player_pass_att",
    "player_rush_yds",
    "player_rush_att",
    "player_rec_yds",
    "player_receptions",
}


def _infer_pos(market: object, explicit: object = None) -> str | None:
    if explicit is not None and not (isinstance(explicit, float) and np.isnan(explicit)):
        text = str(explicit).strip()
        if text:
            return text.upper()
    if not isinstance(market, str):
        return None
    text = market.lower()
    if "pass" in text:
        return "QB"
    if "rush" in text or "carry" in text or "attempt" in text:
        return "RB"
    if "rec" in text or "catch" in text:
        return "WR"
    if "tight" in text or " te" in text or text.startswith("te "):
        return "TE"
    return None


@dataclass
class EdgeEngineConfig:
    database_path: Path
    export_dir: Path = Path("storage/exports")
    kelly_cap: float = 0.05


class EdgeEngine:
    """Compute edges for QB prop markets."""

    def __init__(
        self,
        config: EdgeEngineConfig,
        schedule_lookup: Optional[Dict[str, Dict[str, Optional[str]]]] = None,
    ) -> None:
        self.config = config
        self.schedule_lookup = schedule_lookup or {}
        self.config.export_dir.mkdir(parents=True, exist_ok=True)

    def _prepare_dataframe(
        self, props_df: pd.DataFrame, projections_df: pd.DataFrame
    ) -> pd.DataFrame:
        merged = props_df.merge(
            projections_df,
            on=["event_id", "player"],
            how="left",
            suffixes=("_props", "_proj"),
        )
        merged["mu"] = merged["mu"].fillna(merged["line"])
        merged["sigma"] = merged["sigma"].fillna(55.0)
        merged["sigma"] = merged["sigma"].clip(lower=35.0)
        if "market" in merged.columns:
            merged = merged[merged["market"].isin(SUPPORTED_MARKETS)].copy()
        return merged

    def compute_edges(self, props_df: pd.DataFrame, projections_df: pd.DataFrame) -> pd.DataFrame:
        df = self._prepare_dataframe(props_df, projections_df)
        rows = []
        for _, row in df.iterrows():
            if pd.isna(row.get("over_odds")) or pd.isna(row.get("under_odds")):
                continue
            market = row.get("market")
            pos_sources = [
                row.get("pos"),
                row.get("pos_props"),
                row.get("pos_proj"),
            ]
            explicit_pos = next(
                (val for val in pos_sources if isinstance(val, str) and val.strip()), None
            )
            pos = _infer_pos(market, explicit_pos)
            event_id = row.get("event_id")
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

            opponent_def_code = row.get("def_team_proj")
            if pd.isna(opponent_def_code):
                opponent_def_code = row.get("def_team_props")

            # Schedule-based fallbacks for missing week/opponent data
            if (
                (pd.isna(week_val) or pd.isna(opponent_def_code))
                and event_id
                and self.schedule_lookup
            ):
                # Try direct game_id lookup first
                game_date, away_team_raw, home_team_raw = parse_event_id(event_id)
                schedule_info = self.schedule_lookup.get(event_id)

                # If no direct match, try date-team combination keys
                if not schedule_info and game_date and away_team_raw and home_team_raw:
                    alt_key = f"{game_date}-{away_team_raw}-{home_team_raw}"
                    schedule_info = self.schedule_lookup.get(alt_key)

                if schedule_info:
                    # Use schedule week if missing
                    if pd.isna(week_val) and schedule_info.get("week"):
                        try:
                            week_val = int(schedule_info["week"])
                        except (ValueError, TypeError):
                            pass

                    # Infer opponent defense code from schedule if missing
                    if pd.isna(opponent_def_code) and away_team_raw and home_team_raw:
                        # Get player's offensive team to determine opponent
                        inferred_team = row.get("team_proj")
                        if pd.isna(inferred_team):
                            inferred_team = row.get("team_props")

                        if pd.notna(inferred_team):
                            offense_team_norm = normalize_team_code(inferred_team)
                            away_team_norm = normalize_team_code(away_team_raw)
                            home_team_norm = normalize_team_code(home_team_raw)

                            # Opponent is the team that's not the offense team
                            if offense_team_norm == away_team_norm:
                                opponent_def_code = home_team_norm
                            elif offense_team_norm == home_team_norm:
                                opponent_def_code = away_team_norm

            week_val = int(week_val) if pd.notna(week_val) else None
            opponent_def_code = normalize_team_code(opponent_def_code)
            game_date, away_team_raw, home_team_raw = parse_event_id(event_id)
            away_team = normalize_team_code(away_team_raw)
            home_team = normalize_team_code(home_team_raw)
            inferred_team = row.get("team_proj")
            if pd.isna(inferred_team):
                inferred_team = row.get("team_props")
            offense_team = normalize_team_code(
                inferred_team
                if pd.notna(inferred_team)
                else infer_offense_team(event_id, opponent_def_code)
            )
            is_home_flag = infer_is_home(event_id, offense_team)
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
            if pos == "QB":
                strategy = "AltQB" if abs(line - mu) >= 10 else "BaselineQB"
            else:
                strategy = f"Baseline{pos}" if pos else "Baseline"
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
                    "event_id": event_id,
                    "book": row.get("book"),
                    "player": row.get("player"),
                    "market": market,
                    "pos": pos,
                    "line": line,
                    "odds_side": best_side,
                    "odds": best_odds,
                    "model_p": model_p,
                    "season": season_val,
                    "week": week_val,
                    "opponent_def_code": opponent_def_code,
                    "team": offense_team,
                    "home_team": home_team,
                    "away_team": away_team,
                    "is_home": is_home_flag if is_home_flag is None else int(is_home_flag),
                    "game_date": game_date,
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
            if "team" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN team TEXT")
            if "home_team" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN home_team TEXT")
            if "away_team" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN away_team TEXT")
            if "pos" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN pos TEXT")
            if "is_home" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN is_home INTEGER")
            if "game_date" not in existing_cols:
                alter_statements.append("ALTER TABLE edges ADD COLUMN game_date TEXT")
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
                "pos",
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
                "team",
                "home_team",
                "away_team",
                "is_home",
                "game_date",
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
                        _coerce(row.get("pos")),
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
                        row.get("team"),
                        row.get("home_team"),
                        row.get("away_team"),
                        _coerce(row.get("is_home")),
                        row.get("game_date"),
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
        if "pos" not in export_df.columns:
            export_df["pos"] = pd.NA
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
