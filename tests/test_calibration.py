import pandas as pd

from engine.calibration import brier_score, bucket_calibration


def test_bucket_calibration_shapes():
    df = pd.DataFrame({"p": [0.1, 0.2, 0.8, 0.9], "y": [0, 0, 1, 1]})
    out = bucket_calibration(df, "p", "y", n=2)
    assert {"p_mean", "y_rate", "n"} <= set(out.columns)


def test_brier():
    assert round(brier_score([0, 1], [0, 1]), 6) == 0.0
