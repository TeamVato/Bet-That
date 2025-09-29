"""Core mathematical function tests - critical for financial calculations."""

import pytest

from engine.odds_math import (
    american_to_decimal,
    american_to_implied_prob,
    ev_per_dollar,
    kelly_fraction,
)


class TestCoreMath:
    """Test critical mathematical functions."""

    def test_odds_conversion_accuracy(self):
        """Test odds conversion accuracy."""
        assert american_to_decimal(-110) == pytest.approx(1.909, abs=0.01)
        assert american_to_decimal(110) == pytest.approx(2.10, abs=0.01)

    def test_probability_calculations(self):
        """Test probability calculations."""
        assert 0.52 < american_to_implied_prob(-110) < 0.53

    def test_expected_value_positive_edge(self):
        """Test EV calculation with positive edge."""
        ev = ev_per_dollar(0.55, -110)
        assert ev > 0, "55% win rate at -110 should be profitable"

    def test_kelly_criterion_reasonable(self):
        """Test Kelly criterion gives reasonable results."""
        kelly = kelly_fraction(0.55, 100)
        assert 0 < kelly < 0.1, "Kelly should be positive but reasonable"
