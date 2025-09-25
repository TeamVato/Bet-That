import pandas as pd

from jobs.compute_edges import apply_defense_defaults


def test_apply_defense_defaults_sets_neutral_when_missing():
    edges = pd.DataFrame(
        {
            "player": ["QB"],
            "def_tier": [pd.NA],
            "def_score": [pd.NA],
            "opponent_def_code": [pd.NA],
        }
    )

    enriched = apply_defense_defaults(edges)

    assert len(enriched) == 1
    assert enriched.loc[0, "def_tier"] == "neutral"
    assert enriched.loc[0, "def_score"] == 0.0


def test_apply_defense_defaults_adds_columns_when_absent():
    edges = pd.DataFrame({"player": ["QB"], "model_p": [0.55]})

    enriched = apply_defense_defaults(edges)

    assert "def_tier" in enriched.columns
    assert "def_score" in enriched.columns
    assert enriched.loc[0, "def_tier"] == "neutral"
    assert enriched.loc[0, "def_score"] == 0.0
