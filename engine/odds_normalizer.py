from __future__ import annotations

import pandas as pd

from engine.odds_math import (
    american_to_decimal,
    american_to_implied_prob,
    devig_proportional_from_decimal,
)
from engine.season import infer_season_series

REQUIRED_COLUMNS = [
    "event_id",
    "commence_time",
    "home_team",
    "away_team",
    "player",
    "market",
    "line",
    "side",
    "odds",
    "book",
    "updated_at",
]

OUTPUT_COLUMNS = [
    "event_id",
    "commence_time",
    "home_team",
    "away_team",
    "player",
    "market",
    "line",
    "side",
    "odds",
    "over_odds",
    "under_odds",
    "book",
    "updated_at",
    "implied_prob",
    "fair_prob",
    "overround",
    "is_stale",
    "fair_decimal",
    "x_used",
    "x_remaining",
    "season",
]


def _normalize_side(value: object) -> object:
    if isinstance(value, str):
        value = value.strip()
        return value.title() if value else None
    return value


def _compute_devig(df: pd.DataFrame) -> pd.DataFrame:
    df["fair_prob"] = pd.NA
    df["fair_decimal"] = pd.NA
    df["overround"] = pd.NA
    valid = df["odds"].notna()
    if not valid.any():
        return df
    grouped = df.loc[valid].groupby(
        ["event_id", "market", "book", "line"], dropna=False, sort=False
    )
    for _, group in grouped:
        if len(group) < 2:
            continue
        decimals: list[float] = []
        indices: list[int] = []
        for idx, odds_val in group["odds"].items():
            if pd.isna(odds_val):
                continue
            try:
                decimals.append(american_to_decimal(int(odds_val)))
                indices.append(idx)
            except (ValueError, TypeError):
                continue
        if len(decimals) < 2:
            continue
        pairs, overround = devig_proportional_from_decimal(decimals)
        for idx, (prob, fair_dec) in zip(indices, pairs):
            df.at[idx, "fair_prob"] = prob
            df.at[idx, "fair_decimal"] = fair_dec
            df.at[idx, "overround"] = overround
    return df


def normalize_long_odds(
    df: pd.DataFrame,
    stale_minutes: int = 120,
    *,
    now_ts: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Normalize long-format odds data with season, de-vig, and stale flags."""

    if df.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    data = df.copy()
    for col in REQUIRED_COLUMNS:
        if col not in data.columns:
            data[col] = pd.NA

    # Ensure optional bookkeeping columns exist
    for col in ("x_used", "x_remaining", "season"):
        if col not in data.columns:
            data[col] = pd.NA

    data["line"] = pd.to_numeric(data["line"], errors="coerce")
    data["odds"] = pd.to_numeric(data["odds"], errors="coerce").astype("Int64")
    data["side"] = data["side"].map(_normalize_side)

    updated_at = pd.to_datetime(data["updated_at"], utc=True, errors="coerce")
    data["_updated_at"] = updated_at
    data = data.sort_values("_updated_at")
    dedup_keys = ["event_id", "market", "book", "side", "line"]
    data = data.drop_duplicates(subset=dedup_keys, keep="last")

    # Season inference (respect explicit values when present)
    if "season" in df.columns and df["season"].notna().any():
        data["season"] = pd.to_numeric(data["season"], errors="coerce").astype("Int64")
    else:
        data["season"] = infer_season_series(data.get("commence_time"))

    data["implied_prob"] = data["odds"].apply(
        lambda o: None if pd.isna(o) else american_to_implied_prob(int(o))
    )

    data = _compute_devig(data)

    # Staleness
    if stale_minutes > 0:
        if now_ts is None:
            now_val = pd.Timestamp.utcnow()
        else:
            now_val = pd.Timestamp(now_ts)
        if now_val.tzinfo is None:
            now_val = now_val.tz_localize("UTC")
        else:
            now_val = now_val.tz_convert("UTC")
        delta = now_val - data["_updated_at"]
        stale_series = (delta > pd.to_timedelta(stale_minutes, unit="m")).astype("Int64")
        stale_series[data["_updated_at"].isna()] = pd.NA
    else:
        stale_series = pd.Series(pd.NA, index=data.index, dtype="Int64")
    data["is_stale"] = stale_series

    data["over_odds"] = pd.NA
    data["under_odds"] = pd.NA
    side_lower = data["side"].str.lower()
    over_mask = side_lower == "over"
    under_mask = side_lower == "under"
    data.loc[over_mask, "over_odds"] = data.loc[over_mask, "odds"]
    data.loc[under_mask, "under_odds"] = data.loc[under_mask, "odds"]

    result = data[OUTPUT_COLUMNS].copy()
    result = result.astype(object)
    result = result.where(pd.notna(result), None)
    return result


__all__ = ["normalize_long_odds"]
