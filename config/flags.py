"""Helpers for loading and merging signal flags with TTL support."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml

CONFIG_DIR = Path(__file__).resolve().parent
AUTO_PATH = CONFIG_DIR / "signal_flags.auto.yaml"
MANUAL_PATH = CONFIG_DIR / "signal_flags.manual.yaml"
EFFECTIVE_PATH = CONFIG_DIR / "signal_flags.effective.yaml"

DEFAULT_FLAGS: Dict[str, bool] = {
    "publish_edges": True,
    "show_top_plays": True,
    "show_confidence_badge": True,
}


def _ensure_file(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    default_payload = {"overrides": {}, "meta": {"managed_by": path.stem, "updated_at": ""}}
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(default_payload, handle, sort_keys=True)


def _parse_iso8601(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        cleaned = value.strip()
        if cleaned.endswith("Z"):
            cleaned = cleaned[:-1] + "+00:00"
        return datetime.fromisoformat(cleaned)
    except Exception:
        return None


def _coerce_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "on"}:
            return True
        if lowered in {"false", "0", "no", "off"}:
            return False
    return None


def _compute_expiry(
    raw: Any, meta: Dict[str, Any], now: datetime
) -> Tuple[bool | None, datetime | None]:
    expires_at: datetime | None = None
    ttl_minutes = None
    updated_at = meta.get("updated_at")
    value: Any = raw

    if isinstance(raw, dict):
        value = raw.get("value")
        expires_at = _parse_iso8601(raw.get("expires_at"))
        updated_at = raw.get("updated_at", updated_at)
        ttl_minutes = raw.get("ttl_minutes")
    if expires_at is None:
        if ttl_minutes is None:
            ttl_minutes = meta.get("ttl_minutes")
        if ttl_minutes and updated_at:
            base = _parse_iso8601(updated_at)
            if base:
                try:
                    expires_at = base + timedelta(minutes=int(ttl_minutes))
                except Exception:
                    expires_at = None
    value_bool = _coerce_bool(value)
    return value_bool, expires_at


def _prune_overrides(data: Dict[str, Any], now: datetime) -> Dict[str, bool]:
    overrides: Dict[str, bool] = {}
    raw_overrides = data.get("overrides") or {}
    meta = data.get("meta") or {}
    for key, raw_value in raw_overrides.items():
        coerced, expires_at = _compute_expiry(raw_value, meta, now)
        if coerced is None:
            continue
        if expires_at and expires_at <= now:
            continue
        overrides[key] = coerced
    return overrides


def load_flags(
    *,
    now: datetime | None = None,
    auto_path: Path | None = None,
    manual_path: Path | None = None,
    effective_path: Path | None = None,
) -> Dict[str, bool]:
    """Load manual and auto signal flags, merge (manual > auto), and persist effective state."""

    reference_time = now or datetime.now(timezone.utc)
    auto_path = auto_path or AUTO_PATH
    manual_path = manual_path or MANUAL_PATH
    effective_path = effective_path or EFFECTIVE_PATH

    for required_path in (auto_path, manual_path):
        _ensure_file(required_path)

    with auto_path.open("r", encoding="utf-8") as handle:
        auto_data = yaml.safe_load(handle) or {}
    with manual_path.open("r", encoding="utf-8") as handle:
        manual_data = yaml.safe_load(handle) or {}

    auto_overrides = _prune_overrides(auto_data, reference_time)
    manual_overrides = _prune_overrides(manual_data, reference_time)

    signals: Dict[str, bool] = DEFAULT_FLAGS.copy()
    signals.update(auto_overrides)
    signals.update(manual_overrides)

    effective_payload = {
        "meta": {
            "generated_at": reference_time.isoformat(),
            "source": "config.flags",
        },
        "signals": signals,
        "auto_overrides": auto_overrides,
        "manual_overrides": manual_overrides,
    }

    effective_path.parent.mkdir(parents=True, exist_ok=True)
    with effective_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(effective_payload, handle, sort_keys=True)

    return signals


__all__ = ["load_flags"]
