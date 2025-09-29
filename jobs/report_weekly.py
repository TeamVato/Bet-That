"""Generate weekly CLV/calibration report, alerts, and gating flags."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd
import requests
import yaml

from config.flags import load_flags

CONFIG_DEFAULT = Path("config/report_weekly.yml")
FLAGS_AUTO_DEFAULT = Path("config/signal_flags.auto.yaml")
FLAGS_MANUAL_DEFAULT = Path("config/signal_flags.manual.yaml")
FLAGS_EFFECTIVE_DEFAULT = Path("config/signal_flags.effective.yaml")
ALERT_STATE_DEFAULT = Path("reports/weekly/.alert_state.json")
OUTPUT_DIR_DEFAULT = Path("reports/weekly")
DB_DEFAULT = Path("storage/odds.db")

SEVERITY_ORDER = {"OK": 0, "P1": 1, "P0": 2}


def _load_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _window_filter(df: pd.DataFrame, column: str, window_start: dt.datetime) -> pd.DataFrame:
    if column not in df.columns:
        return df
    series = pd.to_datetime(df[column], errors="coerce", utc=True)
    mask = series >= window_start
    return df.loc[mask].copy()


def _compute_brier(edges: pd.DataFrame) -> Tuple[float, float]:
    if edges.empty or "outcome" not in edges:
        return np.nan, np.nan
    outcomes = pd.to_numeric(edges["outcome"], errors="coerce")
    probs = pd.to_numeric(edges.get("entry_prob_fair"), errors="coerce")
    mask = (~outcomes.isna()) & (~probs.isna())
    if not mask.any():
        return np.nan, np.nan
    outcomes = outcomes[mask].clip(0.0, 1.0)
    probs = probs[mask].clip(0.0, 1.0)
    brier = np.mean((probs - outcomes) ** 2)
    baseline_prob = outcomes.mean()
    baseline_brier = np.mean((baseline_prob - outcomes) ** 2)
    return brier, baseline_brier


def _missing_side_rate(edges: pd.DataFrame) -> float:
    if edges.empty:
        return np.nan
    grouping = edges.groupby(["event_id", "market", "line_entry"], dropna=False)
    counts = grouping["side"].nunique()
    if counts.empty:
        return np.nan
    return float((counts < 2).sum() / len(counts))


def _overround_violation_rate(edges: pd.DataFrame) -> float:
    if "overround" not in edges or edges.empty:
        return np.nan
    vals = pd.to_numeric(edges["overround"], errors="coerce")
    vals = vals.dropna()
    if vals.empty:
        return np.nan
    violations = (vals < 1.0) | (vals > 1.15)
    return float(violations.mean())


def _stale_rate(edges: pd.DataFrame) -> float:
    if "is_stale" not in edges or edges.empty:
        return np.nan
    vals = pd.to_numeric(edges["is_stale"], errors="coerce").fillna(0)
    if vals.empty:
        return np.nan
    return float(vals.mean())


def _compute_metrics(con: sqlite3.Connection, window_start: dt.datetime) -> Dict[str, float]:
    edges = _load_edges(con)
    closings = _load_closing(con)
    clv = _load_clv(con)

    edges = _prepare_edges(edges)
    closings = _prepare_closings(closings)
    clv = _prepare_clv(clv)

    edges_recent = _window_filter(edges, "created_at", window_start)
    closings_recent = _window_filter(closings, "ts_close", window_start)
    clv_recent = _window_filter(clv, "created_at", window_start)

    metrics: Dict[str, float] = {}

    if not clv_recent.empty:
        beat = pd.to_numeric(clv_recent["beat_close"], errors="coerce")
        beat = beat.dropna()
        metrics["clv_beat_close_rate"] = float(beat.mean()) if not beat.empty else np.nan
        edges_count = len(edges_recent) if not edges_recent.empty else len(edges)
        edges_count = edges_count or 0
        matched = clv_recent["edge_id"].nunique()
        metrics["close_match_coverage"] = float(matched / edges_count) if edges_count else np.nan
    else:
        metrics["clv_beat_close_rate"] = np.nan
        metrics["close_match_coverage"] = np.nan

    brier, baseline = _compute_brier(edges_recent)
    if np.isnan(brier) or np.isnan(baseline):
        metrics["brier_over_baseline"] = np.nan
    else:
        metrics["brier_over_baseline"] = float(brier - baseline)

    metrics["overround_violation_rate"] = _overround_violation_rate(edges_recent)
    metrics["missing_side_rate"] = _missing_side_rate(edges_recent)
    metrics["stale_flag_rate"] = _stale_rate(edges_recent)

    return metrics


def _load_edges(con: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM edges", con)


def _load_closing(con: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM closing_lines", con)


def _load_clv(con: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM clv_log", con)


def _prepare_edges(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    working = df.copy()
    working["side"] = working.get("odds_side", "").astype(str).str.lower()
    working["line_entry"] = pd.to_numeric(working.get("line"), errors="coerce")
    working["entry_prob_fair"] = pd.to_numeric(working.get("fair_prob"), errors="coerce")
    fallback = pd.to_numeric(working.get("implied_prob"), errors="coerce")
    working["entry_prob_fair"] = working["entry_prob_fair"].fillna(fallback)
    working["overround"] = pd.to_numeric(working.get("overround"), errors="coerce")
    working["is_stale"] = pd.to_numeric(working.get("is_stale"), errors="coerce")
    working["created_at"] = pd.to_datetime(working.get("created_at"), errors="coerce", utc=True)
    return working


def _prepare_closings(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    working = df.copy()
    working["side"] = working.get("side", "").astype(str).str.lower()
    working["line_close"] = pd.to_numeric(working.get("line"), errors="coerce")
    working["close_prob_fair"] = pd.to_numeric(working.get("fair_prob_close"), errors="coerce")
    fallback = pd.to_numeric(working.get("implied_prob"), errors="coerce")
    working["close_prob_fair"] = working["close_prob_fair"].fillna(fallback)
    working["ts_close"] = pd.to_datetime(working.get("ts_close"), errors="coerce", utc=True)
    return working


def _prepare_clv(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    working = df.copy()
    working["created_at"] = pd.to_datetime(working.get("created_at"), errors="coerce", utc=True)
    return working


def _severity_clv(metric: float, thresholds: Dict[str, float]) -> str:
    if np.isnan(metric):
        return "P1"
    if metric >= thresholds.get("ok", 1.0):
        return "OK"
    if metric >= thresholds.get("warn", thresholds.get("ok", 0)):
        return "P1"
    return "P0"


def _severity_brier(metric: float, thresholds: Dict[str, float]) -> str:
    if np.isnan(metric):
        return "P1"
    warn = thresholds.get("warn")
    fail = thresholds.get("fail")
    if warn is not None and metric <= warn:
        return "OK"
    if fail is not None and metric <= fail:
        return "P1"
    return "P0"


def _severity_min(metric: float, minimum: float) -> str:
    if np.isnan(metric):
        return "P1"
    return "OK" if metric >= minimum else "P0"


def _severity_max(metric: float, warn: float) -> str:
    if np.isnan(metric):
        return "P1"
    return "OK" if metric <= warn else "P1"


def _classify(metrics: Dict[str, float], cfg: Dict[str, Any]) -> Dict[str, str]:
    thresholds = cfg.get("thresholds", {})
    sevs: Dict[str, str] = {}
    sevs["clv_beat_close_rate"] = _severity_clv(
        metrics.get("clv_beat_close_rate", np.nan), thresholds.get("clv_beat_close", {})
    )
    sevs["brier_over_baseline"] = _severity_brier(
        metrics.get("brier_over_baseline", np.nan), thresholds.get("brier_over_baseline", {})
    )
    sevs["close_match_coverage"] = _severity_min(
        metrics.get("close_match_coverage", np.nan), thresholds.get("close_match_coverage_min", 0.0)
    )
    sevs["overround_violation_rate"] = _severity_max(
        metrics.get("overround_violation_rate", np.nan),
        thresholds.get("overround_violation_rate_warn", 1.0),
    )
    sevs["missing_side_rate"] = _severity_max(
        metrics.get("missing_side_rate", np.nan), thresholds.get("missing_side_rate_warn", 1.0)
    )
    sevs["stale_flag_rate"] = _severity_max(
        metrics.get("stale_flag_rate", np.nan), thresholds.get("stale_flag_rate_warn", 1.0)
    )
    return sevs


def _overall(severities: Dict[str, str]) -> str:
    highest = "OK"
    for sev in severities.values():
        if SEVERITY_ORDER.get(sev, 0) > SEVERITY_ORDER[highest]:
            highest = sev
    return highest


def _format_markdown(as_of: dt.date, metrics: Dict[str, float], severities: Dict[str, str]) -> str:
    lines = [
        f"# Weekly CLV & Calibration Report — {as_of.isoformat()}",
        "",
        "| Metric | Value | Severity |",
        "| --- | --- | --- |",
    ]
    for key, value in metrics.items():
        severity = severities.get(key, "OK")
        display_val = "n/a" if np.isnan(value) else f"{value:.4f}"
        lines.append(f"| {key} | {display_val} | {severity} |")
    return "\n".join(lines) + "\n"


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _write_text(path: Path, content: str) -> None:
    _ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(content)


def _coerce_yaml_value(value: Any) -> Any:
    if isinstance(value, float) and np.isnan(value):
        return None
    return value


def _write_auto_flags(path: Path, overrides: Dict[str, bool], now: dt.datetime) -> None:
    payload = {
        "overrides": overrides,
        "meta": {
            "managed_by": "auto",
            "updated_at": now.isoformat(),
        },
    }
    _ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=True)


def _send_slack(alert_url: str, message: str) -> None:
    try:
        response = requests.post(alert_url, json={"text": message}, timeout=5)
        response.raise_for_status()
    except Exception as exc:
        print(f"Slack alert failed: {exc}")


def _should_send_alert(state_path: Path, message: str, now: dt.datetime) -> bool:
    if not state_path.exists():
        return True
    try:
        with state_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        last_msg = data.get("message")
        last_ts = data.get("timestamp")
        if last_msg != message:
            return True
        if last_ts:
            last_time = dt.datetime.fromisoformat(last_ts)
            if now - last_time <= dt.timedelta(minutes=30):
                return False
    except Exception:
        return True
    return True


def _update_alert_state(state_path: Path, message: str, now: dt.datetime) -> None:
    payload = {"message": message, "timestamp": now.isoformat()}
    _ensure_parent(state_path)
    with state_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def generate_report(
    *,
    db_path: Path,
    config_path: Path = CONFIG_DEFAULT,
    output_dir: Path = OUTPUT_DIR_DEFAULT,
    as_of: dt.datetime | None = None,
    flags_auto_path: Path = FLAGS_AUTO_DEFAULT,
    flags_manual_path: Path = FLAGS_MANUAL_DEFAULT,
    flags_effective_path: Path = FLAGS_EFFECTIVE_DEFAULT,
    alert_state_path: Path = ALERT_STATE_DEFAULT,
    now: dt.datetime | None = None,
) -> Dict[str, Any]:
    config = _load_config(config_path)
    as_of_dt = as_of or dt.datetime.now(dt.timezone.utc)
    if isinstance(as_of_dt, dt.date) and not isinstance(as_of_dt, dt.datetime):
        as_of_dt = dt.datetime.combine(as_of_dt, dt.time(0, 0), tzinfo=dt.timezone.utc)
    now_dt = now or dt.datetime.now(dt.timezone.utc)

    rolling_weeks = config.get("rolling_weeks", 4)
    window_start = as_of_dt - dt.timedelta(weeks=rolling_weeks)

    with sqlite3.connect(db_path) as con:
        con.execute("PRAGMA journal_mode=WAL;")
        metrics = _compute_metrics(con, window_start)

    severities = _classify(metrics, config)
    overall = _overall(severities)

    iso_year, iso_week, _ = as_of_dt.isocalendar()
    week_dir = output_dir / f"{iso_year}-{iso_week:02d}"
    markdown_path = week_dir / f"CLV_Calibration_Report_{as_of_dt.date().isoformat()}.md"
    status_path = week_dir / "status.json"

    markdown = _format_markdown(as_of_dt.date(), metrics, severities)
    status_payload = {
        "generated_at": now_dt.isoformat(),
        "as_of": as_of_dt.isoformat(),
        "metrics": {k: _coerce_yaml_value(v) for k, v in metrics.items()},
        "severities": severities,
        "overall": overall,
    }
    _write_text(markdown_path, markdown)
    _write_json(status_path, status_payload)

    routing = config.get("routing", {})
    slack_env = routing.get("slack_webhook_env")
    webhook = os.getenv(slack_env, "") if slack_env else ""
    if webhook:
        message = f"[{overall}] Weekly CLV summary — beat_close={metrics.get('clv_beat_close_rate'):.3f if not np.isnan(metrics.get('clv_beat_close_rate', np.nan)) else 'n/a'} | coverage={metrics.get('close_match_coverage'):.3f if not np.isnan(metrics.get('close_match_coverage', np.nan)) else 'n/a'}"
        if _should_send_alert(alert_state_path, message, now_dt):
            _send_slack(webhook, message)
            _update_alert_state(alert_state_path, message, now_dt)

    overrides: Dict[str, bool] = {}
    if overall == "P0" and config.get("gating", {}).get("auto_disable_signals", True):
        overrides = {"publish_edges": False, "show_confidence_badge": False}
    _write_auto_flags(flags_auto_path, overrides, now_dt)

    load_flags(
        now=now_dt,
        auto_path=flags_auto_path,
        manual_path=flags_manual_path,
        effective_path=flags_effective_path,
    )

    summary = {
        "metrics": metrics,
        "severities": severities,
        "overall": overall,
        "markdown_path": markdown_path,
        "status_path": status_path,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate weekly CLV/calibration report")
    parser.add_argument("--db", type=Path, default=DB_DEFAULT)
    parser.add_argument("--config", type=Path, default=CONFIG_DEFAULT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR_DEFAULT)
    parser.add_argument("--as-of", type=str, default=None, help="ISO date for report (YYYY-MM-DD)")
    parser.add_argument("--flags-auto", type=Path, default=FLAGS_AUTO_DEFAULT)
    parser.add_argument("--flags-manual", type=Path, default=FLAGS_MANUAL_DEFAULT)
    parser.add_argument("--flags-effective", type=Path, default=FLAGS_EFFECTIVE_DEFAULT)
    parser.add_argument("--alert-cache", type=Path, default=ALERT_STATE_DEFAULT)
    args = parser.parse_args()

    as_of_dt = None
    if args.as_of:
        as_of_dt = dt.datetime.fromisoformat(args.as_of).replace(tzinfo=dt.timezone.utc)

    summary = generate_report(
        db_path=args.db,
        config_path=args.config,
        output_dir=args.output_dir,
        as_of=as_of_dt,
        flags_auto_path=args.flags_auto,
        flags_manual_path=args.flags_manual,
        flags_effective_path=args.flags_effective,
        alert_state_path=args.alert_cache,
    )

    config = _load_config(args.config)
    if summary["overall"] == "P0" and config.get("gating", {}).get("fail_ci_on_p0", True):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
