"""Utilities for normalizing NFL team codes and event metadata."""

from __future__ import annotations

from typing import Optional, Tuple

TEAM_CODE_FIXES = {
    "LVR": "LV",
    "OAK": "LV",
    "STL": "LA",
    "SD": "LAC",
    "SDC": "LAC",
    "WSH": "WAS",
    "JAC": "JAX",
    "KCC": "KC",
    "TBB": "TB",
    "NWE": "NE",
    "GNB": "GB",
}


def normalize_team_code(code: Optional[str]) -> Optional[str]:
    """Return a standardized two- or three-letter team code."""
    if code is None:
        return None
    value = str(code).strip().upper()
    if not value:
        return None
    return TEAM_CODE_FIXES.get(value, value)


def parse_event_id(event_id: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Split an event_id like '2023-01-01-KC-LV' into (date, away, home)."""
    if not event_id or not isinstance(event_id, str):
        return None, None, None
    parts = event_id.strip().split("-")
    if len(parts) < 5:
        return None, None, None
    date_str = "-".join(parts[:3])
    away = parts[3].upper()
    home = parts[4].upper()
    return date_str, away, home


def infer_offense_team(event_id: Optional[str], defense_team: Optional[str]) -> Optional[str]:
    """Infer the offense team given the opponent and event metadata."""
    _, away, home = parse_event_id(event_id)
    if not away and not home:
        return None
    def_norm = normalize_team_code(defense_team)
    away_norm = normalize_team_code(away)
    home_norm = normalize_team_code(home)
    if def_norm and home_norm and def_norm == home_norm and away:
        return away
    if def_norm and away_norm and def_norm == away_norm and home:
        return home
    return away or home


def infer_is_home(event_id: Optional[str], offense_team: Optional[str]) -> Optional[int]:
    """Derive 1 if offense_team is home, 0 if away, otherwise ``None``."""
    if offense_team is None:
        return None
    _, away, home = parse_event_id(event_id)
    off_norm = normalize_team_code(offense_team)
    if off_norm is None:
        return None
    if home and normalize_team_code(home) == off_norm:
        return 1
    if away and normalize_team_code(away) == off_norm:
        return 0
    return None
