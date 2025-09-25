from pathlib import Path

import pandas as pd

from engine.edge_engine import EdgeEngine, EdgeEngineConfig


def _make_engine(tmp_path) -> EdgeEngine:
    cfg = EdgeEngineConfig(database_path=tmp_path / "odds.db")
    return EdgeEngine(cfg)


def test_compute_edges_skips_incomplete_two_way_markets(tmp_path):
    engine = _make_engine(tmp_path)
    props = pd.DataFrame(
        [
            {
                "event_id": "E1",
                "book": "BookA",
                "player": "Player",
                "market": "Passing Yards",
                "line": 250.5,
                "over_odds": -110,
                "under_odds": None,
                "season": 2023,
                "def_team": "NYJ",
                "team": "BUF",
            }
        ]
    )
    projections = pd.DataFrame(
        [
            {
                "event_id": "E1",
                "player": "Player",
                "mu": 255.0,
                "sigma": 50.0,
                "p_over": 0.52,
                "season": 2023,
                "week": 1,
                "def_team": "NYJ",
                "team": "BUF",
                "updated_at": "2025-09-24T00:00:00Z",
            }
        ]
    )
    edges = engine.compute_edges(props, projections)
    assert edges.empty


def test_compute_edges_emits_complete_market(tmp_path):
    engine = _make_engine(tmp_path)
    props = pd.DataFrame(
        [
            {
                "event_id": "E2",
                "book": "BookA",
                "player": "Player",
                "market": "Passing Yards",
                "line": 250.5,
                "over_odds": -110,
                "under_odds": -105,
                "season": 2023,
                "def_team": "NYJ",
                "team": "BUF",
            }
        ]
    )
    projections = pd.DataFrame(
        [
            {
                "event_id": "E2",
                "player": "Player",
                "mu": 255.0,
                "sigma": 50.0,
                "p_over": 0.52,
                "season": 2023,
                "week": 1,
                "def_team": "NYJ",
                "team": "BUF",
                "updated_at": "2025-09-24T00:00:00Z",
            }
        ]
    )
    edges = engine.compute_edges(props, projections)
    assert len(edges) == 1
    row = edges.iloc[0]
    assert row["player"] == "Player"
    assert row["team"] == "BUF"
