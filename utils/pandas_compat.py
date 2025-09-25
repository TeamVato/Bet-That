"""Utilities to keep pandas usage compatible and FutureWarning-free."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Hashable, Iterable

import pandas as pd


def safe_groupby(
    frame: pd.DataFrame,
    by: Iterable[Hashable] | Hashable,
    *,
    observed: bool = False,
    dropna: bool | None = False,
    sort: bool = False,
    group_keys: bool = False,
    **kwargs: Any,
) -> pd.core.groupby.generic.DataFrameGroupBy:
    """Wrapper around :meth:`DataFrame.groupby` with stable defaults."""

    return frame.groupby(
        by,
        observed=observed,
        dropna=dropna,
        sort=sort,
        group_keys=group_keys,
        **kwargs,
    )


def safe_series_groupby(
    series: pd.Series,
    by: Iterable[Hashable] | Hashable,
    *,
    observed: bool = False,
    dropna: bool | None = False,
    sort: bool = False,
    group_keys: bool = False,
    **kwargs: Any,
) -> pd.core.groupby.generic.SeriesGroupBy:
    """Wrapper for :meth:`Series.groupby` mirroring :func:`safe_groupby`."""

    return series.groupby(
        by,
        observed=observed,
        dropna=dropna,
        sort=sort,
        group_keys=group_keys,
        **kwargs,
    )


def safe_rolling(
    obj: pd.Series | pd.DataFrame,
    window: int,
    *,
    min_periods: int | None = None,
    center: bool = False,
    closed: str | None = None,
    **kwargs: Any,
) -> pd.core.window.rolling.Rolling:
    """Provide explicit ``min_periods`` to avoid future default changes."""

    if min_periods is None:
        min_periods = 1
    return obj.rolling(window=window, min_periods=min_periods, center=center, closed=closed, **kwargs)


@contextmanager
def suppress_future_warnings() -> Any:
    """Context manager to silence FutureWarnings when unavoidable."""

    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        yield


__all__ = [
    "safe_groupby",
    "safe_series_groupby",
    "safe_rolling",
    "suppress_future_warnings",
]
