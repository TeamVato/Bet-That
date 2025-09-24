from __future__ import annotations

import pandas as pd


def greedy_select(df: pd.DataFrame, max_n: int = 10, corr_keys=("player", "market")) -> pd.DataFrame:
    picked = []
    used = set()
    for _, r in df.sort_values("EV", ascending=False).iterrows():
        key = tuple(r.get(k) for k in corr_keys)
        if key in used:
            continue
        picked.append(r)
        used.add(key)
        if len(picked) >= max_n:
            break
    return pd.DataFrame(picked)


def kelly_fraction(p: float, b: float, frac: float = 0.25) -> float:
    b = float(b)
    if b <= 0:
        return 0.0
    fair_f = (p * (b + 1.0) - 1.0) / b
    fair_f = max(0.0, min(1.0, fair_f))
    return fair_f * float(frac)

