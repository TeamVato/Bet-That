#!/usr/bin/env python3
"""PlayerProfiler-driven betting strategy engine."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


@dataclass
class StrategyConfig:
    name: str
    canonical_requirements: List[str]
    max_edges: int


class StrategyEngine:
    """Evaluate betting edges using PlayerProfiler data with dynamic schemas."""

    DATA_ROOT = Path("/Users/vato/work/Bet-That/storage/imports/PlayerProfiler")

    def __init__(self, validation_data: Optional[Dict[str, object]] = None) -> None:
        self.validation_data = validation_data or {}
        self.column_map: Dict[str, Dict[str, str]] = self.validation_data.get("column_mappings", {})
        self.freshness_score: float = float(self.validation_data.get("freshness_score", 1.0) or 1.0)
        self.coverage_summary = self.validation_data.get("coverage_summary", {})

        self.configs = {
            "QB TD Over 0.5": StrategyConfig(
                name="QB TD Over 0.5",
                canonical_requirements=[
                    "qb.red_zone_pass_attempts",
                    "qb.pass_touchdowns",
                    "player_name",
                    "position",
                    "team",
                ],
                max_edges=5,
            ),
            "RB Rushing Under": StrategyConfig(
                name="RB Rushing Under",
                canonical_requirements=[
                    "rb.defenders_in_box",
                    "rb.yards_created",
                    "player_name",
                    "team",
                ],
                max_edges=5,
            ),
            "WR Receiving Under": StrategyConfig(
                name="WR Receiving Under",
                canonical_requirements=[
                    "wr.targets",
                    "wr.catch_rate",
                    "wr.air_yards",
                    "player_name",
                    "position",
                    "team",
                ],
                max_edges=4,
            ),
        }

        self.loaded_frames: Dict[str, pd.DataFrame] = {}
        self.strategy_frames: Dict[str, pd.DataFrame] = self._prepare_strategy_frames()

        self.edges: List[Dict[str, object]] = []
        self.edge_registry: Dict[str, List[Dict[str, object]]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run_all_strategies(self) -> List[Dict[str, object]]:
        print("Running strategy engine against PlayerProfiler data...")
        self.edges = []
        self.edge_registry = {}

        qb_df = self.strategy_frames.get("QB TD Over 0.5")
        if qb_df is not None:
            qb_edges = self.find_qb_td_edges(qb_df)
            self.edge_registry["QB TD Over 0.5"] = qb_edges
            self.edges.extend(qb_edges)
        else:
            print("  - QB dataset not available; skipping QB TD edges")

        rb_df = self.strategy_frames.get("RB Rushing Under")
        if rb_df is not None:
            rb_edges = self.find_rb_under_edges(rb_df)
            self.edge_registry["RB Rushing Under"] = rb_edges
            self.edges.extend(rb_edges)
        else:
            print("  - RB dataset not available; skipping RB rushing unders")

        wr_df = self.strategy_frames.get("WR Receiving Under")
        if wr_df is not None:
            wr_edges = self.find_wr_under_edges(wr_df)
            self.edge_registry["WR Receiving Under"] = wr_edges
            self.edges.extend(wr_edges)
        else:
            print("  - WR dataset not available; skipping WR receiving unders")

        self.edges.sort(key=lambda edge: edge.get("confidence", 0), reverse=True)
        return self.edges

    def get_edge_summary(self) -> Dict[str, int]:
        return {name: len(edges) for name, edges in self.edge_registry.items()}

    # ------------------------------------------------------------------
    # Strategy Implementations
    # ------------------------------------------------------------------
    def find_qb_td_edges(self, df: pd.DataFrame) -> List[Dict[str, object]]:
        """QB TD Over 0.5 - 90% historical win rate."""
        edges: List[Dict[str, object]] = []

        name_col = self.find_column(
            df, ["name", "player", "player_name", "full_name"], "player_name"
        )
        position_col = self.find_column(df, ["position", "pos", "player_position"], "position")
        team_col = self.find_column(df, ["team", "team_abbr", "current_team", "off_team"], "team")
        rz_col = self.find_column(
            df,
            ["red_zone_pass_attempts", "rz_pass_att", "redzone_attempts", "red_zone_attempts"],
            "qb.red_zone_pass_attempts",
        )
        td_col = self.find_column(
            df,
            ["pass_touchdowns", "pass_tds", "passing_tds", "passing_touchdowns", "pass_td"],
            "qb.pass_touchdowns",
        )

        missing = [col for col in [name_col, position_col, rz_col, td_col] if col is None]
        if missing:
            print(f"  - QB TD strategy missing required columns: {missing}")
            return edges

        qb_df = df[df[position_col].astype(str).str.upper().isin(["QB", "QUARTERBACK"])].copy()
        if qb_df.empty:
            qb_df = df.copy()

        qb_df = qb_df.drop_duplicates(
            subset=[col for col in [name_col, team_col] if col]
        ).reset_index(drop=True)

        rz_threshold = self._quantile_threshold(qb_df[rz_col], 0.65, 4.0)
        td_threshold = self._quantile_threshold(qb_df[td_col], 0.6, 1.0)

        for _, qb in qb_df.iterrows():
            rz_attempts = self._safe_number(qb.get(rz_col))
            recent_tds = self._safe_number(qb.get(td_col))
            if rz_attempts is None or recent_tds is None:
                continue

            if rz_attempts < rz_threshold or recent_tds < td_threshold:
                continue

            name = self._clean_string(qb.get(name_col), "Unknown")
            team = self._clean_string(qb.get(team_col), "?") if team_col else "?"

            confidence = min(
                0.95,
                0.68 + (rz_attempts - rz_threshold) * 0.025 + (recent_tds - td_threshold) * 0.04,
            )
            confidence = max(0.5, confidence * self.freshness_score)
            expected_value = 0.08 + min(0.05, (rz_attempts - rz_threshold) * 0.01)

            edges.append(
                {
                    "strategy": "QB TD Over 0.5",
                    "type": "QB TD Over 0.5",
                    "player": name,
                    "team": team,
                    "confidence": round(confidence, 3),
                    "expected_value": round(expected_value, 3),
                    "data_quality": round(self.freshness_score, 3),
                    "metrics": {
                        "red_zone_attempts": rz_attempts,
                        "recent_touchdowns": recent_tds,
                        "thresholds": {
                            "red_zone": rz_threshold,
                            "touchdowns": td_threshold,
                        },
                    },
                }
            )

        return self._limit_edges("QB TD Over 0.5", edges)

    def find_rb_under_edges(self, df: pd.DataFrame) -> List[Dict[str, object]]:
        """RB Rushing Under - 80% historical win rate."""
        edges: List[Dict[str, object]] = []

        filtered_df = df
        if "run" in df.columns:
            filtered_df = df[df["run"] == 1].copy()
            if filtered_df.empty:
                filtered_df = df.copy()

        name_col = self.find_column(
            filtered_df,
            ["name", "player", "player_name", "runner", "rusher", "full_name"],
            "player_name",
        )
        team_col = self.find_column(
            filtered_df, ["team", "team_abbr", "current_team", "off_team"], "team"
        )
        box_col = self.find_column(
            filtered_df,
            [
                "defenders_in_box",
                "average_defenders_in_box",
                "average_defenders_in_the_box",
                "box_defenders",
                "stacked_box_rate",
            ],
            "rb.defenders_in_box",
        )
        created_col = self.find_column(
            filtered_df,
            ["yards_created", "yards_created_per_attempt", "yards_created_per_rush", "yds_created"],
            "rb.yards_created",
        )

        if name_col is None or box_col is None or created_col is None:
            print("  - RB Under strategy missing required columns")
            return edges

        rb_df = filtered_df[[name_col, team_col, box_col, created_col]].copy()
        rb_df[name_col] = rb_df[name_col].astype(str).str.strip()
        if team_col:
            rb_df[team_col] = rb_df[team_col].astype(str).str.strip()

        group_keys = [col for col in [name_col, team_col] if col]
        grouped = rb_df.groupby(group_keys, dropna=False)
        agg_df = grouped.agg({box_col: "mean", created_col: "mean"}).reset_index()
        attempts = grouped.size().reset_index(name="attempts")
        agg_df = agg_df.merge(attempts, on=group_keys, how="left")

        if agg_df.empty:
            return edges

        box_threshold = self._quantile_threshold(agg_df[box_col], 0.6, 6.0)
        created_threshold = self._quantile_threshold(agg_df[created_col], 0.4, 2.0, clamp_low=False)

        for _, rb in agg_df.iterrows():
            box_defenders = self._safe_number(rb.get(box_col))
            yards_created = self._safe_number(rb.get(created_col))
            attempts_val = self._safe_number(rb.get("attempts"))
            if box_defenders is None or yards_created is None:
                continue

            if box_defenders < box_threshold:
                continue
            if yards_created is not None and yards_created > created_threshold:
                continue
            if attempts_val is not None and attempts_val < 8:
                continue

            name = self._clean_string(rb.get(name_col), "Unknown")
            team = self._clean_string(rb.get(team_col), "?") if team_col else "?"

            confidence = 0.62 + (box_defenders - box_threshold) * 0.04
            if yards_created is not None:
                confidence -= (yards_created - created_threshold) * 0.03
            if attempts_val is not None:
                confidence += min(0.08, (attempts_val - 12) * 0.005)
            confidence = min(0.9, max(0.45, confidence)) * self.freshness_score

            expected_value = 0.06 + min(0.04, (box_defenders - box_threshold) * 0.012)

            edges.append(
                {
                    "strategy": "RB Rushing Under",
                    "type": "RB Rushing Under",
                    "player": name,
                    "team": team,
                    "confidence": round(confidence, 3),
                    "expected_value": round(expected_value, 3),
                    "data_quality": round(self.freshness_score, 3),
                    "metrics": {
                        "defenders_in_box": box_defenders,
                        "yards_created": yards_created,
                        "attempts": attempts_val,
                        "thresholds": {
                            "box": box_threshold,
                            "yards_created": created_threshold,
                        },
                    },
                }
            )

        return self._limit_edges("RB Rushing Under", edges)

    def find_wr_under_edges(self, df: pd.DataFrame) -> List[Dict[str, object]]:
        """WR Receiving Under - focuses on volume inefficiency."""
        edges: List[Dict[str, object]] = []

        name_col = self.find_column(
            df, ["name", "player", "player_name", "full_name"], "player_name"
        )
        position_col = self.find_column(df, ["position", "pos", "player_position"], "position")
        team_col = self.find_column(df, ["team", "team_abbr", "current_team", "off_team"], "team")
        targets_col = self.find_column(df, ["targets", "total_targets", "tgts"], "wr.targets")
        catch_rate_col = self.find_column(
            df,
            ["catch_rate", "reception_percentage", "receptions_per_target", "catch_pct"],
            "wr.catch_rate",
        )
        air_yards_col = self.find_column(
            df, ["air_yards", "air_yards_share", "ay_share"], "wr.air_yards"
        )

        missing = [
            col for col in [name_col, position_col, targets_col, catch_rate_col] if col is None
        ]
        if missing:
            print(f"  - WR Under strategy missing required columns: {missing}")
            return edges

        wr_df = df[df[position_col].astype(str).str.upper().isin(["WR", "WIDE RECEIVER"])].copy()
        if wr_df.empty:
            return edges

        wr_df = wr_df.drop_duplicates(
            subset=[col for col in [name_col, team_col] if col]
        ).reset_index(drop=True)

        wr_df[catch_rate_col] = pd.to_numeric(wr_df[catch_rate_col], errors="coerce")
        if wr_df[catch_rate_col].max(skipna=True) and wr_df[catch_rate_col].max() > 1.5:
            wr_df[catch_rate_col] = wr_df[catch_rate_col] / 100.0
        wr_df[targets_col] = pd.to_numeric(wr_df[targets_col], errors="coerce")

        air_yards_optional = False
        if air_yards_col is not None and air_yards_col in wr_df.columns:
            wr_df[air_yards_col] = pd.to_numeric(wr_df[air_yards_col], errors="coerce")
            valid_air_yards = wr_df[air_yards_col].notna().sum()
            air_yards_optional = valid_air_yards < max(15, int(len(wr_df) * 0.3))
        else:
            air_yards_optional = True

        target_threshold = self._quantile_threshold(wr_df[targets_col], 0.7, 6.0)
        catch_rate_threshold = self._quantile_threshold(
            wr_df[catch_rate_col], 0.35, 0.62, clamp_low=False
        )
        if air_yards_col is not None and not air_yards_optional:
            air_yards_threshold = self._quantile_threshold(
                wr_df[air_yards_col], 0.35, 45.0, clamp_low=False
            )
        else:
            air_yards_threshold = None

        for _, wr in wr_df.iterrows():
            targets = self._safe_number(wr.get(targets_col))
            catch_rate = self._safe_number(wr.get(catch_rate_col))
            air_yards = self._safe_number(wr.get(air_yards_col)) if air_yards_col else None
            if targets is None or catch_rate is None:
                continue

            if targets < target_threshold:
                continue

            efficiency_flag = catch_rate <= catch_rate_threshold
            depth_flag = False
            if air_yards_threshold is not None and air_yards is not None:
                depth_flag = air_yards <= air_yards_threshold
            elif air_yards_optional:
                depth_flag = True

            if not (efficiency_flag or depth_flag):
                continue

            name = self._clean_string(wr.get(name_col), "Unknown")
            team = self._clean_string(wr.get(team_col), "?") if team_col else "?"

            catch_penalty = (catch_rate_threshold - catch_rate) if efficiency_flag else 0
            depth_penalty = 0.0
            if air_yards_threshold is not None and air_yards is not None:
                depth_penalty = max(
                    0, (air_yards_threshold - air_yards) / max(air_yards_threshold, 1.0)
                )

            confidence = (
                0.6
                + (targets - target_threshold) * 0.015
                + catch_penalty * 0.12
                + depth_penalty * 0.08
            )
            confidence = min(0.88, max(0.45, confidence)) * self.freshness_score
            expected_value = 0.05 + min(0.04, (targets - target_threshold) * 0.007)

            notes_parts = [f"Targets {targets:.1f} vs {target_threshold:.1f}"]
            notes_parts.append(
                f"Catch% {catch_rate:.2f} <= {catch_rate_threshold:.2f}"
                if efficiency_flag
                else f"Catch% {catch_rate:.2f}"
            )
            if air_yards_threshold is not None and air_yards is not None:
                notes_parts.append(
                    f"Air yards {air_yards:.1f} <= {air_yards_threshold:.1f}"
                    if depth_flag
                    else f"Air yards {air_yards:.1f}"
                )
            elif air_yards_optional:
                notes_parts.append("Air yards data incomplete")

            edges.append(
                {
                    "strategy": "WR Receiving Under",
                    "type": "WR Receiving Under",
                    "player": name,
                    "team": team,
                    "confidence": round(confidence, 3),
                    "expected_value": round(expected_value, 3),
                    "data_quality": round(self.freshness_score, 3),
                    "metrics": {
                        "targets": targets,
                        "catch_rate": catch_rate,
                        "air_yards": air_yards,
                        "thresholds": {
                            "targets": target_threshold,
                            "catch_rate": catch_rate_threshold,
                            "air_yards": air_yards_threshold,
                        },
                    },
                    "notes": "; ".join(notes_parts),
                }
            )

        return self._limit_edges("WR Receiving Under", edges)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def find_column(
        self, df: pd.DataFrame, possible_names: List[str], canonical: Optional[str] = None
    ) -> Optional[str]:
        """Find column by canonical mapping or fallback names."""
        if canonical and canonical in self.column_map:
            mapped_col = self.column_map[canonical]["column"]
            if mapped_col in df.columns:
                return mapped_col

        lowered = {col.lower(): col for col in df.columns}
        for name in possible_names:
            if name.lower() in lowered:
                return lowered[name.lower()]
        return None

    def _prepare_strategy_frames(self) -> Dict[str, pd.DataFrame]:
        frames: Dict[str, pd.DataFrame] = {}
        for strategy, config in self.configs.items():
            file_choice = self._select_best_file(config.canonical_requirements)
            if not file_choice:
                continue
            df = self._load_dataframe(file_choice)
            if df is not None:
                frames[strategy] = df
        return frames

    def _select_best_file(self, canonical_keys: List[str]) -> Optional[str]:
        scores: Dict[str, int] = {}
        for key in canonical_keys:
            mapping = self.column_map.get(key)
            if not mapping:
                continue
            file_name = mapping.get("file")
            if file_name:
                scores[file_name] = scores.get(file_name, 0) + 1
        if not scores:
            return None
        return max(scores.items(), key=lambda item: item[1])[0]

    def _load_dataframe(self, relative_path: str) -> Optional[pd.DataFrame]:
        if relative_path in self.loaded_frames:
            return self.loaded_frames[relative_path]

        file_path = self.DATA_ROOT / relative_path
        if not file_path.exists():
            print(f"  - Data file missing: {relative_path}")
            return None

        try:
            df = pd.read_csv(file_path, low_memory=False)
        except Exception as exc:
            print(f"  - Failed to load {relative_path}: {exc}")
            return None

        self.loaded_frames[relative_path] = df
        return df

    @staticmethod
    def _clean_string(value: object, fallback: str = "?") -> str:
        if value is None:
            return fallback
        text = str(value).strip()
        if not text or text.lower() in {"nan", "none", "null"}:
            return fallback
        return text

    @staticmethod
    def _safe_number(value: object) -> Optional[float]:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _quantile_threshold(
        series: pd.Series, quantile: float, fallback: float, clamp_low: bool = True
    ) -> float:
        values = pd.to_numeric(series, errors="coerce").dropna()
        if values.empty:
            return float(fallback)
        threshold = float(values.quantile(quantile))
        if clamp_low and threshold < fallback:
            return float(max(threshold, fallback * 0.85))
        if not clamp_low and threshold > fallback:
            return float(min(threshold, fallback * 1.15))
        return threshold

    def _limit_edges(
        self, strategy_name: str, edges: List[Dict[str, object]]
    ) -> List[Dict[str, object]]:
        config = self.configs[strategy_name]
        edges.sort(key=lambda edge: edge.get("confidence", 0), reverse=True)
        return edges[: config.max_edges]


def main() -> None:
    validation_path = Path("/Users/vato/work/Bet-That/backend/data/playerprofiler_validation.json")
    if not validation_path.exists():
        raise SystemExit("Validation data missing. Run validate_playerprofiler_update.py first.")

    with validation_path.open() as f:
        validation_data = json.load(f)

    engine = StrategyEngine(validation_data)
    edges = engine.run_all_strategies()
    summary = engine.get_edge_summary()

    report = {
        "generated_at": datetime.now().isoformat(),
        "data_quality": engine.freshness_score,
        "edge_summary": summary,
        "edges": edges,
    }

    output_path = Path("/Users/vato/work/Bet-That/backend/data/edges_current.json")
    with output_path.open("w") as f:
        json.dump(report, f, indent=2)

    print(f"Saved {len(edges)} edges to {output_path}")
    for name, count in summary.items():
        print(f"  - {name}: {count} edges")


if __name__ == "__main__":
    main()
