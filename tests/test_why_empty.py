import pandas as pd

from app.why_empty import Filters, format_hints, stepwise_drop


def _edges_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "season": [2023, 2023, 2024, 2024, 2025],
            "pos": ["QB", "RB", "WR", "TE", "RB"],
            "book": ["draftkings", "fanduel", "caesars", "draftkings", "fanduel"],
            "odds": [-120, -110, 140, 115, -105],
            "ev_per_dollar": [0.03, 0.02, 0.08, 0.01, 0.05],
            "stale": [0, 1, 0, 0, 1],
            "best_priced": [0, 0, 1, 0, 0],
            "opponent_def_code": [None, "DAL", "PHI", "SF", "KC"],
            "def_tier": [None, "neutral", "stingy", "neutral", "generous"],
        }
    )


def test_stepwise_drop_filters_ordered_counts():
    edges = _edges_df()
    filters = Filters(
        seasons=[2023],
        odds_min=-250,
        odds_max=125,
        ev_min=0.02,
        hide_stale=True,
        best_priced_only=True,
    )
    report = stepwise_drop(edges, filters)
    labels = [item[0] for item in report]
    assert "Season filter" in labels
    assert any(label.startswith("Hide stale") for label in labels)
    assert any(label.startswith("Best-priced only") for label in labels)

    hints = format_hints(report)
    assert hints
    assert any("Fix:" in hint for hint in hints)


def test_position_and_book_context_reporting():
    edges = _edges_df()
    filters_pos = Filters(
        seasons=[2024, 2025],
        odds_min=-250,
        odds_max=250,
        ev_min=-1.0,
        hide_stale=False,
        best_priced_only=False,
        pos="QB",
    )
    report_pos = stepwise_drop(edges, filters_pos)
    assert any("Position filter (QB)" in item[0] for item in report_pos)

    filters_book = Filters(
        seasons=[2024, 2025],
        odds_min=-250,
        odds_max=250,
        ev_min=-1.0,
        hide_stale=False,
        best_priced_only=False,
        book="fanduel",
    )
    report_book = stepwise_drop(edges, filters_book)
    assert any("Sportsbook filter (fanduel)" in item[0] for item in report_book)
