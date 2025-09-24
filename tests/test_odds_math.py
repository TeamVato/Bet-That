import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from engine.odds_math import (
    american_to_decimal,
    american_to_implied_prob,
    devig_proportional_from_decimal,
)


def approx(a, b, tol=1e-4):
    return abs(a - b) <= tol


def test_american_to_implied():
    assert approx(american_to_implied_prob(-110), 0.5238095238)
    assert approx(american_to_implied_prob(+120), 0.4545454545)


def test_american_to_decimal():
    assert approx(american_to_decimal(-110), 1 + 100 / 110)
    assert approx(american_to_decimal(+120), 1 + 120 / 100)


def test_devig_proportional_symmetry():
    (pairs, overround) = devig_proportional_from_decimal([1.90909, 1.90909])
    p1, d1 = pairs[0]
    p2, d2 = pairs[1]
    assert 1.04 < overround < 1.06
    assert approx(p1, 0.5) and approx(p2, 0.5)
    assert approx(d1, 2.0) and approx(d2, 2.0)
