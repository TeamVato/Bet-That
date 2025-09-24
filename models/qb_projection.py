"""Simple QB passing yards projection model."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Iterable, Optional

import sqlite3

import numpy as np
import pandas as pd
from scipy.stats import norm

from adapters.news_flags import load_player_flags
from adapters.weather_provider import WeatherInfo, get_weather_for_game


def apply_qb_defense_adjustment(qb_mean_yards, opponent_def_code, season, week, beta=0.10):
    """
    Multiply qb_mean_yards by a capped factor based on defense_ratings (pos='QB_PASS').
    score > 0 => more generous (increase); score < 0 => stingy (decrease).
    beta is the sensitivity; keep small. Hard-cap effect to ±15%.
    """
    db_path = Path("storage/odds.db")
    if not db_path.exists():
        return qb_mean_yards
    if not opponent_def_code or season is None or week is None:
        return qb_mean_yards
    try:
        with sqlite3.connect(db_path) as con:
            dr = pd.read_sql(
                """
                SELECT score, tier
                FROM defense_ratings
                WHERE defteam = ? AND season = ? AND week = ? AND pos = 'QB_PASS'
                """,
                con,
                params=[str(opponent_def_code).strip().upper(), season, week],
            )
        if not dr.empty and pd.notna(dr.iloc[0]["score"]):
            adj = 1.0 + beta * float(dr.iloc[0]["score"])
            adj = max(0.85, min(1.15, adj))  # cap ±15%
            return qb_mean_yards * adj
    except Exception:
        pass  # fail open if DB missing, etc.
    return qb_mean_yards


@dataclass
class ProjectionConfig:
    baseline_games: int = 8
    weather_fn: Callable[..., WeatherInfo] = get_weather_for_game
    news_flags_path: Path = Path("storage/player_flags.yaml")


class QBProjectionModel:
    """Very small, interpretable QB projection model."""

    def __init__(
        self,
        game_logs: pd.DataFrame,
        schedule_lookup: Dict[str, Dict[str, Optional[str]]],
        config: ProjectionConfig,
    ) -> None:
        self.game_logs = game_logs.copy()
        self.schedule_lookup = schedule_lookup
        self.config = config
        self.player_flags = load_player_flags(config.news_flags_path)
        self.league_avg = self._compute_league_average()
        self.defense_metrics = self._compute_defense_metrics()

    def _compute_league_average(self) -> float:
        if self.game_logs.empty or "passing_yards" not in self.game_logs.columns:
            return 240.0
        values = pd.to_numeric(self.game_logs["passing_yards"], errors="coerce").dropna()
        if values.empty:
            return 240.0
        return float(values.mean())

    def _compute_defense_metrics(self) -> Dict[str, float]:
        metrics: Dict[str, float] = {}
        if self.game_logs.empty:
            return metrics
        df = self.game_logs.copy()
        df["passing_yards"] = pd.to_numeric(df["passing_yards"], errors="coerce")
        grouped = df.groupby("opponent_team")["passing_yards"].mean()
        for team, val in grouped.items():
            metrics[str(team)] = float(val)
        metrics["__league_avg__"] = self.league_avg
        return metrics

    def _apply_defense_adjustment(
        self,
        mu: float,
        def_team: Optional[str],
        season: Optional[int],
        week: Optional[int],
    ) -> float:
        if def_team and season is not None and week is not None:
            return apply_qb_defense_adjustment(
                qb_mean_yards=mu,
                opponent_def_code=def_team,
                season=season,
                week=week,
            )
        if not def_team:
            return mu
        defense_avg = self.defense_metrics.get(def_team)
        league_avg = self.defense_metrics.get("__league_avg__", self.league_avg)
        if not defense_avg or not league_avg:
            return mu
        delta = (league_avg - defense_avg) / league_avg
        return mu * (1 + 0.35 * delta)

    def _apply_weather(self, mu: float, event_id: str) -> float:
        weather = self.config.weather_fn(event_id=event_id)
        adjusted = mu
        if weather.wind_mph >= 15:
            adjusted *= 0.95
        if weather.temperature_f <= 25:
            adjusted *= 0.97
        return adjusted

    def _apply_news_flags(self, mu: float, player: str) -> float:
        flags = self.player_flags.get(player)
        if not flags:
            return mu
        snap_multiplier = float(flags.get("snap_cap_multiplier", 1.0))
        return mu * snap_multiplier

    def _player_recent_games(self, player: str, season: Optional[int]) -> pd.DataFrame:
        if self.game_logs.empty:
            return pd.DataFrame(columns=self.game_logs.columns)
        df = self.game_logs
        mask = df["player_name"].str.lower() == player.lower()
        if season is not None and "season" in df.columns:
            mask &= df["season"] == season
        return df.loc[mask].sort_values("week").tail(self.config.baseline_games)

    def _estimate_sigma(self, recent_games: pd.DataFrame, mu: float) -> float:
        if recent_games.empty:
            return 55.0
        values = pd.to_numeric(recent_games["passing_yards"], errors="coerce").dropna()
        if values.empty:
            return 55.0
        residuals = values - mu
        rmse = float(np.sqrt(np.mean(np.square(residuals))))
        if np.isnan(rmse) or rmse <= 0:
            rmse = float(values.std(ddof=0))
        rmse = float(np.clip(rmse, 35.0, 80.0))
        return rmse

    def project_player(
        self,
        *,
        event_id: str,
        player: str,
        def_team: Optional[str],
        season: Optional[int],
        week: Optional[int],
        default_line: Optional[float],
    ) -> Dict[str, float]:
        schedule_info = self.schedule_lookup.get(event_id, {})
        if season is None:
            season_lookup = schedule_info.get("season")
            if season_lookup is not None and pd.notna(season_lookup):
                season = int(season_lookup)
        if week is None:
            week_lookup = schedule_info.get("week")
            if week_lookup is not None and pd.notna(week_lookup):
                week = int(week_lookup)
        recent_games = self._player_recent_games(player, season)
        if recent_games.empty:
            mu = default_line or self.league_avg
        else:
            mu = float(pd.to_numeric(recent_games["passing_yards"], errors="coerce").mean())
        mu = self._apply_defense_adjustment(mu, def_team, season, week)
        mu = self._apply_weather(mu, event_id)
        mu = self._apply_news_flags(mu, player)
        sigma = self._estimate_sigma(recent_games, mu)
        baseline_line = default_line or mu
        distribution = norm(loc=mu, scale=sigma)
        p_over = float(1 - distribution.cdf(baseline_line))
        return {
            "event_id": event_id,
            "player": player,
            "mu": mu,
            "sigma": sigma,
            "p_over": p_over,
            "season": season,
            "week": week,
            "def_team": def_team,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def build_projections(self, props_df: pd.DataFrame) -> pd.DataFrame:
        records = []
        for player, group in props_df.groupby("player"):
            event_id = group["event_id"].iloc[0]
            season_series = group.get("season")
            season = (
                int(season_series.dropna().astype(int).iloc[0])
                if season_series is not None and season_series.notna().any()
                else None
            )
            week_series = group.get("week")
            week = (
                int(week_series.dropna().astype(int).iloc[0])
                if week_series is not None and week_series.notna().any()
                else None
            )
            def_team_series = group.get("def_team")
            def_team = (
                def_team_series.dropna().iloc[0]
                if def_team_series is not None and def_team_series.notna().any()
                else None
            )
            default_line = float(group["line"].mean()) if not group["line"].isna().all() else None
            proj = self.project_player(
                event_id=event_id,
                player=player,
                def_team=def_team,
                season=season,
                week=week,
                default_line=default_line,
            )
            records.append(proj)
        return pd.DataFrame(records)


def build_qb_projections(
    props_df: pd.DataFrame,
    *,
    game_logs: pd.DataFrame,
    schedule_lookup: Dict[str, Dict[str, Optional[str]]],
    config: Optional[ProjectionConfig] = None,
) -> pd.DataFrame:
    config = config or ProjectionConfig()
    model = QBProjectionModel(game_logs=game_logs, schedule_lookup=schedule_lookup, config=config)
    return model.build_projections(props_df)
