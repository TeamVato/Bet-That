#!/usr/bin/env python3
"""
Auto-commit script for code quality improvements
Usage: python scripts/auto_commit.py [--dry-run] [--message "Custom message"]
"""

import argparse
import subprocess
import sys
from pathlib import Path


class AutoCommitter:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def run_command(self, cmd, check=True):
        """Run shell command and return result"""
        print("🔧 Running: " + cmd)
        if self.dry_run:
            print("   [DRY RUN - would run this command]")
            return None

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print("❌ Error: " + result.stderr)
            return result
        return result

    def fix_code_style(self):
        """Auto-fix code style issues"""
        print("🎨 Fixing code style...")

        # Fix imports
        self.run_command("source .venv/bin/activate && isort api/ --diff")
        self.run_command("source .venv/bin/activate && isort api/")

        # Fix formatting
        self.run_command("source .venv/bin/activate && black api/ --diff")
        self.run_command("source .venv/bin/activate && black api/")

    def check_git_status(self):
        """Check if there are changes to commit"""
        result = self.run_command("git status --porcelain", check=False)
        return bool(result and result.stdout.strip())

    def commit_and_push(self, message):
        """Commit and push changes"""
        if not self.check_git_status():
            print("✅ No changes to commit")
            return

        print("📦 Committing changes...")
        self.run_command(f"git add api/")
        self.run_command(f'git commit -m "{message}"')

        print("🚀 Pushing to GitHub...")
        self.run_command("git push")

    def run_quality_check(self):
        """Run final quality checks"""
        print("🔍 Running quality checks...")

        # Check linting
        result = self.run_command(
            "source .venv/bin/activate && flake8 api/ --select=F401,F841,F811,F821,E712",
            check=False,
        )
        if result and result.returncode == 0:
            print("✅ No critical linting errors")

        # Check tests
        result = self.run_command(
            "source .venv/bin/activate && python -m pytest backend/tests/ -q", check=False
        )
        if result and result.returncode == 0:
            print("✅ All tests passing")


def main():
    parser = argparse.ArgumentParser(description="Auto-commit code quality improvements")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument(
        "--message", default="polish: auto-fix code style and quality", help="Commit message"
    )
    parser.add_argument("--skip-style", action="store_true", help="Skip style fixes")

    args = parser.parse_args()

    committer = AutoCommitter(dry_run=args.dry_run)

    print("🤖 Auto-Committer Starting...")

    if not args.skip_style:
        committer.fix_code_style()

    committer.run_quality_check()

    if committer.check_git_status():
        committer.commit_and_push(args.message)
        print("🎉 Auto-commit completed!")
    else:
        print("ℹ️  No changes to commit")


if __name__ == "__main__":
    main()
