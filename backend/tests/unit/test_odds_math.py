"""Test suite for core odds mathematics - CRITICAL FINANCIAL LOGIC."""

import math

import pytest

from engine.odds_math import (
    american_to_decimal,
    american_to_implied_prob,
    american_to_prob,
    decimal_to_prob,
    ev_per_dollar,
    kelly_fraction,
    no_vig_two_way,
    prob_to_decimal,
)


class TestOddsConversions:
    """Test fundamental odds conversion functions."""

    def test_american_to_decimal_favorites(self):
        """Test conversion for favorites (negative American odds)."""
        # Standard examples
        assert american_to_decimal(-110) == pytest.approx(1.909, abs=0.01)
        assert american_to_decimal(-200) == pytest.approx(1.50, abs=0.01)
        assert american_to_decimal(-150) == pytest.approx(1.667, abs=0.01)

        # Edge cases
        assert american_to_decimal(-100) == pytest.approx(2.0, abs=0.01)
        assert american_to_decimal(-1000) == pytest.approx(1.10, abs=0.01)

    def test_american_to_decimal_underdogs(self):
        """Test conversion for underdogs (positive American odds)."""
        # Standard examples
        assert american_to_decimal(110) == pytest.approx(2.10, abs=0.01)
        assert american_to_decimal(200) == pytest.approx(3.00, abs=0.01)
        assert american_to_decimal(150) == pytest.approx(2.50, abs=0.01)

        # Edge cases
        assert american_to_decimal(100) == pytest.approx(2.0, abs=0.01)
        assert american_to_decimal(1000) == pytest.approx(11.0, abs=0.01)

    def test_american_to_decimal_zero_error(self):
        """Test that zero odds raise ValueError."""
        with pytest.raises(ValueError, match="American odds of 0 are undefined"):
            american_to_decimal(0)

    def test_american_to_implied_prob_favorites(self):
        """Test implied probability calculations for favorites."""
        # -110 odds should be ~52.38% implied probability
        prob = american_to_implied_prob(-110)
        assert 0.523 < prob < 0.525

        # -200 odds should be ~66.67% implied probability
        prob = american_to_implied_prob(-200)
        assert 0.666 < prob < 0.668

    def test_american_to_implied_prob_underdogs(self):
        """Test implied probability calculations for underdogs."""
        # +110 odds should be ~47.62% implied probability
        prob = american_to_implied_prob(110)
        assert 0.476 < prob < 0.477

        # +200 odds should be ~33.33% implied probability
        prob = american_to_implied_prob(200)
        assert 0.333 < prob < 0.334

    def test_decimal_prob_conversions(self):
        """Test decimal odds to probability conversions."""
        # 2.0 decimal = 50% probability
        assert decimal_to_prob(2.0) == pytest.approx(0.5, abs=0.001)

        # 1.5 decimal = 66.67% probability
        assert decimal_to_prob(1.5) == pytest.approx(0.667, abs=0.001)

        # Round trip conversion
        prob = 0.6
        decimal = prob_to_decimal(prob)
        assert decimal_to_prob(decimal) == pytest.approx(prob, abs=0.001)

    def test_prob_to_decimal_zero_error(self):
        """Test that zero probability raises ValueError."""
        with pytest.raises(ValueError, match="Probability of 0 cannot be converted"):
            prob_to_decimal(0)


class TestNoVigCalculations:
    """Test no-vig (fair) odds calculations."""

    def test_no_vig_two_way_standard(self):
        """Test no-vig calculation for typical two-way market."""
        # Both sides -110 (overround ~104.76%)
        result = no_vig_two_way(-110, -110)

        # Should be close to 50/50 after removing vig
        assert abs(result["a"] - 0.5) < 0.01
        assert abs(result["b"] - 0.5) < 0.01
        assert abs(result["a"] + result["b"] - 1.0) < 0.001

    def test_no_vig_two_way_favorites(self):
        """Test no-vig with clear favorite/underdog."""
        # -200 favorite vs +150 underdog
        result = no_vig_two_way(-200, 150)

        # Favorite should have higher probability
        assert result["a"] > result["b"]
        assert result["a"] > 0.6  # Should be significant favorite
        assert abs(result["a"] + result["b"] - 1.0) < 0.001

    def test_no_vig_custom_labels(self):
        """Test no-vig with custom labels."""
        result = no_vig_two_way(-110, -110, labels=("over", "under"))

        assert "over" in result
        assert "under" in result
        assert len(result) == 2


class TestExpectedValue:
    """Test expected value calculations - CRITICAL for bet recommendations."""

    def test_ev_positive_edge(self):
        """Test EV calculation with positive edge."""
        # 55% win probability at -110 odds should be +EV
        ev = ev_per_dollar(0.55, -110)
        assert ev > 0, "55% win rate at -110 should be profitable"

        # Should be approximately +5% EV
        assert 0.04 < ev < 0.06

    def test_ev_negative_edge(self):
        """Test EV calculation with negative edge."""
        # 50% win probability at -110 odds should be -EV (due to vig)
        ev = ev_per_dollar(0.50, -110)
        assert ev < 0, "50% win rate at -110 should be unprofitable due to vig"

    def test_ev_breakeven(self):
        """Test EV at theoretical breakeven."""
        # Calculate breakeven probability for -110
        breakeven_prob = american_to_implied_prob(-110)
        ev = ev_per_dollar(breakeven_prob, -110)
        assert abs(ev) < 0.001, "EV should be ~0 at breakeven probability"

    def test_ev_extreme_cases(self):
        """Test EV with extreme probabilities and odds."""
        # 90% win probability at +200 odds = huge EV
        ev = ev_per_dollar(0.90, 200)
        assert ev > 1.0, "90% win rate at +200 should have massive EV"

        # 10% win probability at -200 odds = huge negative EV
        ev = ev_per_dollar(0.10, -200)
        assert ev < -0.5, "10% win rate at -200 should have terrible EV"


class TestKellyFraction:
    """Test Kelly criterion calculations - CRITICAL for bet sizing."""

    def test_kelly_positive_edge(self):
        """Test Kelly fraction with positive edge."""
        # 55% probability, even odds (100)
        kelly = kelly_fraction(0.55, 100)
        assert 0 < kelly < 0.2, f"Kelly should be positive but reasonable: {kelly}"

        # Should be approximately 2.5% of bankroll (25% of full Kelly)
        assert 0.02 < kelly < 0.04

    def test_kelly_no_edge(self):
        """Test Kelly fraction with no edge."""
        # Breakeven probability at given odds
        kelly = kelly_fraction(0.5, 100)  # 50% at even odds
        assert abs(kelly) < 0.01, "Kelly should be ~0 with no edge"

    def test_kelly_negative_edge(self):
        """Test Kelly fraction with negative edge."""
        # Bad bet should recommend 0% allocation
        kelly = kelly_fraction(0.4, 100)  # 40% at even odds
        assert kelly == 0.0, "Kelly should be 0 for negative edge bets"

    def test_kelly_extreme_edge(self):
        """Test Kelly fraction caps at reasonable levels."""
        # Huge edge should still be capped
        kelly = kelly_fraction(0.9, 100)  # 90% at even odds
        assert kelly <= 1.0, "Kelly should never exceed 100% of bankroll"

    def test_kelly_zero_odds(self):
        """Test Kelly with zero or negative decimal odds (after conversion)."""
        # Zero American odds are invalid and should raise error
        with pytest.raises(ValueError):
            kelly_fraction(0.6, 0)

        # Very negative odds should work but give small Kelly
        kelly = kelly_fraction(0.6, -1000)  # Very heavy favorite
        assert kelly >= 0.0, "Kelly should be non-negative for valid odds"


class TestIntegration:
    """Test integration of multiple odds math functions."""

    def test_round_trip_conversions(self):
        """Test that conversions are consistent in both directions."""
        test_odds = [-500, -200, -110, 100, 150, 300]

        for odds in test_odds:
            # American -> Decimal -> Probability -> Decimal -> Implied prob
            decimal = american_to_decimal(odds)
            prob_from_decimal = decimal_to_prob(decimal)
            prob_from_american = american_to_implied_prob(odds)

            # Should be approximately equal
            assert abs(prob_from_decimal - prob_from_american) < 0.001

    def test_ev_kelly_consistency(self):
        """Test that EV and Kelly are consistent."""
        # If EV is positive, Kelly should be positive
        # If EV is negative, Kelly should be 0

        test_cases = [
            (0.6, -110),  # Positive EV
            (0.45, -110),  # Negative EV
            (0.55, 200),  # Positive EV, underdog
        ]

        for prob, odds in test_cases:
            ev = ev_per_dollar(prob, odds)
            kelly = kelly_fraction(prob, odds)

            if ev > 0:
                assert kelly > 0, f"Positive EV ({ev}) should have positive Kelly ({kelly})"
            else:
                assert kelly == 0, f"Negative EV ({ev}) should have zero Kelly ({kelly})"

    def test_overround_detection(self):
        """Test that we can detect overround in markets."""
        # Two-way market with typical vig
        prob_a = american_to_implied_prob(-110)
        prob_b = american_to_implied_prob(-110)
        overround = prob_a + prob_b

        # Should be > 1.0 due to vig
        assert overround > 1.0, "Two-way market with vig should have overround > 1"
        assert overround < 1.1, "Overround should be reasonable (< 10%)"

    def test_edge_calculation_accuracy(self):
        """Test edge calculation using real-world scenario."""
        # Scenario: 55% model probability vs -110 market odds
        model_prob = 0.55
        market_odds = -110
        market_prob = american_to_implied_prob(market_odds)

        edge = model_prob - market_prob
        ev = ev_per_dollar(model_prob, market_odds)

        # Edge should be positive
        assert edge > 0, "55% model vs -110 market should show positive edge"

        # EV should be positive
        assert ev > 0, "Positive edge should result in positive EV"

        # Edge and EV should be correlated
        assert edge > 0.02, "Edge should be meaningful (>2%)"


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        # Test None inputs
        with pytest.raises((ValueError, TypeError)):
            american_to_decimal(None)

        # Test string inputs that should fail
        with pytest.raises((ValueError, TypeError)):
            american_to_decimal("invalid")

    def test_extreme_values(self):
        """Test handling of extreme but valid values."""
        # Very large odds
        large_decimal = american_to_decimal(10000)
        assert large_decimal == pytest.approx(101.0, abs=0.1)

        # Very small probabilities
        tiny_prob = american_to_implied_prob(10000)
        assert 0 < tiny_prob < 0.01

    def test_numerical_precision(self):
        """Test numerical precision for financial calculations."""
        # Kelly fraction should be precise for small edges
        kelly = kelly_fraction(0.501, 100)  # Tiny edge
        assert isinstance(kelly, float)
        assert kelly >= 0

        # EV should maintain precision
        ev = ev_per_dollar(0.5001, -110)  # Tiny edge
        assert isinstance(ev, float)
