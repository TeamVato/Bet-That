#!/usr/bin/env python3
"""Simulate a customer placing the recommended bets"""

import requests

API_BASE = "http://127.0.0.1:8000/api/v1"


def get_edges():
    """Fetch current edges from API"""
    response = requests.get(f"{API_BASE}/odds/edges", timeout=10)
    response.raise_for_status()
    return response.json()


def place_bet(edge: dict, stake: float = 50):
    """Simulate placing a bet based on an edge"""
    game_id = edge['id'].replace('edge_', '')
    selection = 'UNDER' if 'UNDER' in edge['recommendation'] else 'OVER'

    bet_data = {
        "game_id": game_id,
        "market": "total",
        "selection": selection,
        "line": edge['line'],
        "odds": -110,
        "stake": stake,
        "bookmaker": edge['bookmaker'],
    }

    print(f"\n📝 Placing bet: {edge['game']}")
    print(f"   {selection} {edge['line']} @ {edge['bookmaker']}")
    print(f"   Stake: ${stake}")

    response = requests.post(f"{API_BASE}/bets/place", json=bet_data, timeout=10)

    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ SUCCESS - Bet ID: {result['bet']['id']}")
        print(f"   Potential payout: ${result['bet']['potential_payout']}")
        return result['bet']

    print(f"   ❌ FAILED: {response.text}")
    return None


def view_bet_slip():
    """Display current bet slip"""
    response = requests.get(f"{API_BASE}/bets/my-bets", timeout=10)
    response.raise_for_status()
    data = response.json()

    print("\n" + "=" * 60)
    print("MY BET SLIP")
    print("=" * 60)

    if data['bets']:
        for bet in data['bets']:
            print(f"\n{bet['game_name']}")
            print(f"  {bet['selection']} {bet['line']} @ {bet['bookmaker']}")
            print(f"  Stake: ${bet['stake']} → Potential: ${bet['potential_payout']}")
            print(f"  Status: {bet['status'].upper()}")
            print(f"  Placed: {bet['placed_at']}")
    else:
        print("No bets placed yet.")

    print("\n" + "-" * 60)
    print("SUMMARY:")
    print(f"  Total Bets: {data['summary']['total_bets']}")
    print(f"  Pending: {data['summary']['pending']}")
    print(f"  Total Staked: ${data['summary']['total_stake']}")
    print(f"  Net Profit: ${data['summary']['net_profit']}")
    print(f"  ROI: {data['summary']['roi']}%")


def main():
    print("🎰 BET-THAT CUSTOMER SIMULATION")
    print("=" * 60)

    print("\nFetching available edges...")
    edges_response = get_edges()
    edges = edges_response.get('edges', [])

    print(f"Found {len(edges)} edges available")

    placed_bets = []
    for edge in edges[:4]:
        bet = place_bet(edge, stake=50)
        if bet:
            placed_bets.append(bet)

    view_bet_slip()

    print("\n✅ Customer simulation complete!")
    print(f"   Placed {len(placed_bets)} bets")
    print(f"   Total staked: ${sum(b['stake'] for b in placed_bets)}")
    print(f"   Total potential payout: ${sum(b['potential_payout'] for b in placed_bets):.2f}")


if __name__ == "__main__":
    main()
