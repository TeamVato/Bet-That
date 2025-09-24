"""Helper mappings for aligning team/player names across datasets."""
from __future__ import annotations

from typing import Dict

TEAM_ABBREVIATIONS: Dict[str, str] = {
    "JAX Jaguars": "JAX",
    "Tennessee Titans": "TEN",
    "New York Jets": "NYJ",
    "New York Giants": "NYG",
    "Dallas Cowboys": "DAL",
    "Kansas City Chiefs": "KC",
    "Buffalo Bills": "BUF",
    "Los Angeles Chargers": "LAC",
}


def normalize_team(name: str) -> str:
    """Return a canonical abbreviation when available."""
    return TEAM_ABBREVIATIONS.get(name, name)
