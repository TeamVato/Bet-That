import math
import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from jobs.build_defense_ratings import _compute_qb_pass_adjusted_scores
from jobs.compute_edges import ensure_defense_ratings_latest_view
from models.qb_projection import ProjectionConfig, QBProjectionModel


def test_ensure_defense_ratings_latest_view(tmp_path):
    db_path = tmp_path / "ratings.db"
    with sqlite3.connect(db_path) as con:
        con.execute(
            """
            CREATE TABLE defense_ratings (
                defteam TEXT,
                season INT,
                week INT,
                pos TEXT,
                score REAL,
                tier TEXT,
                PRIMARY KEY(defteam, season, week, pos)
            )
            """
        )
        rows = [
            ("BUF", 2024, 1, "QB_PASS", 0.10, "neutral"),
            ("BUF", 2024, 2, "QB_PASS", 0.15, "generous"),
            ("BUF", 2024, 1, "RB_RUSH", -0.05, "stingy"),
            ("NYJ", 2024, 3, "QB_PASS", -0.20, "stingy"),
            ("NYJ", 2024, 4, "QB_PASS", -0.25, "stingy"),
        ]
        con.executemany(
            "INSERT OR REPLACE INTO defense_ratings VALUES (?, ?, ?, ?, ?, ?)",
            rows,
        )
    ensure_defense_ratings_latest_view(db_path)
    with sqlite3.connect(db_path) as con:
        fetched = con.execute(
            "SELECT defteam, season, pos, week, tier FROM defense_ratings_latest ORDER BY defteam, pos"
        ).fetchall()
    assert fetched == [
        ("BUF", 2024, "QB_PASS", 2, "generous"),
        ("BUF", 2024, "RB_RUSH", 1, "stingy"),
        ("NYJ", 2024, "QB_PASS", 4, "stingy"),
    ]


def test_qb_pass_adjusted_scores_smoothed_output():
    pbp = pd.DataFrame(
        [
            {
                "is_pass": 1,
                "defteam": "NYJ",
                "posteam": "BUF",
                "season": 2024,
                "week": 1,
                "epa": -0.3,
                "successful": 0,
            },
            {
                "is_pass": 1,
                "defteam": "NYJ",
                "posteam": "BUF",
                "season": 2024,
                "week": 1,
                "epa": -0.2,
                "successful": 1,
            },
            {
                "is_pass": 1,
                "defteam": "NYJ",
                "posteam": "KC",
                "season": 2024,
                "week": 2,
                "epa": -0.15,
                "successful": 1,
            },
            {
                "is_pass": 1,
                "defteam": "NYJ",
                "posteam": "KC",
                "season": 2024,
                "week": 3,
                "epa": -0.1,
                "successful": 1,
            },
            {
                "is_pass": 1,
                "defteam": "BUF",
                "posteam": "KC",
                "season": 2024,
                "week": 1,
                "epa": 0.25,
                "successful": 1,
            },
            {
                "is_pass": 1,
                "defteam": "BUF",
                "posteam": "KC",
                "season": 2024,
                "week": 2,
                "epa": 0.30,
                "successful": 1,
            },
            {
                "is_pass": 1,
                "defteam": "BUF",
                "posteam": "NYJ",
                "season": 2024,
                "week": 3,
                "epa": 0.35,
                "successful": 1,
            },
            {
                "is_pass": 1,
                "defteam": "BUF",
                "posteam": "NYJ",
                "season": 2024,
                "week": 4,
                "epa": 0.40,
                "successful": 1,
            },
        ]
    )
    adjusted = _compute_qb_pass_adjusted_scores(pbp)
    assert not adjusted.empty
    assert set(["score_adj", "tier_adj"]).issubset(adjusted.columns)
    assert {"NYJ", "BUF"}.issubset(set(adjusted["defteam"]))
    assert adjusted["score_adj"].notna().any()


def test_projection_fallback_uses_internal_metrics(monkeypatch):
    game_logs = pd.DataFrame(
        [
            {
                "player_name": "A",
                "season": 2024,
                "week": 1,
                "passing_yards": 210,
                "opponent_team": "NYJ",
            },
            {
                "player_name": "B",
                "season": 2024,
                "week": 2,
                "passing_yards": 205,
                "opponent_team": "NYJ",
            },
            {
                "player_name": "C",
                "season": 2024,
                "week": 1,
                "passing_yards": 320,
                "opponent_team": "NE",
            },
            {
                "player_name": "D",
                "season": 2024,
                "week": 2,
                "passing_yards": 330,
                "opponent_team": "NE",
            },
        ]
    )
    schedule_lookup = {"EVT1": {"season": 2024, "week": 3}}
    model = QBProjectionModel(
        game_logs=game_logs,
        schedule_lookup=schedule_lookup,
        config=ProjectionConfig(),
    )

    monkeypatch.setattr("models.qb_projection.apply_qb_defense_adjustment", lambda **_: None)

    mu = 250.0
    adjusted = model._apply_defense_adjustment(mu, "NYJ", 2024, 3)
    league_avg = model.defense_metrics["__league_avg__"]
    defense_avg = model.defense_metrics["NYJ"]
    expected = mu * (1 + 0.35 * ((league_avg - defense_avg) / league_avg))
    assert math.isclose(adjusted, expected, rel_tol=1e-6)
