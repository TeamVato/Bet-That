import pandas as pd

from engine.edge_engine import EdgeEngine, EdgeEngineConfig


def _props_row(event_id, player, market, line, over_odds, under_odds, book, pos, season, week, def_team, team):
    return {
        "event_id": event_id,
        "player": player,
        "market": market,
        "line": line,
        "over_odds": over_odds,
        "under_odds": under_odds,
        "book": book,
        "season": season,
        "week": week,
        "def_team": def_team,
        "team": team,
        "is_stale": 0,
        "pos": pos,
    }


def _projection_row(event_id, player, mu, sigma, season, week, def_team, team):
    return {
        "event_id": event_id,
        "player": player,
        "mu": mu,
        "sigma": sigma,
        "season": season,
        "week": week,
        "def_team": def_team,
        "team": team,
    }


def test_edge_engine_emits_multi_position_edges(tmp_path):
    config = EdgeEngineConfig(database_path=tmp_path / "edges.db", export_dir=tmp_path)
    engine = EdgeEngine(config)

    props_df = pd.DataFrame(
        [
            _props_row("2025-09-21-NE-BUF", "Quarterback Q", "player_pass_yds", 280.5, -110, -105, "dk", "QB", 2025, 1, "NE", "BUF"),
            _props_row("2025-09-21-SF-ATL", "Running Back R", "player_rush_yds", 72.5, -115, -105, "fd", "RB", 2025, 1, "ATL", "SF"),
            _props_row("2025-09-21-MIN-GB", "Wideout W", "player_rec_yds", 88.5, -120, 100, "dk", "WR", 2025, 1, "GB", "MIN"),
            _props_row("2025-09-21-DAL-SF", "Tight End T", "player_receptions", 5.5, 110, -130, "fd", "TE", 2025, 1, "SF", "DAL"),
        ]
    )

    projections_df = pd.DataFrame(
        [
            _projection_row("2025-09-21-NE-BUF", "Quarterback Q", 295.0, 40.0, 2025, 1, "NE", "BUF"),
            _projection_row("2025-09-21-SF-ATL", "Running Back R", 70.0, 25.0, 2025, 1, "ATL", "SF"),
            _projection_row("2025-09-21-MIN-GB", "Wideout W", 90.0, 30.0, 2025, 1, "GB", "MIN"),
            _projection_row("2025-09-21-DAL-SF", "Tight End T", 5.2, 1.8, 2025, 1, "SF", "DAL"),
        ]
    )

    edges_df = engine.compute_edges(props_df, projections_df)
    assert not edges_df.empty
    emitted_positions = set(edges_df["pos"].dropna())
    assert {"QB", "RB", "WR", "TE"}.issubset(emitted_positions)

    engine.export(edges_df)
    export_path = tmp_path / "edges_latest.csv"
    exported = pd.read_csv(export_path)
    export_positions = set(exported["pos"].dropna())
    assert {"RB", "WR", "TE"}.issubset(export_positions)
