# Custom Commands for Bet-That

This document describes the custom commands implemented for the Bet-That project.

## Overview

The custom commands system provides specialized workflows for common development and debugging tasks. Commands are implemented using a discoverable plugin architecture with integration into both the Makefile and the BetThat shell script.

## Available Commands

### 1. check-ingestion-contract

**Purpose**: Verify odds ingestion contract end-to-end

**What it does**:
- Verifies book name normalization (e.g., "draftkings" → "DraftKings")
- Ensures position inference from market types (e.g., "player_pass_yds" → "QB")
- Guarantees season information is present in all rows
- Runs comprehensive integrity tests with a dedicated CSV fixture

**Usage**:
```bash
make check-ingestion-contract
# OR
./BetThat check-ingestion-contract
# OR
python run_command.py check-ingestion-contract
```

**Acceptance criteria**:
- `pytest -q tests/test_importer_integrity.py` passes
- `make import-odds && make edges` succeeds
- Database contract compliance verified

### 2. enhance-empty-state

**Purpose**: Add enhanced empty-state callout with reset filters functionality

**What it does**:
- Enhances the Streamlit UI empty state messaging
- Adds contextual explanations for likely causes of empty results
- Provides a "Reset All Filters" button for quick recovery
- Includes unit tests for explanation string formatting

**Usage**:
```bash
make enhance-empty-state
# OR
./BetThat enhance-empty-state
# OR
python run_command.py enhance-empty-state
```

**Features**:
- Improved UX with clear explanations of filter effects
- One-click filter reset functionality
- Unit tested helper functions

### 3. bugfix-with-test

**Purpose**: Interactive bugfix workflow with test-first approach

**What it does**:
- Accepts stack traces and analyzes them to identify target locations
- Proposes minimal fix approaches with small surface area
- Creates or extends focused unit tests
- Applies defensive coding fixes
- Provides verification commands

**Usage**:
```bash
make bugfix-with-test
# OR
./BetThat bugfix-with-test
# OR
python run_command.py bugfix-with-test
```

**Workflow**:
1. Paste stack trace when prompted
2. Review identified target location (file + function)
3. Confirm proposed fix approach
4. Command creates focused test and applies minimal fix
5. Run provided verification commands

**Constraints**:
- No new heavy dependencies
- Streamlit width API only
- Focuses on defensive coding practices
- Minimal surface area changes

## Integration

### Makefile Integration

Custom commands are integrated with the existing Makefile system:

```bash
make custom-commands          # List all available commands
make check-ingestion-contract # Run specific command
make enhance-empty-state      # Run specific command
make bugfix-with-test         # Run specific command
```

### BetThat Script Integration

Commands can be run through the main BetThat script:

```bash
./BetThat command                    # List available custom commands
./BetThat check-ingestion-contract   # Run specific command
./BetThat enhance-empty-state        # Run specific command
./BetThat bugfix-with-test          # Run specific command
```

### Direct Execution

Commands can be run directly via the command runner:

```bash
python run_command.py list                     # List commands
python run_command.py check-ingestion-contract # Run specific command
```

## Architecture

### Directory Structure

```
commands/
├── __init__.py                    # Command discovery and registry
├── base.py                        # BaseCommand class with common utilities
├── check_ingestion_contract.py    # Custom command #1
├── enhance_empty_state.py         # Custom command #2
└── bugfix_with_test.py           # Custom command #3

run_command.py                     # Command line entry point
```

### Command Discovery

Commands are automatically discovered by:
1. Scanning the `commands/` directory
2. Importing modules that aren't `base.py` or start with `_`
3. Finding classes that inherit from `BaseCommand`
4. Registering them by their `name` attribute

### Base Command Class

All commands inherit from `BaseCommand` which provides:
- `run()` abstract method for command execution
- `log()`, `error()`, `success()` for logging
- `run_pytest()` for test execution
- `run_make_target()` for Makefile integration
- `print_help()` for documentation

## Testing

Each command includes focused unit tests:
- `test_ingestion_contract_end_to_end` in `tests/test_importer_integrity.py`
- `test_empty_state_enhancements.py` (created by enhance-empty-state command)
- Test files created dynamically by bugfix-with-test command

Run all tests:
```bash
python -m pytest tests/ -v
```

## Adding New Commands

To add a new custom command:

1. Create a new file in `commands/` (e.g., `commands/my_new_command.py`)
2. Inherit from `BaseCommand` and implement the `run()` method
3. Set `name` and `description` class attributes
4. Add any required unit tests
5. Command will be automatically discovered and available

Example:
```python
from .base import BaseCommand

class MyNewCommand(BaseCommand):
    name = "my-new-command"
    description = "Description of what this command does"

    def run(self, *args, **kwargs) -> int:
        self.log("Running my new command")
        # Implementation here
        return 0  # Success
```