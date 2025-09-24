"""Simple QB passing yards projection model."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Iterable, Optional

import numpy as np
import pandas as pd
from scipy.stats import norm

from adapters.news_flags import load_player_flags
from adapters.weather_provider import WeatherInfo, get_weather_for_game


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

    def _apply_defense_adjustment(self, mu: float, def_team: Optional[str]) -> float:
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
        default_line: Optional[float],
    ) -> Dict[str, float]:
        recent_games = self._player_recent_games(player, season)
        if recent_games.empty:
            mu = default_line or self.league_avg
        else:
            mu = float(pd.to_numeric(recent_games["passing_yards"], errors="coerce").mean())
        mu = self._apply_defense_adjustment(mu, def_team)
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
            "def_team": def_team,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def build_projections(self, props_df: pd.DataFrame) -> pd.DataFrame:
        records = []
        for player, group in props_df.groupby("player"):
            event_id = group["event_id"].iloc[0]
            season = group.get("season").dropna().astype(int).iloc[0] if group.get("season").notna().any() else None
            def_team = group.get("def_team").dropna().iloc[0] if group.get("def_team").notna().any() else None
            default_line = float(group["line"].mean()) if not group["line"].isna().all() else None
            proj = self.project_player(
                event_id=event_id,
                player=player,
                def_team=def_team,
                season=season,
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
