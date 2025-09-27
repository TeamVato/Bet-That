#!/usr/bin/env python3
"""Comprehensive edge analysis across cached NFL odds."""

import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

DATA_FILE = Path("/Users/vato/work/Bet-That/backend/data/nfl_pull_20250927_074502.json")
KEY_NUMBERS = [40, 41, 43, 44, 47, 50, 51, 55]
MOVEMENT_MEDIUM = 2.0
MOVEMENT_HIGH = 3.0
FRESHNESS_THRESHOLD_HOURS = 2.0


def load_data() -> Dict[str, Any]:
    """Load cached odds payload."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Cached data file not found: {DATA_FILE}")
    with DATA_FILE.open() as f:
        return json.load(f)


def american_odds_edge(price: int) -> float:
    """Rudimentary expected edge estimate from the best available price."""
    if price == 0:
        return 0.0
    implied_prob = 100 / (price + 100) if price > 0 else -price / (-price + 100)
    edge = (0.5 - implied_prob) * 100  # assume fair price at -110 (~52.4%)
    return round(edge, 2)


def build_totals_index(game: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Map bookmaker key to its total point and associated metadata."""
    totals = {}
    for bookmaker in game.get("bookmakers", []):
        totals_list = bookmaker.get("totals") or []
        if not totals_list:
            continue
        points = {entry.get("point") for entry in totals_list if entry.get("point") is not None}
        if not points:
            continue
        # Totals feed should have a single point value per bookmaker
        point = points.pop()
        over = next((o for o in totals_list if o.get("name", "").lower() == "over"), None)
        under = next((o for o in totals_list if o.get("name", "").lower() == "under"), None)
        totals[bookmaker["key"]] = {
            "book": bookmaker["title"],
            "point": point,
            "over_price": over.get("price") if over else None,
            "under_price": under.get("price") if under else None,
            "last_update": bookmaker.get("last_update"),
        }
    return totals


def detect_movement_edges(game: Dict[str, Any], totals_index: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    edges: List[Dict[str, Any]] = []
    if len(totals_index) < 2:
        return edges
    points = [entry["point"] for entry in totals_index.values() if entry.get("point") is not None]
    if not points:
        return edges
    max_point = max(points)
    min_point = min(points)
    movement = max_point - min_point
    if movement < MOVEMENT_MEDIUM:
        return edges
    high_conf = movement >= MOVEMENT_HIGH
    best_over = max(
        (entry for entry in totals_index.values() if entry.get("over_price") is not None),
        key=lambda e: e["over_price"],
        default=None,
    )
    best_under = max(
        (entry for entry in totals_index.values() if entry.get("under_price") is not None),
        key=lambda e: e["under_price"],
        default=None,
    )
    edges.append({
        "game": f"{game['away_team']} @ {game['home_team']}",
        "movement": round(movement, 2),
        "min_total": min_point,
        "max_total": max_point,
        "max_book": next((b for b, v in totals_index.items() if v["point"] == max_point), None),
        "min_book": next((b for b, v in totals_index.items() if v["point"] == min_point), None),
        "best_over": (
            f"Over {best_over['point']} @ {best_over['book']} ({best_over['over_price']})"
            if best_over
            else None
        ),
        "best_under": (
            f"Under {best_under['point']} @ {best_under['book']} ({best_under['under_price']})"
            if best_under
            else None
        ),
        "edge_percentage": round(max(0.0, movement - MOVEMENT_MEDIUM) * 2.5, 2),
        "confidence": "high" if high_conf else "medium",
    })
    return edges


def detect_line_shopping(game: Dict[str, Any], totals_index: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    opportunities: List[Dict[str, Any]] = []
    prices_by_point: Dict[float, List[Dict[str, Any]]] = defaultdict(list)
    for book, entry in totals_index.items():
        point = entry.get("point")
        if point is None:
            continue
        prices_by_point[point].append({"book": entry["book"], "over": entry.get("over_price"), "under": entry.get("under_price")})

    for point, offers in prices_by_point.items():
        if len(offers) < 2:
            continue
        over_prices = [offer["over"] for offer in offers if offer.get("over") is not None]
        under_prices = [offer["under"] for offer in offers if offer.get("under") is not None]
        if over_prices:
            best_over = max(over_prices)
            worst_over = min(over_prices)
            if best_over - worst_over >= 15:  # 15 cents improvement threshold
                best_book = next(offer for offer in offers if offer.get("over") == best_over)
                opportunities.append({
                    "game": f"{game['away_team']} @ {game['home_team']}",
                    "point": point,
                    "bet": "Over",
                    "best_price": best_over,
                    "worst_price": worst_over,
                    "best_book": best_book["book"],
                    "improvement_cents": best_over - worst_over,
                    "edge_percentage": american_odds_edge(best_over),
                })
        if under_prices:
            best_under = max(under_prices)
            worst_under = min(under_prices)
            if best_under - worst_under >= 15:
                best_book = next(offer for offer in offers if offer.get("under") == best_under)
                opportunities.append({
                    "game": f"{game['away_team']} @ {game['home_team']}",
                    "point": point,
                    "bet": "Under",
                    "best_price": best_under,
                    "worst_price": worst_under,
                    "best_book": best_book["book"],
                    "improvement_cents": best_under - worst_under,
                    "edge_percentage": american_odds_edge(best_under),
                })
    return opportunities


def detect_key_crossings(game: Dict[str, Any], totals_index: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    crossings: List[Dict[str, Any]] = []
    points = sorted({entry["point"] for entry in totals_index.values() if entry.get("point") is not None})
    if len(points) < 2:
        return crossings
    for key_num in KEY_NUMBERS:
        below = any(point < key_num for point in points)
        above = any(point > key_num for point in points)
        if below and above:
            crossings.append({
                "game": f"{game['away_team']} @ {game['home_team']}",
                "key_number": key_num,
                "lowest_total": points[0],
                "highest_total": points[-1],
                "spread": round(points[-1] - points[0], 2),
            })
    return crossings


def check_freshness(game: Dict[str, Any], totals_index: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    stale_entries: List[Dict[str, Any]] = []
    now = datetime.now(timezone.utc)
    for book, entry in totals_index.items():
        ts = entry.get("last_update")
        if not ts:
            continue
        try:
            updated_at = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            stale_entries.append({
                "game": f"{game['away_team']} @ {game['home_team']}",
                "book": book,
                "issue": f"Invalid timestamp: {ts}",
            })
            continue
        age_hours = (now - updated_at).total_seconds() / 3600
        if age_hours > FRESHNESS_THRESHOLD_HOURS:
            stale_entries.append({
                "game": f"{game['away_team']} @ {game['home_team']}",
                "book": book,
                "last_update": ts,
                "age_hours": round(age_hours, 2),
            })
    return stale_entries


def main() -> int:
    try:
        payload = load_data()
    except Exception as exc:  # pragma: no cover - CLI output
        print(json.dumps({"error": str(exc)}))
        return 1

    games = payload.get("games", [])
    high_confidence: List[Dict[str, Any]] = []
    medium_confidence: List[Dict[str, Any]] = []
    line_shopping: List[Dict[str, Any]] = []
    key_crossings: List[Dict[str, Any]] = []
    freshness_issues: List[Dict[str, Any]] = []

    for game in games:
        totals_index = build_totals_index(game)
        for movement_edge in detect_movement_edges(game, totals_index):
            if movement_edge["confidence"] == "high":
                high_confidence.append(movement_edge)
            else:
                medium_confidence.append(movement_edge)
        line_shopping.extend(detect_line_shopping(game, totals_index))
        key_crossings.extend(detect_key_crossings(game, totals_index))
        freshness_issues.extend(check_freshness(game, totals_index))

    generated_at_raw = payload.get("generated_at")
    data_age_hours = None
    if generated_at_raw:
        try:
            generated_at = datetime.fromisoformat(generated_at_raw.replace("Z", "+00:00"))
            data_age_hours = round((datetime.now(timezone.utc) - generated_at).total_seconds() / 3600, 2)
        except ValueError:
            data_age_hours = None

    edges_found = {
        "high_confidence": high_confidence,
        "medium_confidence": medium_confidence,
        "line_shopping": line_shopping,
        "key_crossings": key_crossings,
        "freshness_issues": freshness_issues,
        "edges_total": len(high_confidence) + len(medium_confidence) + len(line_shopping),
        "data_age_hours": data_age_hours,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    print(json.dumps(edges_found, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
