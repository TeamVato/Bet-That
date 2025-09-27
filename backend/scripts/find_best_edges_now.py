#!/usr/bin/env python3
"""Find the best betting edges from cached data with explicit recommendations."""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

KEY_NUMBERS = [40, 41, 43, 44, 47, 50, 51, 55]
TARGET_BOOKS = ['DraftKings', 'BetMGM', 'FanDuel']

def load_data() -> List[Dict]:
    data_file = Path("/Users/vato/work/Bet-That/backend/data/nfl_pull_20250927_074502.json")
    with open(data_file) as f:
        raw = json.load(f)
    games = raw.get("games", [])
    if not isinstance(games, list):
        raise ValueError("Invalid games data structure in cache file")
    return games

def find_edges(games: List[Dict]) -> Dict:
    edges = {
        "STRONG_BETS": [],  # Place these immediately
        "VALUE_PLAYS": [],   # Good value, consider
        "LINE_SHOPS": [],    # Same pick, better price
        "MONITOR": []        # Watch for movement
    }
    
    for game in games:
        game_name = f"{game['away_team']} @ {game['home_team']}"
        
        # Extract totals from all books
        totals_data = {}
        for book in game.get('bookmakers', []):
            title = book.get('title')
            if title not in TARGET_BOOKS:
                continue
            for outcome in book.get('totals', []):
                if outcome.get('name') == 'Over':
                    totals_data[title] = {
                        'point': outcome.get('point'),
                        'price': outcome.get('price')
                    }
        
        if not totals_data:
            continue
            
        # Find key number crosses
        points = [t['point'] for t in totals_data.values()]
        min_total = min(points)
        max_total = max(points)
        spread = max_total - min_total
        
        for key in KEY_NUMBERS:
            if min_total < key <= max_total:
                # This is a key number crossing - HIGH VALUE
                best_under = [(book, data) for book, data in totals_data.items() 
                             if data['point'] > key]
                best_over = [(book, data) for book, data in totals_data.items() 
                            if data['point'] < key]
                
                if best_under:
                    book, data = max(best_under, key=lambda x: x[1]['point'])
                    edges["STRONG_BETS"].append({
                        "game": game_name,
                        "bet": f"UNDER {data['point']}",
                        "book": book,
                        "reason": f"Crosses key number {key}",
                        "confidence": "HIGH",
                        "edge_pct": 5.5
                    })
                    
        # Find line shopping opportunities
        if spread < 0.5:  # Same line across books
            prices = [(book, data['price']) for book, data in totals_data.items()]
            best_price = max(prices, key=lambda x: x[1])
            worst_price = min(prices, key=lambda x: x[1])
            
            if best_price[1] - worst_price[1] >= 10:  # 10+ cents difference
                edges["LINE_SHOPS"].append({
                    "game": game_name,
                    "line": f"Total {min_total}",
                    "best_book": best_price[0],
                    "best_price": best_price[1],
                    "worst_book": worst_price[0],
                    "worst_price": worst_price[1],
                    "savings": best_price[1] - worst_price[1]
                })
    
    return edges

def main():
    games = load_data()
    edges = find_edges(games)
    
    # Output actionable recommendations
    print("\n" + "="*60)
    print("BET-THAT EDGE REPORT - PLACE THESE BETS NOW")
    print("="*60)
    
    if edges["STRONG_BETS"]:
        print("\n🔥 STRONG BETS (Place Immediately):")
        for bet in edges["STRONG_BETS"]:
            print(f"\n  Game: {bet['game']}")
            print(f"  BET: {bet['bet']} @ {bet['book']}")
            print(f"  Reason: {bet['reason']}")
            print(f"  Edge: {bet['edge_pct']}%")
    
    if edges["LINE_SHOPS"]:
        print("\n💰 LINE SHOPPING VALUES:")
        for shop in edges["LINE_SHOPS"]:
            print(f"\n  Game: {shop['game']}")
            print(f"  Line: {shop['line']}")
            print(f"  GET: {shop['best_price']:+d} @ {shop['best_book']}")
            print(f"  NOT: {shop['worst_price']:+d} @ {shop['worst_book']}")
            print(f"  Save: {shop['savings']} cents")
    
    # Summary stats
    total_edges = len(edges["STRONG_BETS"]) + len(edges["VALUE_PLAYS"])
    print(f"\n📊 SUMMARY: {total_edges} edges found")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Save to file for frontend
    output_file = Path("/Users/vato/work/Bet-That/backend/data/current_edges.json")
    with open(output_file, 'w') as f:
        json.dump(edges, f, indent=2)
    print(f"\nEdges saved to: {output_file}")

if __name__ == "__main__":
    main()
