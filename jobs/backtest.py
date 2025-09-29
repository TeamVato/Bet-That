from __future__ import annotations

import argparse

import pandas as pd

from engine.calibration import brier_score, bucket_calibration


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--start", type=str, required=False, help="Filter by date >= start (if column present)"
    )
    args = ap.parse_args()

    df = pd.read_csv("storage/exports/edges_latest.csv")
    if args.start and "date" in df.columns:
        df = df[df["date"] >= args.start]

    p_col = "p_model_shrunk" if "p_model_shrunk" in df.columns else "model_p"
    if p_col not in df.columns:
        raise SystemExit("No probability column found (model_p or p_model_shrunk)")
    p = df[p_col].fillna(0.5)
    y = df.get("won", pd.Series([0] * len(df)))

    cal = bucket_calibration(pd.DataFrame({"p": p, "y": y}), "p", "y", n=10)
    print("Brier:", brier_score(p, y))
    print(cal)


if __name__ == "__main__":
    main()
