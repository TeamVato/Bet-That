"""Custom commands for Bet-That project."""
from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import Dict, List, Type

from .base import BaseCommand


def discover_commands() -> Dict[str, Type[BaseCommand]]:
    """Discover all available custom commands."""
    commands: Dict[str, Type[BaseCommand]] = {}

    # Get the commands package directory
    commands_dir = Path(__file__).parent

    # Import all modules in the commands package
    for module_info in pkgutil.iter_modules([str(commands_dir)]):
        if module_info.name.startswith('_') or module_info.name == 'base':
            continue

        try:
            module = importlib.import_module(f'commands.{module_info.name}')

            # Look for command classes
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, BaseCommand) and
                    attr != BaseCommand):
                    command_name = getattr(attr, 'name', attr_name.lower())
                    commands[command_name] = attr
        except ImportError as e:
            print(f"Warning: Could not import command module {module_info.name}: {e}")

    return commands


def list_commands() -> List[str]:
    """List all available custom commands."""
    commands = discover_commands()
    return sorted(commands.keys())


def get_command(name: str) -> Type[BaseCommand] | None:
    """Get a specific command by name."""
    commands = discover_commands()
    return commands.get(name)


def run_command(name: str, *args, **kwargs) -> int:
    """Run a custom command by name."""
    command_class = get_command(name)
    if not command_class:
        print(f"Error: Unknown command '{name}'")
        print(f"Available commands: {', '.join(list_commands())}")
        return 1

    command = command_class()
    try:
        return command.run(*args, **kwargs)
    except Exception as e:
        print(f"Error running command '{name}': {e}")
        return 1


__all__ = ['BaseCommand', 'discover_commands', 'list_commands', 'get_command', 'run_command']