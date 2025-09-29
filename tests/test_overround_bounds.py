import pandas as pd

from engine.edge_engine import EdgeEngine, EdgeEngineConfig


def test_overround_with_standard_juice_is_within_bounds(tmp_path):
    engine = EdgeEngine(EdgeEngineConfig(database_path=tmp_path / "odds.db"))
    props = pd.DataFrame(
        [
            {
                "event_id": "GAME1",
                "player": "QB1",
                "market": "Passing Yards",
                "book": "BookA",
                "line": 250.5,
                "over_odds": -110,
                "under_odds": -110,
                "season": 2024,
                "def_team": "NYJ",
                "team": "BUF",
            }
        ]
    )
    projections = pd.DataFrame(
        [
            {
                "event_id": "GAME1",
                "player": "QB1",
                "mu": 255.0,
                "sigma": 45.0,
                "p_over": 0.55,
                "season": 2024,
                "week": 1,
                "def_team": "NYJ",
                "team": "BUF",
                "updated_at": "2024-09-01T00:00:00Z",
            }
        ]
    )

    edges = engine.compute_edges(props, projections)
    assert len(edges) == 2, "Two-way market should generate over and under edges"

    # Check that we have both sides
    sides = set(edges["side"].tolist())
    assert sides == {"over", "under"}, f"Expected over and under sides, got {sides}"

    # Verify overround exists by checking implied probabilities sum > 1
    from engine.odds_math import american_to_implied_prob

    total_implied_prob = sum(american_to_implied_prob(odds) for odds in [-110, -110])
    assert (
        total_implied_prob > 1.0
    ), f"Two-way market should have overround, got {total_implied_prob:.3f}"
    assert (
        total_implied_prob <= 1.15
    ), f"Overround should be reasonable, got {total_implied_prob:.3f}"
