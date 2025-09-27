import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

GAMES_FILE = Path("/Users/vato/work/Bet-That/backend/data/nfl_pull_20250927_074502.json")


def load_games():
    if not GAMES_FILE.exists():
        return {}
    with open(GAMES_FILE) as handle:
        data = json.load(handle)
    return data.get("games", []) if isinstance(data, dict) else data


@router.get("/edges")
async def get_edges():
    """Get current betting edges from analysis"""
    edge_file = Path("/Users/vato/work/Bet-That/backend/data/current_edges.json")
    
    # Run edge detection if file doesn't exist
    if not edge_file.exists():
        script_path = Path("/Users/vato/work/Bet-That/backend/scripts/find_best_edges_now.py")
        subprocess.run([sys.executable, str(script_path)], capture_output=True)
    
    # Load edges
    with open(edge_file) as f:
        edges_data = json.load(f)

    games = load_games()
    game_lookup = {}
    if isinstance(games, list):
        for game in games:
            if isinstance(game, dict):
                matchup = f"{game.get('away_team')} @ {game.get('home_team')}"
                game_lookup[matchup] = game.get('id')
    
    # Format for frontend
    formatted_edges = []
    edge_id = 1
    
    for bet in edges_data.get("STRONG_BETS", []):
        matchup = bet["game"]
        game_id = game_lookup.get(matchup)
        formatted_edges.append({
            "id": f"edge_{game_id}" if game_id else f"edge_{edge_id}",
            "game_id": game_id,
            "game": matchup,
            "type": "total",
            "line": float(bet["bet"].split()[-1]),
            "edge_percentage": bet["edge_pct"],
            "confidence": 85,
            "recommendation": bet["bet"],
            "bookmaker": bet["book"],
            "timestamp": datetime.now().isoformat()
        })
        edge_id += 1
    
    return {"edges": formatted_edges, "count": len(formatted_edges)}

@router.get("/token-status")
async def get_token_status():
    return {
        "total": 3000,
        "used": 879,
        "remaining": 2121,
        "daily_limit": 20,
        "keys_active": 6
    }
