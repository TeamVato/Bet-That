"""Odds-related helpers used across Bet-That jobs."""

from __future__ import annotations

import math
from typing import Tuple


def american_to_decimal(american: int) -> float:
    """Convert American odds to decimal odds.

    Raises:
        ValueError: If ``american`` is zero.
    """

    if american == 0:
        raise ValueError("American odds cannot be zero.")
    if american > 0:
        return 1.0 + (american / 100.0)
    return 1.0 + (100.0 / abs(american))


def implied_from_decimal(decimal_odds: float) -> float:
    """Return implied probability from decimal odds."""

    if decimal_odds <= 0:
        raise ValueError("Decimal odds must be positive.")
    return 1.0 / decimal_odds


def proportional_devig_two_way(p_over: float, p_under: float) -> Tuple[float, float]:
    """Allocate vig proportionally across two-way market probabilities.

    Args:
        p_over: Implied probability for the over selection.
        p_under: Implied probability for the under selection.

    Returns:
        Tuple of fair probabilities (over, under) that sum to 1.0 when both inputs
        are positive.
    """

    if p_over < 0 or p_under < 0:
        raise ValueError("Probabilities must be non-negative.")
    total = p_over + p_under
    if total == 0:
        return 0.5, 0.5
    return p_over / total, p_under / total


def logit(probability: float) -> float:
    """Compute the logit (log-odds) for a probability in (0, 1)."""

    if not 0 < probability < 1:
        raise ValueError("Probability must be in the open interval (0, 1).")
    return math.log(probability / (1.0 - probability))


__all__ = [
    "american_to_decimal",
    "implied_from_decimal",
    "proportional_devig_two_way",
    "logit",
]
