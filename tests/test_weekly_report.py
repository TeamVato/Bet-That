import datetime as dt
import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

from jobs import report_weekly


def _init_weekly_db(path: Path) -> None:
    with sqlite3.connect(path) as con:
        con.execute(
            """
            CREATE TABLE edges (
                edge_id TEXT PRIMARY KEY,
                event_id TEXT,
                market TEXT,
                odds_side TEXT,
                line REAL,
                odds INTEGER,
                fair_prob REAL,
                implied_prob REAL,
                created_at TEXT,
                overround REAL,
                is_stale INTEGER,
                outcome REAL
            )
            """
        )
        con.execute(
            """
            CREATE TABLE closing_lines (
                closing_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT,
                market TEXT,
                side TEXT,
                line REAL,
                book TEXT,
                odds_american INTEGER,
                implied_prob REAL,
                fair_prob_close REAL,
                ts_close TEXT,
                is_primary INTEGER
            )
            """
        )
        con.execute(
            """
            CREATE TABLE clv_log (
                clv_id INTEGER PRIMARY KEY AUTOINCREMENT,
                edge_id TEXT,
                event_id TEXT,
                market TEXT,
                side TEXT,
                line REAL,
                beat_close INTEGER,
                created_at TEXT
            )
            """
        )

        edges_rows = [
            (
                "E1",
                "EVT1",
                "player_props",
                "over",
                285.5,
                -110,
                0.55,
                0.55,
                "2025-09-18T12:00:00Z",
                1.05,
                0,
                1.0,
            ),
            (
                "E2",
                "EVT1",
                "player_props",
                "under",
                285.5,
                -110,
                0.45,
                0.45,
                "2025-09-18T12:00:00Z",
                1.05,
                0,
                0.0,
            ),
        ]
        con.executemany(
            """
            INSERT INTO edges(edge_id, event_id, market, odds_side, line, odds, fair_prob, implied_prob,
                              created_at, overround, is_stale, outcome)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            edges_rows,
        )

        closing_rows = [
            (
                "EVT1",
                "player_props",
                "over",
                285.5,
                "dk",
                -120,
                0.55,
                0.55,
                "2025-09-19T12:05:00Z",
                1,
            ),
            (
                "EVT1",
                "player_props",
                "under",
                285.5,
                "dk",
                -110,
                0.5,
                0.5,
                "2025-09-19T12:05:00Z",
                1,
            ),
        ]
        con.executemany(
            """
            INSERT INTO closing_lines(event_id, market, side, line, book, odds_american,
                                      implied_prob, fair_prob_close, ts_close, is_primary)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            closing_rows,
        )

        clv_rows = [
            (
                "E1",
                "EVT1",
                "player_props",
                "over",
                285.5,
                1,
                "2025-09-19T13:00:00Z",
            ),
            (
                "E2",
                "EVT1",
                "player_props",
                "under",
                285.5,
                1,
                "2025-09-19T13:00:00Z",
            ),
        ]
        con.executemany(
            """
            INSERT INTO clv_log(edge_id, event_id, market, side, line, beat_close, created_at)
            VALUES(?,?,?,?,?,?,?)
            """,
            clv_rows,
        )


def test_weekly_report_outputs_and_flags(tmp_path, monkeypatch):
    db_path = tmp_path / "odds.db"
    _init_weekly_db(db_path)

    output_dir = tmp_path / "reports"
    alert_cache = tmp_path / "alerts.json"
    auto_flags = tmp_path / "flags.auto.yaml"
    manual_flags = tmp_path / "flags.manual.yaml"
    effective_flags = tmp_path / "flags.effective.yaml"

    with manual_flags.open("w", encoding="utf-8") as handle:
        yaml.safe_dump({"overrides": {}, "meta": {"managed_by": "manual", "updated_at": ""}}, handle)

    monkeypatch.setenv("SLACK_WEBHOOK_URL", "")

    as_of = dt.datetime(2025, 9, 21, tzinfo=dt.timezone.utc)

    summary = report_weekly.generate_report(
        db_path=db_path,
        config_path=Path("config/report_weekly.yml"),
        output_dir=output_dir,
        as_of=as_of,
        flags_auto_path=auto_flags,
        flags_manual_path=manual_flags,
        flags_effective_path=effective_flags,
        alert_state_path=alert_cache,
        now=as_of,
    )

    assert summary["overall"] == "OK"

    iso_year, iso_week, _ = as_of.isocalendar()
    week_dir = output_dir / f"{iso_year}-{iso_week:02d}"
    md_files = list(week_dir.glob("*.md"))
    status_file = week_dir / "status.json"
    assert md_files, "Markdown report not generated"
    assert status_file.exists()
    status = json.loads(status_file.read_text())
    assert status["overall"] == "OK"
    assert "clv_beat_close_rate" in status["metrics"]

    auto_payload = yaml.safe_load(auto_flags.read_text())
    effective_payload = yaml.safe_load(effective_flags.read_text())
    assert auto_payload["overrides"] == {}
    assert effective_payload["signals"]["publish_edges"] is True
    assert effective_payload["signals"]["show_confidence_badge"] is True


def test_weekly_report_p0_exits(monkeypatch, tmp_path):
    db_path = tmp_path / "odds.db"
    _init_weekly_db(db_path)

    def fake_metrics(*_args, **_kwargs):
        return {
            "clv_beat_close_rate": 0.4,
            "brier_over_baseline": 0.05,
            "close_match_coverage": 0.2,
            "overround_violation_rate": 0.5,
            "missing_side_rate": 0.5,
            "stale_flag_rate": 0.2,
        }

    monkeypatch.setenv("SLACK_WEBHOOK_URL", "")
    monkeypatch.setattr(report_weekly, "_compute_metrics", fake_metrics)
    monkeypatch.setattr(report_weekly, "_send_slack", lambda *args, **kwargs: None)

    auto_flags = tmp_path / "auto.yaml"
    manual_flags = tmp_path / "manual.yaml"
    effective_flags = tmp_path / "effective.yaml"
    alert_cache = tmp_path / "alerts.json"

    with manual_flags.open("w", encoding="utf-8") as handle:
        yaml.safe_dump({"overrides": {}, "meta": {"managed_by": "manual", "updated_at": ""}}, handle)

    # Expect SystemExit because severity escalates to P0
    args = [
        "report_weekly.py",
        "--db",
        str(db_path),
        "--output-dir",
        str(tmp_path / "reports"),
        "--flags-auto",
        str(auto_flags),
        "--flags-manual",
        str(manual_flags),
        "--flags-effective",
        str(effective_flags),
        "--alert-cache",
        str(alert_cache),
        "--as-of",
        "2025-09-21",
    ]
    monkeypatch.setattr(sys, "argv", args)
    with pytest.raises(SystemExit):
        report_weekly.main()
