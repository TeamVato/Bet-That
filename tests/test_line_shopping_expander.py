import pandas as pd

from app.streamlit_app import build_line_shopping_table


def test_line_shopping_table_includes_all_books_and_best_flags():
    odds_raw = pd.DataFrame(
        [
            {
                "event_id": "E1",
                "player": "Player",
                "market": "Passing Yards",
                "line": 250.5,
                "book": "BookA",
                "side": "Over",
                "odds": -110,
                "implied_prob": 0.524,
                "fair_prob": 0.51,
                "updated_at": "2025-09-24T00:00:00Z",
            },
            {
                "event_id": "E1",
                "player": "Player",
                "market": "Passing Yards",
                "line": 250.5,
                "book": "BookB",
                "side": "Over",
                "odds": -105,
                "implied_prob": 0.512,
                "fair_prob": 0.50,
                "updated_at": "2025-09-24T00:05:00Z",
            },
            {
                "event_id": "E1",
                "player": "Player",
                "market": "Passing Yards",
                "line": 250.5,
                "book": "BookA",
                "side": "Under",
                "odds": -110,
                "implied_prob": 0.524,
                "fair_prob": 0.51,
                "updated_at": "2025-09-24T00:00:00Z",
            },
            {
                "event_id": "E1",
                "player": "Player",
                "market": "Passing Yards",
                "line": 250.5,
                "book": "BookC",
                "side": "Under",
                "odds": -102,
                "implied_prob": 0.503,
                "fair_prob": 0.49,
                "updated_at": "2025-09-24T00:02:00Z",
            },
        ]
    )
    row = pd.Series(
        {"event_id": "E1", "player": "Player", "market": "Passing Yards", "line": 250.5}
    )
    view, consensus = build_line_shopping_table(odds_raw, row)

    assert len(view) == 4
    assert set(view["book"]) == {"BookA", "BookB", "BookC"}
    over_rows = view[view["side"] == "Over"]
    assert over_rows.loc[over_rows["book"] == "BookB", "best_flag"].iloc[0] == "⭐"
    under_rows = view[view["side"] == "Under"]
    assert under_rows.loc[under_rows["book"] == "BookC", "best_flag"].iloc[0] == "⭐"

    assert "Over" in consensus and "Under" in consensus
    assert abs(consensus["Over"] - 0.505) < 1e-6
    assert abs(consensus["Under"] - 0.5) < 1e-6
