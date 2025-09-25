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
    assert len(edges) == 1
    overround = float(edges.iloc[0]["overround"])
    assert 1.0 <= overround <= 1.15
