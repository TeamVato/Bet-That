import pandas as pd

from jobs.import_odds_from_csv import dedupe_latest


def test_dedupe_latest_keeps_max_updated_at():
    df = pd.DataFrame(
        [
            {
                "event_id": "E1",
                "market": "Passing Yards",
                "book": "BookA",
                "side": "Over",
                "line": 250.5,
                "updated_at": "2024-09-01T00:00:00Z",
                "odds": -110,
            },
            {
                "event_id": "E1",
                "market": "Passing Yards",
                "book": "BookA",
                "side": "Over",
                "line": 250.5,
                "updated_at": "2024-09-01T00:05:00Z",
                "odds": -105,
            },
            {
                "event_id": "E1",
                "market": "Passing Yards",
                "book": "BookA",
                "side": "Under",
                "line": 250.5,
                "updated_at": "2024-09-01T00:10:00Z",
                "odds": -115,
            },
        ]
    )

    deduped = dedupe_latest(df, ["event_id", "market", "book", "side", "line"], sort_col="updated_at")

    assert len(deduped) == 2
    over_row = deduped[deduped["side"] == "Over"].iloc[0]
    assert over_row["odds"] == -105
    under_row = deduped[deduped["side"] == "Under"].iloc[0]
    assert under_row["odds"] == -115


def test_dedupe_latest_handles_missing_subset():
    df = pd.DataFrame([{ "event_id": "E2", "updated_at": "2024-09-01T00:00:00Z" }])
    result = dedupe_latest(df, [], sort_col="updated_at")
    assert result.equals(df)
