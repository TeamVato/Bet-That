"""Core odds math utilities used across the project."""
from __future__ import annotations

from typing import Dict, Iterable, List, Tuple


def american_to_decimal(american: int | float) -> float:
    """Convert American odds to stake-inclusive decimal odds.

    Examples
    --------
    ``-110`` -> ``1 + 100/110`` and ``+120`` -> ``1 + 120/100``.
    """

    value = float(american)
    if value == 0:
        raise ValueError("American odds of 0 are undefined")
    return 1.0 + (100.0 / abs(value) if value < 0 else value / 100.0)


def american_to_implied_prob(american: int | float) -> float:
    """Moneyline to implied probability (with vig)."""

    value = float(american)
    if value == 0:
        raise ValueError("American odds of 0 are undefined")
    return (abs(value) / (abs(value) + 100.0)) if value < 0 else (100.0 / (value + 100.0))


def american_to_prob(american: int | float) -> float:
    """Backward compatible alias for :func:`american_to_implied_prob`."""

    return american_to_implied_prob(american)


def decimal_to_prob(decimal_odds: float) -> float:
    """Stake-inclusive decimal to implied probability (``2.00`` -> ``0.5``)."""

    return 1.0 / float(decimal_odds)


def prob_to_decimal(p: float) -> float:
    """Implied probability to decimal odds."""

    if p == 0:
        raise ValueError("Probability of 0 cannot be converted to decimal odds")
    return 1.0 / float(p)


def devig_proportional_from_decimal(
    decimals: Iterable[float],
) -> Tuple[List[Tuple[float, float]], float]:
    """Remove vig via proportional renormalisation of decimal odds.

    Parameters
    ----------
    decimals:
        Iterable of stake-inclusive decimal odds for each outcome in the market.

    Returns
    -------
    tuple
        ``([(p_fair_i, fair_decimal_i), ...], overround)`` where ``p_fair_i`` is the
        fair (no-vig) probability and ``fair_decimal_i`` the corresponding decimal
        price for each entry in ``decimals``. ``overround`` is the implied probability
        sum (bookmaker margin) before renormalisation.
    """

    ds = [float(d) for d in decimals]
    if not ds:
        return [], 0.0
    inv = [1.0 / d for d in ds]
    overround = sum(inv)
    if overround == 0:
        return [(0.0, float("inf")) for _ in ds], 0.0
    p_fair = [x / overround for x in inv]
    fair_dec = [1.0 / p for p in p_fair]
    return list(zip(p_fair, fair_dec)), overround


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

    decimals = [american_to_decimal(odds_a), american_to_decimal(odds_b)]
    pairs, _ = devig_proportional_from_decimal(decimals)
    if len(pairs) != 2:
        raise ValueError("Expected exactly two outcomes for two-way market")
    return {labels[0]: pairs[0][0], labels[1]: pairs[1][0]}


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
