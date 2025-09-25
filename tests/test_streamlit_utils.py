from __future__ import annotations

import pandas as pd

from app.streamlit_app import _safe_filter


def test_safe_filter_returns_empty_dataframe() -> None:
    df = pd.DataFrame()
    result = _safe_filter(df, "col", 1)

    assert isinstance(result, pd.DataFrame)
    assert result.empty
    assert list(result.columns) == ["col"]
