from engine.portfolio import kelly_fraction


def test_kelly_basic():
    assert kelly_fraction(0.5, 1.0, 0.5) == 0.0
    assert abs(kelly_fraction(0.55, 1.0, 0.5) - 0.05) < 1e-6
