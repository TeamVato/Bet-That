from datetime import datetime
import json
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class BetPlacement(BaseModel):
    game_id: str
    market: str  # 'spread', 'total', 'moneyline'
    selection: str  # 'HOME', 'AWAY', 'OVER', 'UNDER'
    line: float
    odds: int  # American odds
    stake: float
    bookmaker: str


class Bet(BaseModel):
    id: str
    user_id: str
    game_id: str
    game_name: str
    market: str
    selection: str
    line: float
    odds: int
    stake: float
    potential_win: float
    potential_payout: float
    bookmaker: str
    status: str  # 'pending', 'won', 'lost', 'pushed'
    placed_at: str
    settled_at: Optional[str] = None


# In-memory storage for demo (would use database in production)
BETS_FILE = Path("/Users/vato/work/Bet-That/backend/data/user_bets.json")


def load_bets() -> List[dict]:
    if BETS_FILE.exists():
        with open(BETS_FILE) as f:
            return json.load(f)
    return []


def save_bets(bets: List[dict]):
    BETS_FILE.parent.mkdir(exist_ok=True)
    with open(BETS_FILE, "w") as f:
        json.dump(bets, f, indent=2)


@router.post("/place")
async def place_bet(bet_data: BetPlacement):
    """Place a new bet"""
    # Load game data to get team names
    games_file = Path("/Users/vato/work/Bet-That/backend/data/nfl_pull_20250927_074502.json")
    if not games_file.exists():
        raise HTTPException(status_code=500, detail="Games data unavailable")

    with open(games_file) as f:
        games_payload = json.load(f)

    games = games_payload.get("games", []) if isinstance(games_payload, dict) else games_payload

    # Ensure iterable of dicts
    if not isinstance(games, list):
        raise HTTPException(status_code=500, detail="Games data malformed")

    game = next((g for g in games if isinstance(g, dict) and g.get("id") == bet_data.game_id), None)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    game_name = f"{game.get('away_team')} @ {game.get('home_team')}"

    # Calculate potential win
    if bet_data.odds > 0:
        potential_win = bet_data.stake * bet_data.odds / 100
    else:
        potential_win = bet_data.stake * 100 / abs(bet_data.odds)

    bet = {
        "id": str(uuid.uuid4()),
        "user_id": "demo_user",
        "game_id": bet_data.game_id,
        "game_name": game_name,
        "market": bet_data.market,
        "selection": bet_data.selection,
        "line": bet_data.line,
        "odds": bet_data.odds,
        "stake": bet_data.stake,
        "potential_win": round(potential_win, 2),
        "potential_payout": round(bet_data.stake + potential_win, 2),
        "bookmaker": bet_data.bookmaker,
        "status": "pending",
        "placed_at": datetime.now().isoformat(),
        "settled_at": None,
    }

    bets = load_bets()
    bets.append(bet)
    save_bets(bets)

    return {
        "success": True,
        "bet": bet,
        "message": f"Bet placed: {bet_data.selection} {bet_data.line} for ${bet_data.stake}",
    }


@router.get("/my-bets")
async def get_my_bets():
    """Get user's betting history"""
    bets = load_bets()

    total_stake = sum(b["stake"] for b in bets)
    pending_bets = [b for b in bets if b["status"] == "pending"]
    won_bets = [b for b in bets if b["status"] == "won"]
    lost_bets = [b for b in bets if b["status"] == "lost"]

    total_won = sum(b["potential_win"] for b in won_bets)
    total_lost = sum(b["stake"] for b in lost_bets)
    net_profit = total_won - total_lost

    return {
        "bets": bets,
        "summary": {
            "total_bets": len(bets),
            "pending": len(pending_bets),
            "won": len(won_bets),
            "lost": len(lost_bets),
            "total_stake": round(total_stake, 2),
            "net_profit": round(net_profit, 2),
            "roi": round((net_profit / total_stake * 100) if total_stake > 0 else 0, 2),
        },
    }


@router.delete("/{bet_id}")
async def cancel_bet(bet_id: str):
    """Cancel a pending bet"""
    bets = load_bets()
    bet = next((b for b in bets if b["id"] == bet_id), None)

    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")

    if bet["status"] != "pending":
        raise HTTPException(status_code=400, detail="Can only cancel pending bets")

    updated = [b for b in bets if b["id"] != bet_id]
    save_bets(updated)

    return {"success": True, "message": "Bet cancelled"}
