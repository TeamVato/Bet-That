"""Utility functions for odds conversion"""


def american_to_decimal(american_odds: int) -> float:
    """
    Convert American odds to decimal odds

    Args:
        american_odds: American format odds (e.g., -110, +150)

    Returns:
        Decimal odds (e.g., 1.91, 2.50)
    """
    if american_odds > 0:
        # Positive American odds
        decimal_odds = (american_odds / 100) + 1
    else:
        # Negative American odds
        decimal_odds = (100 / abs(american_odds)) + 1

    return round(decimal_odds, 3)


def decimal_to_american(decimal_odds: float) -> int:
    """
    Convert decimal odds to American odds

    Args:
        decimal_odds: Decimal format odds (e.g., 1.91, 2.50)

    Returns:
        American odds (e.g., -110, +150)
    """
    if decimal_odds >= 2.0:
        # Convert to positive American odds
        american_odds = int((decimal_odds - 1) * 100)
    else:
        # Convert to negative American odds
        american_odds = int(-100 / (decimal_odds - 1))

    return american_odds
