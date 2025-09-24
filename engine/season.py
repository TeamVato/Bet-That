from __future__ import annotations

import pandas as pd


def infer_season_series(commence_series: pd.Series | None) -> pd.Series:
    """Infer NFL season from a Series of commence timestamps.

    August through December map to the same calendar year, while January through
    July map to the previous year. Invalid or missing timestamps yield a nullable
    integer series of ``pd.NA`` values.
    """

    if commence_series is None:
        return pd.Series(pd.NA, dtype="Int64")

    ts = pd.to_datetime(commence_series, utc=True, errors="coerce")
    years = ts.dt.year
    seasons = years.where(ts.dt.month >= 8, years - 1)
    return seasons.astype("Int64")


def infer_season(commence_ts: str | None) -> int | None:
    """Scalar helper built on :func:`infer_season_series`."""

    if commence_ts is None:
        return None
    series = infer_season_series(pd.Series([commence_ts]))
    value = series.iloc[0] if not series.empty else pd.NA
    if pd.isna(value):
        return None
    return int(value)
