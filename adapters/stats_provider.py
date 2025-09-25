"""Robust adapter for weekly player stats across nfl_data_py versions."""
from __future__ import annotations

import pandas as pd

EXPECTED_COLUMNS = ["season", "week", "player_id", "team", "position"]


try:  # pragma: no cover - import guard
    import nfl_data_py as nfl
except ImportError:  # pragma: no cover
    nfl = None  # type: ignore


def import_weekly_stats(seasons):
    """Try several function names across nfl_data_py versions.

    Returns an empty frame with expected columns when no provider succeeds.
    """

    if nfl is None:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    for fn_name in [
        "import_weekly_player_stats",
        "import_player_weekly",
        "import_player_stats",
    ]:
        fn = getattr(nfl, fn_name, None)
        if callable(fn):
            try:
                return fn(seasons)
            except Exception:
                continue

    return pd.DataFrame(columns=EXPECTED_COLUMNS)
