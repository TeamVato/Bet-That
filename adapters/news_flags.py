"""Manual YAML-based overrides for injuries, snap counts, etc."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

DEFAULT_FLAGS_PATH = Path("storage/player_flags.yaml")


def load_player_flags(path: Path = DEFAULT_FLAGS_PATH) -> Dict[str, Dict[str, Any]]:
    """Return a dictionary of manual player flags keyed by player name."""
    if not path.exists():
        print(f"Player flags file not found at {path}; returning empty overrides.")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    flags: Dict[str, Dict[str, Any]] = {}
    if isinstance(data, dict):
        for player, payload in data.items():
            if isinstance(payload, dict):
                flags[player] = payload
    return flags
