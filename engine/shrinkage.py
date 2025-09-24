from __future__ import annotations

import pandas as pd


def consensus_prob(df: pd.DataFrame) -> pd.Series:
    key = ["event_id", "market", "line", "player"]
    p_col = "fair_prob" if "fair_prob" in df.columns else "implied_prob"
    if p_col not in df.columns:
        return pd.Series([None] * len(df), index=df.index)
    return df.groupby(key)[p_col].transform("mean")


def shrink_to_market(p_model: pd.Series, p_consensus: pd.Series, weight: float = 0.35) -> pd.Series:
    weight = float(max(0.0, min(1.0, weight)))
    return (1.0 - weight) * p_model.astype(float) + weight * p_consensus.astype(float)

