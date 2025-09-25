import pandas as pd


def apply_best_priced_filter(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.sort_values("ev_per_dollar", ascending=False)
        .drop_duplicates(["event_id", "player", "market"])
        .reset_index(drop=True)
    )


def test_best_priced_filter_keeps_highest_ev_per_market():
    data = pd.DataFrame(
        [
            {"event_id": "E1", "player": "Player", "market": "Passing Yards", "book": "BookA", "ev_per_dollar": 0.05},
            {"event_id": "E1", "player": "Player", "market": "Passing Yards", "book": "BookB", "ev_per_dollar": 0.12},
            {"event_id": "E2", "player": "Player", "market": "Touchdowns", "book": "BookC", "ev_per_dollar": -0.01},
            {"event_id": "E2", "player": "Player", "market": "Touchdowns", "book": "BookD", "ev_per_dollar": 0.02},
        ]
    )
    filtered = apply_best_priced_filter(data)
    assert len(filtered) == 2
    e1_row = filtered.loc[filtered["event_id"] == "E1"].iloc[0]
    assert e1_row["book"] == "BookB"
    e2_row = filtered.loc[filtered["event_id"] == "E2"].iloc[0]
    assert e2_row["book"] == "BookD"


def test_best_priced_filter_handles_negative_and_positive_edges():
    data = pd.DataFrame(
        [
            {"event_id": "E3", "player": "Q", "market": "Completions", "book": "BookA", "ev_per_dollar": -0.02},
            {"event_id": "E3", "player": "Q", "market": "Completions", "book": "BookB", "ev_per_dollar": -0.10},
            {"event_id": "E4", "player": "Q", "market": "Attempts", "book": "BookC", "ev_per_dollar": 0.08},
            {"event_id": "E4", "player": "Q", "market": "Attempts", "book": "BookD", "ev_per_dollar": 0.07},
        ]
    )
    filtered = apply_best_priced_filter(data)
    assert len(filtered) == 2
    e3_row = filtered.loc[filtered["event_id"] == "E3"].iloc[0]
    assert e3_row["book"] == "BookA"
    e4_row = filtered.loc[filtered["event_id"] == "E4"].iloc[0]
    assert e4_row["book"] == "BookC"
