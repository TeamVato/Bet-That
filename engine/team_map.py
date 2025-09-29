"""Team code normalization for defense ratings merge."""

from __future__ import annotations


def normalize_team_code(x: str) -> str:
    """Return canonical 3-letter codes used by defense_ratings.defteam."""
    if x is None or not x:
        return ""

    code = str(x).strip().upper()
    if not code:
        return ""

    # Canonical mappings to match defense_ratings.defteam format
    CANONICAL_MAPPINGS = {
        # Jacksonville: JAX -> JAC (canonical)
        "JAX": "JAC",
        # Los Angeles Rams: LA -> LAR (when Rams)
        "LA": "LAR",
        # Washington: WSH -> WAS (canonical)
        "WSH": "WAS",
        # Legacy team relocations
        "OAK": "LV",  # Oakland -> Las Vegas
        "SD": "LAC",  # San Diego -> Los Angeles Chargers
        "SDC": "LAC",  # San Diego Chargers variant
        "STL": "LAR",  # St. Louis -> Los Angeles Rams
        # Other common variations
        "LVR": "LV",  # Las Vegas variant
        "KCC": "KC",  # Kansas City variant
        "TBB": "TB",  # Tampa Bay variant
        "NWE": "NE",  # New England variant
        "GNB": "GB",  # Green Bay variant
    }

    return CANONICAL_MAPPINGS.get(code, code)
