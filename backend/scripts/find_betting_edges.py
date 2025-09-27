from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

CACHE_FILE = Path(__file__).resolve().parents[1] / "data" / "nfl_cache.json"
KEY_NUMBERS = [40, 41, 43, 44, 47, 50, 51, 55]


def _load_cache() -> Dict[str, Any]:
    if not CACHE_FILE.exists():
        raise FileNotFoundError(
            "Cached NFL data not found. Run scripts/run_nfl_data_pull.py first."
        )
    try:
        return json.loads(CACHE_FILE.read_text())
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Cache file is corrupted: {exc}") from exc


def _ensure_fresh(cache: Dict[str, Any]) -> None:
    expires_at = cache.get("expires_at")
    if not expires_at:
        raise RuntimeError("Cache payload missing expires_at; rerun the data pull script.")
    try:
        expiry_dt = datetime.fromisoformat(expires_at)
    except ValueError as exc:
        raise RuntimeError(f"Invalid expires_at timestamp: {expires_at}") from exc
    if datetime.now(timezone.utc) > expiry_dt:
        raise RuntimeError("Cached data is stale. Run scripts/run_nfl_data_pull.py to refresh.")


def _totals_summary(game: Dict[str, Any]) -> Dict[str, Any]:
    totals_points = game.get("totals_points") or []
    if not totals_points:
        return {"movement": 0.0, "key_hits": [], "sorted": []}
    points = [item["point"] for item in totals_points]
    movement = max(points) - min(points) if len(points) > 1 else 0.0
    sorted_points = sorted(totals_points, key=lambda item: item["point"])
    key_hits: List[float] = []
    avg_total = sum(points) / len(points)
    for key in KEY_NUMBERS:
        if abs(avg_total - key) < 0.5:
            key_hits.append(key)
    return {
        "movement": movement,
        "sorted": sorted_points,
        "average": avg_total,
        "key_hits": key_hits,
    }


def _build_recommendation(game: Dict[str, Any]) -> Dict[str, Any]:
    totals_info = _totals_summary(game)
    movement = totals_info["movement"]
    if movement < 2.0 or len(totals_info["sorted"]) < 2:
        return {}

    low = totals_info["sorted"][0]
    high = totals_info["sorted"][-1]
    confidence = "High" if movement >= 3.0 else "Medium"
    action = (
        f"Buy Under {high['point']:.1f} at {high['book']}"
        if confidence == "High"
        else f"Consider Over {low['point']:.1f} at {low['book']}"
    )

    return {
        "game": f"{game.get('away_team')} @ {game.get('home_team')}",
        "movement": round(movement, 1),
        "average_total": round(totals_info["average"], 1) if totals_info["average"] else None,
        "key_numbers": totals_info["key_hits"],
        "recommendation": action,
        "confidence": confidence,
        "lowest_total": low,
        "highest_total": high,
    }


def main() -> None:
    cache = _load_cache()
    _ensure_fresh(cache)
    games = cache.get("games", [])

    print("🎯 BETTING EDGE REPORT")
    print("=" * 28)
    if not games:
        print("No cached games available.")
        return

    edges_found = 0
    for game in games:
        rec = _build_recommendation(game)
        if not rec:
            continue
        edges_found += 1
        print(f"\n{rec['game']}")
        print(f"- Totals movement: {rec['movement']:.1f} points")
        if rec.get("average_total"):
            print(f"- Average total: {rec['average_total']:.1f}")
        if rec.get("key_numbers"):
            key_text = ", ".join(str(k) for k in rec["key_numbers"])
            print(f"- Key number(s): {key_text}")
        print(f"- Recommendation: {rec['recommendation']}")
        print(f"- Confidence: {rec['confidence']}")
        low = rec["lowest_total"]
        high = rec["highest_total"]
        print(f"- Shopping window: {low['book']} {low['point']:.1f} ({low.get('price', 0):+d})")
        if high != low:
            print(f"                 {high['book']} {high['point']:.1f} ({high.get('price', 0):+d})")

    if edges_found == 0:
        print("\nNo qualifying edges in the cached data. Re-run after market moves.")


if __name__ == "__main__":
    main()
