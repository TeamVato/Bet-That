#!/usr/bin/env python3
"""Master pipeline for PlayerProfiler strategy execution."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from playerprofiler_strategy_engine import StrategyEngine
from validate_playerprofiler_update import PlayerProfilerValidator


def main() -> None:
    backend_root = Path(__file__).resolve().parents[1]

    print("\n" + "=" * 60)
    print("BET-THAT STRATEGY PIPELINE EXECUTION")
    print("=" * 60)

    # Step 1: Validation
    print("\n[STEP] Validating PlayerProfiler data...")
    validator = PlayerProfilerValidator()
    validation = validator.run_complete_validation()

    warnings = validation.get("warnings") or []
    if warnings:
        print("\n[WARN] Data warnings detected:")
        for warning in warnings:
            print(f"  - {warning}")

        try:
            response = input("\nProceed anyway? (y/n): ").strip().lower()
        except EOFError:
            print('\n[INFO] No input detected; defaulting to proceed.')
            response = 'y'
        if response != "y":
            print("Execution cancelled")
            return

    # Step 2: Strategies
    print("\n[STEP] Running edge detection strategies...")
    engine = StrategyEngine(validation)
    edges = engine.run_all_strategies()
    summary = engine.get_edge_summary()

    print(f"\n[RESULT] Found {len(edges)} total edges:")
    for strategy, count in summary.items():
        print(f"  - {strategy}: {count} edges")

    # Step 3: Persist edges
    output_path = backend_root / "data/edges_current.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        json.dump(
            {
                "generated": datetime.now().isoformat(),
                "edges": edges,
                "edge_summary": summary,
                "data_quality": engine.freshness_score,
            },
            f,
            indent=2,
        )

    print(f"\n[INFO] Edges saved to {output_path}")

    if len(edges) < 10:
        print("\n[WARN] Fewer than 10 edges detected")
        print("Possible issues:")
        print("  1. Data may be too stale")
        print("  2. Missing critical columns")
        print("  3. Defensive rankings not loaded")
    elif len(edges) > 20:
        print("\n[WARN] Many edges detected - verify quality")
    else:
        print("\n[OK] Edge count within expected range (10-15)")


if __name__ == "__main__":
    main()
