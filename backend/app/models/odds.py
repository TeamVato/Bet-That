from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field


class MarketLine(BaseModel):
    bookmaker: str
    price: float
    point: Optional[float] = None


class GameOdds(BaseModel):
    game_id: str = Field(..., alias="id")
    commence_time: datetime
    home_team: str
    away_team: str
    best_spreads: Dict[str, MarketLine]
    best_totals: Dict[str, MarketLine]
    last_updated: datetime

    class Config:
        allow_population_by_field_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}
