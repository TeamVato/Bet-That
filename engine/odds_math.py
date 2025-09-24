"""Core odds math utilities used across the project."""
from __future__ import annotations

from typing import Dict, Tuple


def american_to_decimal(odds: int | float) -> float:
    """Convert American odds to decimal odds."""
    odds_value = float(odds)
    if odds_value > 0:
        return 1 + odds_value / 100
    if odds_value < 0:
        return 1 + 100 / abs(odds_value)
    raise ValueError("American odds of 0 are undefined")


def american_to_prob(odds: int | float) -> float:
    """Convert American odds to the implied probability (with vig)."""
    decimal = american_to_decimal(odds)
    return 1 / decimal


def no_vig_two_way(
    odds_a: int | float,
    odds_b: int | float,
    labels: Tuple[str, str] = ("a", "b"),
) -> Dict[str, float]:
    """Return no-vig probabilities for a two-way market.

    Parameters
    ----------
    odds_a, odds_b:
        The American odds for each side of the market.
    labels:
        Output labels for the two sides.
    """

    prob_a = american_to_prob(odds_a)
    prob_b = american_to_prob(odds_b)
    denom = prob_a + prob_b
    if denom == 0:
        raise ValueError("Both implied probabilities are zero")
    normalized_a = prob_a / denom
    normalized_b = prob_b / denom
    return {labels[0]: normalized_a, labels[1]: normalized_b}


def ev_per_dollar(p_true: float, odds: int | float) -> float:
    """Expected value per dollar staked given a true win probability."""
    decimal = american_to_decimal(odds)
    payout = decimal - 1
    return p_true * payout - (1 - p_true)


def kelly_fraction(p_true: float, odds: int | float, *, fraction: float = 0.25) -> float:
    """Fractional Kelly staking recommendation."""
    decimal = american_to_decimal(odds)
    b = decimal - 1
    if b == 0:
        return 0.0
    full_kelly = (p_true * (b + 1) - 1) / b
    kelly = max(0.0, full_kelly) * fraction
    return kelly
