"""Base command class for custom Bet-That commands."""
from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

# Add the project root to Python path
sys.path.append(str(Path(__file__).resolve().parents[1]))


class BaseCommand(ABC):
    """Base class for custom commands."""

    name: str = ""
    description: str = ""

    @abstractmethod
    def run(self, *args, **kwargs) -> int:
        """
        Run the command.

        Returns:
            int: Exit code (0 for success, non-zero for failure)
        """
        pass

    def print_help(self) -> None:
        """Print help information for this command."""
        print(f"Command: {self.name}")
        print(f"Description: {self.description}")

    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message with timestamp."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def error(self, message: str) -> None:
        """Log an error message."""
        self.log(message, "ERROR")

    def success(self, message: str) -> None:
        """Log a success message."""
        self.log(message, "SUCCESS")

    def run_pytest(self, test_path: str, verbose: bool = False) -> int:
        """
        Run pytest on a specific test file or directory.

        Args:
            test_path: Path to test file or directory
            verbose: Whether to run in verbose mode

        Returns:
            int: Exit code from pytest
        """
        import subprocess

        cmd = [sys.executable, "-m", "pytest"]
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        cmd.append(test_path)

        self.log(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
        return result.returncode

    def run_make_target(self, target: str) -> int:
        """
        Run a make target.

        Args:
            target: Make target to run

        Returns:
            int: Exit code from make
        """
        import subprocess

        cmd = ["make", target]
        self.log(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
        return result.returncode