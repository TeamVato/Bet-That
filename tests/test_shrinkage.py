import pandas as pd

from engine.shrinkage import shrink_to_market


def test_shrink_bounds():
    p_model = pd.Series([0.7, 0.3])
    p_cons = pd.Series([0.5, 0.5])
    out = shrink_to_market(p_model, p_cons, weight=0.5)
    assert list(out.round(3)) == [0.6, 0.4]

