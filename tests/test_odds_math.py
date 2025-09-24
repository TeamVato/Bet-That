import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import math

import pytest

from engine import odds_math


def test_american_to_decimal_positive():
    assert math.isclose(odds_math.american_to_decimal(150), 2.5)


def test_american_to_decimal_negative():
    assert math.isclose(odds_math.american_to_decimal(-120), 1 + 100 / 120)


def test_american_to_prob():
    prob = odds_math.american_to_prob(-110)
    assert math.isclose(prob, 1 / 1.9090909, rel_tol=1e-6)


def test_no_vig_two_way():
    probs = odds_math.no_vig_two_way(-110, -110, labels=("over", "under"))
    assert math.isclose(probs["over"], 0.5)
    assert math.isclose(probs["under"], 0.5)


def test_ev_and_kelly():
    p_true = 0.55
    odds = -110
    ev = odds_math.ev_per_dollar(p_true, odds)
    assert ev > 0
    kelly = odds_math.kelly_fraction(p_true, odds)
    assert 0 < kelly < 1
