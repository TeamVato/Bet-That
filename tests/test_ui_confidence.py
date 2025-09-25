import numpy as np
import pandas as pd

from app.streamlit_app import compute_confidence


def test_confidence_clamped_for_na_inputs():
    df = pd.DataFrame(
        [
            {
                "is_stale": pd.NA,
                "sigma": None,
                "p_model_shrunk": pd.NA,
                "model_p": 0.55,
                "implied_prob": np.nan,
                "fair_prob": 0.52,
            },
            {
                "is_stale": 1,
                "sigma": "65",
                "p_model_shrunk": None,
                "model_p": pd.NA,
                "implied_prob": 0.48,
                "fair_prob": None,
            },
            {
                "is_stale": 0,
                "sigma": 40.0,
                "p_model_shrunk": 0.61,
                "model_p": 0.6,
                "implied_prob": 0.4,
                "fair_prob": 0.41,
            },
        ]
    )

    confidences = df.apply(compute_confidence, axis=1)

    assert confidences.notna().all()
    assert (confidences >= 0.0).all()
    assert (confidences <= 1.0).all()
