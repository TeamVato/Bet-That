"""Detect notable line movement (steam) from the odds history."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List

import pandas as pd


def load_recent_history(database_path: Path) -> pd.DataFrame:
    with sqlite3.connect(database_path) as conn:
        return pd.read_sql_query("SELECT * FROM odds_snapshots ORDER BY fetched_at DESC", conn)


def detect_steam(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(
            columns=[
                "event_id",
                "market_key",
                "bookmaker_key",
                "outcome",
                "price_change",
                "line_change",
                "latest_price",
                "latest_points",
                "fetched_at",
            ]
        )
    df = df.copy()
    df["fetched_at"] = pd.to_datetime(df["fetched_at"], errors="coerce")
    df.sort_values("fetched_at", inplace=True)
    alerts: List[dict] = []
    group_cols = ["event_id", "market_key", "bookmaker_key", "outcome"]
    for _, group in df.groupby(group_cols):
        if len(group) < 2:
            continue
        latest = group.iloc[-1]
        previous = group.iloc[-2]
        price_change = float(latest.get("price", 0) or 0) - float(previous.get("price", 0) or 0)
        line_change = float(latest.get("line", 0) or 0) - float(previous.get("line", 0) or 0)
        if abs(price_change) >= 20 or abs(line_change) >= 0.5:
            alerts.append(
                {
                    "event_id": latest.get("event_id"),
                    "market_key": latest.get("market_key"),
                    "bookmaker_key": latest.get("bookmaker_key"),
                    "outcome": latest.get("outcome"),
                    "price_change": price_change,
                    "line_change": line_change,
                    "latest_price": latest.get("price"),
                    "latest_points": latest.get("line"),
                    "fetched_at": latest.get("fetched_at"),
                }
            )
    return pd.DataFrame(alerts)


def export_alerts(alerts: pd.DataFrame, export_dir: Path = Path("storage/exports")) -> Path:
    export_dir.mkdir(parents=True, exist_ok=True)
    path = export_dir / "steam_alerts.csv"
    alerts.to_csv(path, index=False)
    return path
