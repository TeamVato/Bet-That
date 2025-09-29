"""Base classes and utilities for odds provider adapters."""

from __future__ import annotations

import abc
from typing import Any, Dict, Iterable, Optional

import pandas as pd


class OddsAdapter(abc.ABC):
    """Abstract base class for odds providers."""

    @abc.abstractmethod
    def fetch(self, *args: Any, **kwargs: Any) -> pd.DataFrame:
        """Fetch odds data and return a normalized DataFrame."""

    def persist(self, df: pd.DataFrame, *args: Any, **kwargs: Any) -> None:
        """Optional hook to persist data; subclasses may override."""
        return None


class SupportsLineHistory(abc.ABC):
    """Interface for adapters that can append to the odds history store."""

    @abc.abstractmethod
    def persist_snapshots(self, df: pd.DataFrame, **kwargs: Any) -> None:
        """Persist normalized odds snapshots to storage."""


def ensure_columns(df: pd.DataFrame, required: Iterable[str]) -> pd.DataFrame:
    """Raise a helpful error if required columns are missing."""
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"DataFrame missing required columns: {missing}")
    return df


def safe_int(value: Optional[Any]) -> Optional[int]:
    """Convert a value to int when possible, returning None otherwise."""
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def safe_float(value: Optional[Any]) -> Optional[float]:
    """Convert a value to float when possible."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
