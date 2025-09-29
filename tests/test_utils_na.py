import math

import pandas as pd
from pandas import NA

from app.streamlit_app import _coalesce, _coalesce_na, _str_eq


def test_coalesce_skips_na_like_values():
    assert _coalesce(NA, None, "Questionable") == "Questionable"
    assert _coalesce(None, NA, None, default="—") == "—"
    assert _coalesce(float("nan"), "", "  ", "Fallback") == "Fallback"
    assert _coalesce("  trimmed  ") == "  trimmed  "
    assert math.isclose(_coalesce(None, 0.0, 1.2), 0.0, rel_tol=1e-9)


def test_str_eq_na_safe():
    assert _str_eq(None, None) is True
    assert _str_eq(" DAL ", "dal") is True
    assert _str_eq(pd.NA, "x") is False


def test_injury_drawer_pandas_na_bugfix():
    """Test the specific injury drawer pandas.NA crash that was reported.

    This test addresses: TypeError: boolean value of NA is ambiguous
    which occurred in render_matchup_expander when using:
    status = inj.get("status") or inj.get("designation")
    """
    # Simulate the exact scenario that caused the crash
    injury_row = {"status": pd.NA, "designation": pd.NA, "player": "Patrick Mahomes"}

    # The original problematic code would have been:
    # status = injury_row.get("status") or injury_row.get("designation")  # CRASHES!

    # The fixed code uses _coalesce_na:
    status = _coalesce_na(
        injury_row.get("status"), injury_row.get("designation"), default="(status unknown)"
    )

    assert status == "(status unknown)"

    # Test with mixed NA and valid data
    injury_row2 = {"status": pd.NA, "designation": "Questionable", "player": "Travis Kelce"}

    status2 = _coalesce_na(
        injury_row2.get("status"), injury_row2.get("designation"), default="(status unknown)"
    )

    assert status2 == "Questionable"
