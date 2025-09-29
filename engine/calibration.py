from __future__ import annotations

import numpy as np
import pandas as pd


def bucket_calibration(df: pd.DataFrame, p_col: str, y_col: str, n: int = 10) -> pd.DataFrame:
    df = df[[p_col, y_col]].dropna().copy()
    if df.empty:
        return pd.DataFrame(columns=["p_mean", "y_rate", "n"])
    df["bin"] = pd.qcut(df[p_col], q=min(n, max(1, df[p_col].nunique())), duplicates="drop")
    out = (
        df.groupby("bin")
        .agg(p_mean=(p_col, "mean"), y_rate=(y_col, "mean"), n=("bin", "size"))
        .reset_index(drop=True)
    )
    return out


def brier_score(p, y) -> float:
    p = np.asarray(p, dtype=float)
    y = np.asarray(y, dtype=float)
    if p.size == 0:
        return float("nan")
    return float(np.mean((p - y) ** 2))
