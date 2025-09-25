import datetime as dt
import tempfile
from pathlib import Path

import pytest
import yaml

from config.flags import load_flags


def _write_yaml(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=True)


def test_manual_overrides_take_precedence(tmp_path):
    auto_path = tmp_path / "auto.yaml"
    manual_path = tmp_path / "manual.yaml"
    effective_path = tmp_path / "effective.yaml"
    now = dt.datetime(2025, 9, 21, tzinfo=dt.timezone.utc)

    _write_yaml(
        auto_path,
        {
            "overrides": {
                "publish_edges": True,
                "show_confidence_badge": False,
            },
            "meta": {"managed_by": "auto", "updated_at": now.isoformat()},
        },
    )
    _write_yaml(
        manual_path,
        {
            "overrides": {
                "show_confidence_badge": True,
            },
            "meta": {"managed_by": "manual", "updated_at": now.isoformat()},
        },
    )

    flags = load_flags(
        now=now,
        auto_path=auto_path,
        manual_path=manual_path,
        effective_path=effective_path,
    )
    assert flags["publish_edges"] is True
    assert flags["show_confidence_badge"] is True

    effective = yaml.safe_load(effective_path.read_text())
    assert effective["signals"]["show_confidence_badge"] is True


def test_manual_ttl_expired(tmp_path):
    auto_path = tmp_path / "auto.yaml"
    manual_path = tmp_path / "manual.yaml"
    effective_path = tmp_path / "effective.yaml"

    now = dt.datetime(2025, 9, 21, tzinfo=dt.timezone.utc)
    earlier = now - dt.timedelta(hours=2)

    _write_yaml(
        auto_path,
        {
            "overrides": {"publish_edges": False},
            "meta": {"managed_by": "auto", "updated_at": now.isoformat()},
        },
    )
    _write_yaml(
        manual_path,
        {
            "overrides": {
                "publish_edges": {
                    "value": True,
                    "updated_at": earlier.isoformat(),
                    "ttl_minutes": 30,
                }
            },
            "meta": {"managed_by": "manual", "updated_at": earlier.isoformat()},
        },
    )

    flags = load_flags(
        now=now,
        auto_path=auto_path,
        manual_path=manual_path,
        effective_path=effective_path,
    )
    assert flags["publish_edges"] is False


def test_manual_active_within_ttl(tmp_path):
    auto_path = tmp_path / "auto.yaml"
    manual_path = tmp_path / "manual.yaml"
    effective_path = tmp_path / "effective.yaml"

    now = dt.datetime(2025, 9, 21, tzinfo=dt.timezone.utc)
    recent = now - dt.timedelta(minutes=10)

    _write_yaml(
        auto_path,
        {
            "overrides": {"publish_edges": False},
            "meta": {"managed_by": "auto", "updated_at": now.isoformat()},
        },
    )
    _write_yaml(
        manual_path,
        {
            "overrides": {
                "publish_edges": {
                    "value": True,
                    "updated_at": recent.isoformat(),
                    "ttl_minutes": 60,
                }
            },
            "meta": {"managed_by": "manual", "updated_at": recent.isoformat()},
        },
    )

    flags = load_flags(
        now=now,
        auto_path=auto_path,
        manual_path=manual_path,
        effective_path=effective_path,
    )
    assert flags["publish_edges"] is True


def test_effective_file_written(tmp_path):
    auto_path = tmp_path / "auto.yaml"
    manual_path = tmp_path / "manual.yaml"
    effective_path = tmp_path / "effective.yaml"

    now = dt.datetime(2025, 9, 21, tzinfo=dt.timezone.utc)
    _write_yaml(auto_path, {"overrides": {}, "meta": {"managed_by": "auto", "updated_at": now.isoformat()}})
    _write_yaml(manual_path, {"overrides": {}, "meta": {"managed_by": "manual", "updated_at": now.isoformat()}})

    flags = load_flags(
        now=now,
        auto_path=auto_path,
        manual_path=manual_path,
        effective_path=effective_path,
    )
    assert effective_path.exists()
    effective = yaml.safe_load(effective_path.read_text())
    assert effective["signals"] == flags
