#!/usr/bin/env python3
"""Monitor placed bets and edge performance"""

import json
import time
from datetime import datetime
from pathlib import Path


def monitor_bets():
    """Real-time monitoring of bet status"""
    bets_file = Path("/Users/vato/work/Bet-That/backend/data/user_bets.json")

    while True:
        if bets_file.exists():
            with open(bets_file) as handle:
                bets = json.load(handle)
        else:
            bets = []

        print("\033[2J\033[H", end="")  # Clear screen
        print("🎰 BET-THAT LIVE MONITORING")
        print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        pending = [bet for bet in bets if bet.get('status') == 'pending']
        if pending:
            print(f"\n📊 ACTIVE BETS ({len(pending)})")
            for bet in pending:
                print(f"  • {bet['game_name']}")
                print(
                    f"    {bet['selection']} {bet['line']} | ${bet['stake']} → ${bet['potential_payout']:.2f}"
                )
        else:
            print("\n📭 No active bets")

        total_stake = sum(bet['stake'] for bet in bets)
        total_potential = sum(bet['potential_payout'] for bet in pending)

        print("\n💰 EXPOSURE")
        print(f"  Total at risk: ${total_stake:.2f}")
        print(f"  Potential return: ${total_potential:.2f}")
        print(f"  Potential profit: ${(total_potential - total_stake):.2f}")

        print("\nPress Ctrl+C to exit")
        time.sleep(5)


if __name__ == "__main__":
    try:
        monitor_bets()
    except KeyboardInterrupt:
        print("\nMonitoring stopped")
