"""Stub weather provider with extension hooks for future integrations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class WeatherInfo:
    """Simple weather data container used by the projection model."""

    temperature_f: float = 70.0
    wind_mph: float = 5.0
    precipitation_chance: float = 0.0
    description: str = "Clear"

    @property
    def neutral(self) -> bool:
        return self.wind_mph < 12 and self.temperature_f > 30


def get_weather_for_game(
    event_id: str,
    *,
    api_key: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> WeatherInfo:
    """Return neutral weather values.

    This stub keeps the project offline-friendly while leaving clear TODOs for
    integrating a real weather API such as Visual Crossing or the National
    Weather Service. Callers can replace this function with a richer
    implementation without changing the projection engine.
    """

    # TODO: hook in a real provider using the API key once available.
    return WeatherInfo()
