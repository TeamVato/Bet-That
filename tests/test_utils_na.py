import math

import pandas as pd
from pandas import NA

from app.streamlit_app import _coalesce, _str_eq


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
