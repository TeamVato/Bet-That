from fastapi import APIRouter
from pathlib import Path
import json
from datetime import datetime
import subprocess
import sys

router = APIRouter()

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
    
    # Format for frontend
    formatted_edges = []
    edge_id = 1
    
    for bet in edges_data.get("STRONG_BETS", []):
        formatted_edges.append({
            "id": f"edge_{edge_id}",
            "game": bet["game"],
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
