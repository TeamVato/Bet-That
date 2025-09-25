#!/usr/bin/env python3
"""Command runner for Bet-That custom commands."""
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent))

from commands import run_command, list_commands


def main():
    """Main entry point for command runner."""
    if len(sys.argv) < 2:
        print("Usage: python run_command.py <command_name> [args...]")
        print(f"Available commands: {', '.join(list_commands())}")
        return 1

    command_name = sys.argv[1]
    args = sys.argv[2:]

    if command_name == "list":
        print("Available custom commands:")
        for cmd in list_commands():
            print(f"  {cmd}")
        return 0

    return run_command(command_name, *args)


if __name__ == "__main__":
    sys.exit(main())