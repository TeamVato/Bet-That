from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = BASE_DIR / "data"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_FILE = CACHE_DIR / "nfl_cache.json"
KEY_NUMBERS = [40, 41, 43, 44, 47, 50, 51, 55]
CACHE_TTL = timedelta(minutes=30)
OUTPUT_PREFIX = "nfl_pull_"

if str(BASE_DIR) not in os.sys.path:
    os.sys.path.insert(0, str(BASE_DIR))

from app.services.odds_api_manager import OddsAPIManager  # noqa: E402


@dataclass
class TokenStatus:
    index: int
    key_suffix: str
    remaining: Optional[int]
    used: Optional[int]
    status: str
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "key_suffix": self.key_suffix,
            "remaining": self.remaining,
            "used": self.used,
            "status": self.status,
            "error": self.error,
        }


def _load_env() -> None:
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)


async def check_token_status(keys: List[str]) -> List[TokenStatus]:
    statuses: List[TokenStatus] = []
    timeout = httpx.Timeout(10.0, read=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        for idx, key in enumerate(keys, start=1):
            try:
                response = await client.get(
                    "https://api.the-odds-api.com/v4/sports", params={"apiKey": key}
                )
            except Exception as exc:  # pragma: no cover - network guard
                statuses.append(
                    TokenStatus(
                        index=idx,
                        key_suffix=key[-6:],
                        remaining=None,
                        used=None,
                        status="error",
                        error=str(exc),
                    )
                )
                continue

            if response.status_code == 200:
                remaining_header = response.headers.get("x-requests-remaining")
                used_header = response.headers.get("x-requests-used")
                remaining = int(remaining_header) if remaining_header and remaining_header.isdigit() else None
                used = int(used_header) if used_header and used_header.isdigit() else None
                statuses.append(
                    TokenStatus(
                        index=idx,
                        key_suffix=key[-6:],
                        remaining=remaining,
                        used=used,
                        status="ok",
                    )
                )
            else:
                statuses.append(
                    TokenStatus(
                        index=idx,
                        key_suffix=key[-6:],
                        remaining=None,
                        used=None,
                        status=f"http_{response.status_code}",
                        error=response.text[:200],
                    )
                )
    return statuses


def _choose_best_key(keys: List[str], statuses: List[TokenStatus]) -> str:
    lookup = {status.index: status for status in statuses}
    best_key = keys[0]
    best_remaining = -1
    for idx, key in enumerate(keys, start=1):
        status = lookup.get(idx)
        if status and status.remaining is not None and status.remaining > best_remaining:
            best_remaining = status.remaining
            best_key = key
    return best_key


async def fetch_odds_with_key(api_key: str) -> List[Dict[str, Any]]:
    params = {
        "apiKey": api_key,
        "regions": "us",
        "markets": "spreads,totals",
        "bookmakers": "draftkings,fanduel,betmgm",
        "oddsFormat": "american",
        "dateFormat": "iso",
    }
    timeout = httpx.Timeout(15.0, read=15.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(
            "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds",
            params=params,
        )
        response.raise_for_status()
        return response.json()


def _within_current_week(commence: str, reference: datetime) -> bool:
    try:
        game_time = datetime.fromisoformat(commence.replace("Z", "+00:00"))
    except ValueError:
        return False
    return reference - timedelta(hours=2) <= game_time <= reference + timedelta(days=7)


def _extract_game_summary(event: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    commence_time = event.get("commence_time")
    commence_dt: Optional[datetime] = None
    if commence_time:
        try:
            commence_dt = datetime.fromisoformat(commence_time.replace("Z", "+00:00"))
        except ValueError:
            commence_dt = None

    bookmakers_summary: List[Dict[str, Any]] = []
    totals_points: List[Dict[str, Any]] = []
    spreads_points: List[Dict[str, Any]] = []

    for bookmaker in event.get("bookmakers", []):
        markets = bookmaker.get("markets", [])
        totals_market = next((m for m in markets if m.get("key") == "totals"), None)
        spreads_market = next((m for m in markets if m.get("key") == "spreads"), None)

        book_entry: Dict[str, Any] = {
            "key": bookmaker.get("key"),
            "title": bookmaker.get("title"),
            "last_update": bookmaker.get("last_update"),
            "totals": [],
            "spreads": [],
        }

        if totals_market:
            for outcome in totals_market.get("outcomes", []):
                point = outcome.get("point")
                if point is None:
                    continue
                total_record = {
                    "name": outcome.get("name"),
                    "point": point,
                    "price": outcome.get("price"),
                }
                book_entry["totals"].append(total_record)
            if book_entry["totals"]:
                totals_points.append(
                    {
                        "book": bookmaker.get("title") or bookmaker.get("key"),
                        "point": book_entry["totals"][0]["point"],
                        "price": book_entry["totals"][0].get("price"),
                    }
                )

        if spreads_market:
            for outcome in spreads_market.get("outcomes", []):
                if outcome.get("point") is None:
                    continue
                spread_record = {
                    "name": outcome.get("name"),
                    "point": outcome.get("point"),
                    "price": outcome.get("price"),
                }
                book_entry["spreads"].append(spread_record)
            home_team = event.get("home_team")
            if home_team:
                home_outcome = next(
                    (o for o in book_entry["spreads"] if o.get("name") == home_team),
                    None,
                )
                if home_outcome:
                    spreads_points.append(
                        {
                            "book": bookmaker.get("title") or bookmaker.get("key"),
                            "point": home_outcome.get("point"),
                            "price": home_outcome.get("price"),
                        }
                    )

        bookmakers_summary.append(book_entry)

    totals_movement = 0.0
    avg_total = None
    if totals_points:
        points = [tp["point"] for tp in totals_points]
        totals_movement = max(points) - min(points) if len(points) > 1 else 0.0
        avg_total = sum(points) / len(points)

    on_key_number = False
    key_hits: List[float] = []
    if avg_total is not None:
        for key_number in KEY_NUMBERS:
            if abs(avg_total - key_number) < 0.5:
                on_key_number = True
                key_hits.append(key_number)

    best_books = sorted({tp["book"] for tp in totals_points})[:3] if totals_points else []

    return {
        "id": event.get("id"),
        "home_team": event.get("home_team"),
        "away_team": event.get("away_team"),
        "commence_time": commence_dt.isoformat() if commence_dt else commence_time,
        "bookmakers": bookmakers_summary,
        "totals_points": totals_points,
        "spreads_points": spreads_points,
        "totals_movement": totals_movement,
        "average_total": avg_total,
        "on_key_number": on_key_number,
        "key_numbers": key_hits,
        "best_books": best_books,
        "last_updated": now.isoformat(),
    }


def _detect_edges(game: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    movement = game.get("totals_movement") or 0.0
    totals_points = game.get("totals_points") or []
    if movement < 2.0 or len(totals_points) < 2:
        return None

    sorted_points = sorted(totals_points, key=lambda item: item["point"])
    low = sorted_points[0]
    high = sorted_points[-1]
    recommendation = {
        "game": f"{game.get('away_team')} @ {game.get('home_team')}",
        "movement": round(movement, 1),
        "lowest_total": low,
        "highest_total": high,
        "on_key_number": bool(game.get("on_key_number")),
        "key_numbers": game.get("key_numbers") or [],
        "strategy": "Totals movement",
    }

    if movement >= 3.0:
        recommendation["action"] = f"Buy Under {high['point']:.1f} at {high['book']}"
        recommendation["confidence"] = "High"
    else:
        recommendation["action"] = f"Monitor or grab Over {low['point']:.1f} at {low['book']}"
        recommendation["confidence"] = "Medium"
    return recommendation


def _build_cache_payload(games: List[Dict[str, Any]], fetched_at: datetime) -> Dict[str, Any]:
    expires_at = fetched_at + CACHE_TTL
    return {
        "fetched_at": fetched_at.isoformat(),
        "expires_at": expires_at.isoformat(),
        "games": games,
    }


def _write_cache(payload: Dict[str, Any]) -> None:
    CACHE_FILE.write_text(json.dumps(payload, indent=2))


def _should_use_cache() -> bool:
    if not CACHE_FILE.exists():
        return False
    try:
        cache = json.loads(CACHE_FILE.read_text())
    except json.JSONDecodeError:
        return False
    expires_at = cache.get("expires_at")
    if not expires_at:
        return False
    try:
        expiry_dt = datetime.fromisoformat(expires_at)
    except ValueError:
        return False
    return datetime.now(timezone.utc) < expiry_dt


def _format_game_block(index: int, game: Dict[str, Any]) -> str:
    lines: List[str] = []
    matchup = f"{game.get('away_team')} @ {game.get('home_team')}"
    lines.append(f"{index}. {matchup}")

    totals_points = game.get("totals_points") or []
    if totals_points:
        avg_total = game.get("average_total")
        movement = game.get("totals_movement", 0.0)
        lines.append(f"   Total: {avg_total:.1f} (Movement: {movement:.1f} points)")
        if game.get("on_key_number"):
            key_numbers = ", ".join(str(k) for k in game.get("key_numbers", []))
            lines.append(f"   ⚠️ Key Number: {key_numbers}")

    spreads_points = game.get("spreads_points") or []
    if spreads_points:
        avg_spread = sum(item["point"] for item in spreads_points) / len(spreads_points)
        lines.append(
            f"   Spread: {game.get('home_team')} {avg_spread:+.1f}"
        )

    if totals_points:
        best_books = ", ".join(game.get("best_books", []))
        if best_books:
            lines.append(f"   Best Books: {best_books}")

    return "\n".join(lines)


def _format_edges(edges: List[Dict[str, Any]]) -> str:
    if not edges:
        return "No edges meeting criteria found currently.\nContinue monitoring for line movement."

    blocks: List[str] = []
    for edge in sorted(edges, key=lambda item: item.get("movement", 0), reverse=True):
        block = [f"{edge['game']}:", f"   - Strategy: {edge['strategy']} ({edge['movement']:.1f} points)"]
        block.append(f"   - Action: {edge['action']}")
        block.append(f"   - Confidence: {edge['confidence']}")
        block.append(
            "   - Key Number: "
            + ("YES - Protect it" if edge.get("on_key_number") else "No")
        )
        block.append("   - Lines available:")
        low = edge.get("lowest_total")
        high = edge.get("highest_total")
        if low:
            block.append(
                f"      {low['book']}: {low['point']:.1f} ({low.get('price', 0):+d})"
            )
        if high and high != low:
            block.append(
                f"      {high['book']}: {high['point']:.1f} ({high.get('price', 0):+d})"
            )
        blocks.append("\n".join(block))
    return "\n\n".join(blocks)


def format_output(result: Dict[str, Any]) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    lines = [f"🏈 NFL DATA PULL - {timestamp}", "=" * 37]

    lines.append("\n📊 API STATUS:")
    total_tokens = result.get("total_tokens", 0)
    for status in result.get("token_status", []):
        remaining = status.get("remaining")
        remaining_text = f"{remaining}" if remaining is not None else "?"
        lines.append(
            f"- Key {status['index']} (…{status['key_suffix']}): {remaining_text} tokens remaining"
        )
    lines.append(f"\nTotal Available: {total_tokens} tokens")

    games = result.get("games", [])
    lines.append("\n🏈 THIS WEEK'S GAMES:")
    lines.append("-" * 37)
    if not games:
        lines.append("No qualifying NFL games within the next week.")
    else:
        for idx, game in enumerate(games, start=1):
            lines.append("\n" + _format_game_block(idx, game))

    lines.append("\n" + "=" * 37)
    lines.append("🎯 EDGES DETECTED:")
    lines.append("-" * 37)
    lines.append(_format_edges(result.get("edges", [])))

    lines.append("\n" + "=" * 37)
    lines.append("✅ Data cached for 30 minutes")
    next_refresh = datetime.now(timezone.utc) + timedelta(minutes=30)
    lines.append(
        f"📝 Next refresh recommended: {next_refresh.strftime('%A %I:%M %p %Z')}"
    )

    return "\n".join(lines)


def _save_output_json(result: Dict[str, Any]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = CACHE_DIR / f"{OUTPUT_PREFIX}{timestamp}.json"
    output_path.write_text(json.dumps(result, indent=2))
    return output_path


async def run(force_refresh: bool = False) -> Dict[str, Any]:
    _load_env()
    manager = OddsAPIManager()
    keys = manager.settings.all_odds_keys
    if not keys:
        raise RuntimeError("No Odds API keys configured")

    token_statuses = await check_token_status(keys)
    total_tokens = sum(status.remaining for status in token_statuses if status.remaining is not None)

    use_cache = _should_use_cache() and not force_refresh
    games_payload: List[Dict[str, Any]]

    if use_cache:
        cache = json.loads(CACHE_FILE.read_text())
        games_payload = cache.get("games", [])
    else:
        best_key = _choose_best_key(keys, token_statuses)
        raw_events = await fetch_odds_with_key(best_key)
        now = datetime.now(timezone.utc)

        games_payload = []
        for event in raw_events:
            if not _within_current_week(event.get("commence_time", ""), now):
                continue
            summary = _extract_game_summary(event)
            if summary.get("totals_points"):
                games_payload.append(summary)
        cache_payload = _build_cache_payload(games_payload, now)
        _write_cache(cache_payload)

    edges: List[Dict[str, Any]] = []
    for game in games_payload:
        edge = _detect_edges(game)
        if edge:
            edges.append(edge)

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "token_status": [status.to_dict() for status in token_statuses],
        "total_tokens": total_tokens,
        "games": games_payload,
        "edges": edges,
    }
    return result


if __name__ == "__main__":
    payload = asyncio.run(run(force_refresh=True))
    formatted = format_output(payload)
    print(formatted)
    saved_path = _save_output_json(payload)
    print(f"\nOutput saved to {saved_path}")
