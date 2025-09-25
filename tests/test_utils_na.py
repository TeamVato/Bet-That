import pandas as pd
from pandas import NA

from app.streamlit_app import _coalesce_na, _str_eq


def test_coalesce_na_basic():
    assert _coalesce_na(NA, None, "Questionable") == "Questionable"
    assert _coalesce_na(None, NA, None, default="—") == "—"


def test_str_eq_na_safe():
    assert _str_eq(None, None) is True
    assert _str_eq(" DAL ", "dal") is True
    assert _str_eq(pd.NA, "x") is False
