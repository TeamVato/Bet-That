#!/usr/bin/env python3
"""Validation helper for updated PlayerProfiler data drops."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast

import numpy as np
import pandas as pd


class PlayerProfilerValidator:
    """Run a lightweight validation pipeline over PlayerProfiler exports."""

    def __init__(self) -> None:
        self.backend_root = Path(__file__).resolve().parents[1]
        self.base_path = Path("/Users/vato/work/Bet-That/storage/imports/PlayerProfiler")
        self.validation_results: Dict[str, object] = {
            "timestamp": datetime.now().isoformat(),
            "warnings": [],
        }
        self.column_mappings: Dict[str, Dict[str, str]] = {}
        self.canonical_columns: Dict[str, List[str]] = {
            "player_name": ["player", "player_name", "name", "full_name"],
            "position": ["position", "pos", "player_position"],
            "team": ["team", "team_abbr", "nfl_team", "current_team"],
            "qb.red_zone_pass_attempts": [
                "red_zone_pass_attempts",
                "rz_pass_att",
                "redzone_attempts",
                "red_zone_attempts",
            ],
            "qb.pass_touchdowns": [
                "pass_touchdowns",
                "pass_tds",
                "passing_tds",
                "td_passes",
            ],
            "qb.recent_attempts": [
                "attempts_last_3",
                "attempts_last_5",
                "attempts_rolling",
                "pass_attempts",
            ],
            "rb.defenders_in_box": [
                "defenders_in_box",
                "average_defenders_in_box",
                "box_defenders",
                "stacked_box_rate",
                "stacked_front_count",
            ],
            "rb.yards_created": [
                "yards_created",
                "yards_created_per_attempt",
                "yds_created",
                "yards_created_per_game",
            ],
            "rb.rush_attempts": ["rush_attempts", "rushing_attempts", "attempts"],
            "wr.targets": ["targets", "total_targets", "tgts"],
            "wr.catch_rate": ["catch_rate", "receptions_per_target", "reception_percentage"],
            "wr.air_yards": ["air_yards", "air_yards_share", "ay_share"],
        }
        self.validation_results["canonical_columns"] = list(self.canonical_columns.keys())

    # ------------------------------------------------------------------
    # Pipeline Steps
    # ------------------------------------------------------------------
    def run_complete_validation(self) -> Dict[str, object]:
        """Execute full validation pipeline."""
        print("[VALIDATION] PlayerProfiler Data Validation Starting...")

        self.inventory_files()
        self.map_strategy_columns()
        self.check_data_coverage()
        self.create_execution_plan()

        output_path = self.backend_root / "data/playerprofiler_validation.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w") as f:
            json.dump(self.validation_results, f, indent=2, default=self._json_serializer)

        print(f"[SAVE] Validation results saved to {output_path}")
        return self.validation_results

    # ------------------------------------------------------------------
    def inventory_files(self) -> None:
        """Catalog available PlayerProfiler files and basic metadata."""
        print("  - Building file inventory...")

        inventory: List[Dict[str, object]] = []
        for folder in sorted(self.base_path.glob("*")):
            if not folder.is_dir():
                continue

            for file in sorted(folder.glob("*.csv")):
                rel_path = file.relative_to(self.base_path).as_posix()
                size_bytes = file.stat().st_size
                modified = datetime.fromtimestamp(file.stat().st_mtime)

                columns, sample_rows = self._preview_file(file)

                inventory.append(
                    {
                        "folder": folder.name,
                        "file": file.name,
                        "relative_path": rel_path,
                        "size_bytes": size_bytes,
                        "modified": modified.isoformat(),
                        "columns": columns,
                        "sample_rows": sample_rows,
                    }
                )

        if not inventory:
            cast(List, self.validation_results["warnings"]).append("No PlayerProfiler CSV files discovered.")

        self.validation_results["inventory"] = inventory
        print(f"    - Catalogued {len(inventory)} CSV files")

    # ------------------------------------------------------------------
    def map_strategy_columns(self) -> None:
        """Identify which files provide critical strategy columns."""
        print("  - Mapping strategy-critical columns...")

        column_mappings: Dict[str, Dict[str, str]] = {}
        inventory = cast(List[Dict[str, Any]], self.validation_results.get("inventory", []))

        for canonical, synonyms in self.canonical_columns.items():
            best_match: Optional[Dict[str, str]] = None

            for item in inventory:
                columns = cast(List[str], item.get("columns", []))
                match = self._find_column_match(columns, synonyms)
                if match:
                    candidate = {
                        "file": item["relative_path"],
                        "column": match,
                        "folder": item.get("folder"),
                    }
                    if "player" in match or "position" in match:
                        # Prefer files with explicit player/position naming
                        best_match = candidate
                        break

                    if not best_match:
                        best_match = candidate

            if best_match:
                column_mappings[canonical] = best_match
            else:
                warning = f"Missing column for '{canonical}'"
                cast(List, self.validation_results.setdefault("warnings", [])).append(warning)

        self.column_mappings = column_mappings
        self.validation_results["column_mappings"] = column_mappings
        print(f"    - Mapped {len(column_mappings)} canonical columns")

    # ------------------------------------------------------------------
    def check_data_coverage(self) -> None:
        """Evaluate data freshness and column completeness."""
        print("  - Assessing data coverage and freshness...")

        freshness_scores: List[float] = []
        coverage_summary: Dict[str, Dict[str, Any]] = {}

        now = datetime.now()

        for canonical, mapping in self.column_mappings.items():
            file_path = self.base_path / mapping["file"]
            column_name = mapping["column"]

            try:
                series = pd.read_csv(
                    file_path, usecols=[column_name], squeeze=True, low_memory=False
                )
            except Exception:
                # Fall back to reading entire file if pandas struggles with usecols
                try:
                    df = pd.read_csv(file_path, low_memory=False)
                    series = df[column_name]
                except Exception as exc:
                    warning = (
                        f"Failed to evaluate coverage for {canonical} ({mapping['file']}): {exc}"
                    )
                    cast(List, self.validation_results.setdefault("warnings", [])).append(warning)
                    continue

            non_null = series.notna().sum()
            total = len(series)
            coverage = float(non_null / total) if total else 0.0
            coverage_summary[canonical] = {
                "file": mapping["file"],
                "column": column_name,
                "rows": float(total),
                "non_null_ratio": round(coverage, 4),
            }

            modified = datetime.fromtimestamp((self.base_path / mapping["file"]).stat().st_mtime)
            age_days = (now - modified).total_seconds() / 86_400
            freshness_scores.append(self._score_freshness(age_days))

            if coverage < 0.75 and canonical not in {"player_name", "position", "team"}:
                warning = (
                    f"Low coverage for {canonical} ({mapping['file']}::{column_name}) - "
                    f"{coverage:.0%} non-null"
                )
                cast(List, self.validation_results.setdefault("warnings", [])).append(warning)

        self.validation_results["coverage_summary"] = coverage_summary
        freshness = float(np.mean(freshness_scores)) if freshness_scores else 0.6
        self.validation_results["freshness_score"] = round(freshness, 3)
        print(f"    - Data freshness score: {freshness:.2f}")

    # ------------------------------------------------------------------
    def create_execution_plan(self) -> None:
        """Produce a recommended strategy execution plan."""
        print("  - Creating execution plan...")

        plan: Dict[str, Any] = {
            "strategies": [],
            "data_inputs": {},
        }

        canonical_to_strategy = {
            "qb.red_zone_pass_attempts": "QB TD Over 0.5",
            "qb.pass_touchdowns": "QB TD Over 0.5",
            "rb.defenders_in_box": "RB Rushing Under",
            "rb.yards_created": "RB Rushing Under",
            "wr.targets": "WR Receiving Under",
            "wr.catch_rate": "WR Receiving Under",
        }

        for canonical, mapping in self.column_mappings.items():
            strategy = canonical_to_strategy.get(canonical)
            if not strategy:
                continue

            coverage_summary = cast(Dict, self.validation_results.get("coverage_summary", {}))
            canonical_data = cast(Dict, coverage_summary.get(canonical, {}))
            cast(List, cast(Dict, plan.setdefault("data_inputs", {})).setdefault(strategy, [])).append(
                {
                    "canonical": canonical,
                    "file": mapping["file"],
                    "column": mapping["column"],
                    "coverage": canonical_data.get("non_null_ratio"),
                }
            )

        freshness_score = float(cast(float, self.validation_results.get("freshness_score", 1.0)) or 1.0)
        freshness_flag = (
            "fresh" if freshness_score >= 0.8 else "stale" if freshness_score < 0.5 else "mixed"
        )

        plan["strategies"] = [
            {
                "name": "QB TD Over 0.5",
                "status": "ready" if self._strategy_ready("qb") else "blocked",
                "notes": f"Data freshness is {freshness_flag}",
            },
            {
                "name": "RB Rushing Under",
                "status": "ready" if self._strategy_ready("rb") else "blocked",
                "notes": (
                    "Check stacked box coverage"
                    if not self._strategy_ready("rb")
                    else "Coverage acceptable"
                ),
            },
            {
                "name": "WR Receiving Under",
                "status": "ready" if self._strategy_ready("wr") else "blocked",
                "notes": "Needs targets + catch rate",
            },
        ]

        self.validation_results["execution_plan"] = plan
        print("    - Execution plan prepared")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _preview_file(self, path: Path) -> Tuple[List[str], List[Dict[str, object]]]:
        """Return column list and a tiny preview for reference."""
        try:
            df = pd.read_csv(path, nrows=5, low_memory=False)
        except Exception:
            return [], []

        columns = df.columns.tolist()
        sample_rows = df.head(3).to_dict(orient="records")

        return columns, sample_rows

    @staticmethod
    def _score_freshness(age_days: float) -> float:
        """Translate file age in days to a 0-1 freshness score."""
        if age_days <= 2:
            return 1.0
        if age_days <= 7:
            return 0.85
        if age_days <= 14:
            return 0.7
        if age_days <= 30:
            return 0.5
        if age_days <= 60:
            return 0.35
        return 0.2

    @staticmethod
    def _find_column_match(columns: List[str], synonyms: List[str]) -> Optional[str]:
        columns_lower = {col.lower(): col for col in columns}
        for synonym in synonyms:
            if synonym.lower() in columns_lower:
                return columns_lower[synonym.lower()]
        return None

    def _strategy_ready(self, prefix: str) -> bool:
        return any(key.startswith(prefix) for key in self.column_mappings.keys())

    @staticmethod
    def _json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        raise TypeError(f"Type {type(obj)} not serializable")


def main() -> None:
    validator = PlayerProfilerValidator()
    validator.run_complete_validation()


if __name__ == "__main__":
    main()
