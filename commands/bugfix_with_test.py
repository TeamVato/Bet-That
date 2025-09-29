"""Interactive bugfix workflow with test-first approach for Bet-That."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from .base import BaseCommand


class BugfixWithTestCommand(BaseCommand):
    """Interactive bugfix workflow: identify minimal change, apply fix, add focused test."""

    name = "bugfix-with-test"
    description = "Make a small, test-backed fix with minimal surface area"

    def run(self, *args, **kwargs) -> int:
        """Run the interactive bugfix workflow."""
        self.log("Starting test-backed bugfix workflow")

        # Step 1: Get stack trace from user
        stack_trace = self._get_stack_trace_input()
        if not stack_trace:
            self.error("No stack trace provided - cannot proceed")
            return 1

        # Step 2: Parse and analyze the stack trace
        analysis = self._analyze_stack_trace(stack_trace)
        if not analysis:
            self.error("Could not parse stack trace")
            return 1

        # Step 3: Identify minimal code region to change
        target_location = self._identify_target_location(analysis)
        if not target_location:
            self.error("Could not identify target location for fix")
            return 1

        print(f"\n🎯 **Target Location Identified:**")
        print(f"File: {target_location['file']}")
        print(f"Function: {target_location['function']}")
        print(f"Line: {target_location['line']}")
        print(f"Issue: {target_location['issue']}")

        # Step 4: Propose fix (interactive)
        fix_approach = self._propose_fix_approach(target_location, stack_trace)
        if not fix_approach:
            self.error("No fix approach determined")
            return 1

        # Step 5: Create/extend focused unit test
        test_result = self._create_focused_test(target_location, fix_approach)
        if test_result != 0:
            self.error("Failed to create focused unit test")
            return test_result

        # Step 6: Apply the minimal fix
        fix_result = self._apply_minimal_fix(target_location, fix_approach)
        if fix_result != 0:
            self.error("Failed to apply fix")
            return fix_result

        # Step 7: Run tests to verify fix
        self.log("Verifying fix with tests")
        test_result = self.run_pytest(f"tests/test_{target_location['test_name']}.py", verbose=True)

        if test_result != 0:
            self.error("Tests failed after applying fix")
            return test_result

        # Step 8: Provide command summary
        self._provide_command_summary(target_location)

        self.success("Bugfix workflow completed successfully")
        return 0

    def _get_stack_trace_input(self) -> str:
        """Get stack trace from user input or clipboard."""
        print("\n📋 **Stack Trace Input**")
        print("Please paste your stack trace (press Enter twice when done):")

        lines = []
        empty_count = 0

        try:
            while empty_count < 2:
                line = input()
                if line.strip() == "":
                    empty_count += 1
                else:
                    empty_count = 0
                    lines.append(line)
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return ""
        except EOFError:
            pass

        stack_trace = "\n".join(lines).strip()

        if not stack_trace:
            # Try to provide an example for testing
            print("No stack trace provided. Using example for testing...")
            stack_trace = """Traceback (most recent call last):
  File "app/streamlit_app.py", line 1234, in render_table
    df["confidence"] = df.apply(compute_confidence, axis=1)
  File "pandas/core/frame.py", line 9876, in apply
    return op.apply().__finalize__(result, method="apply")
AttributeError: 'NoneType' object has no attribute 'get'
"""

        return stack_trace

    def _analyze_stack_trace(self, stack_trace: str) -> dict | None:
        """Parse the stack trace to extract key information."""
        try:
            lines = stack_trace.strip().split("\n")

            # Find the main error line
            error_line = None
            for line in reversed(lines):
                if any(
                    error_type in line
                    for error_type in [
                        "Error:",
                        "Exception:",
                        "AttributeError",
                        "KeyError",
                        "ValueError",
                    ]
                ):
                    error_line = line.strip()
                    break

            # Find file/line references
            file_references = []
            for line in lines:
                if 'File "' in line and ", line " in line:
                    match = re.search(r'File "([^"]+)", line (\d+), in (\w+)', line)
                    if match:
                        file_references.append(
                            {
                                "file": match.group(1),
                                "line": int(match.group(2)),
                                "function": match.group(3),
                            }
                        )

            # Filter to project files (not library code)
            project_files = [
                ref
                for ref in file_references
                if not any(
                    lib in ref["file"]
                    for lib in ["pandas/", "numpy/", "streamlit/", "site-packages/"]
                )
            ]

            if not project_files:
                return None

            return {
                "error_message": error_line,
                "project_files": project_files,
                "all_files": file_references,
            }

        except Exception as e:
            self.error(f"Error parsing stack trace: {e}")
            return None

    def _identify_target_location(self, analysis: dict) -> dict | None:
        """Identify the minimal code region that needs to be changed."""
        if not analysis["project_files"]:
            return None

        # Take the first project file in the stack (usually where the issue originates)
        target_ref = analysis["project_files"][0]

        # Determine the issue type from error message
        error_msg = analysis["error_message"] or ""

        issue_type = "unknown"
        if "'NoneType' object has no attribute" in error_msg:
            issue_type = "null_attribute_access"
        elif "KeyError" in error_msg:
            issue_type = "missing_key"
        elif "AttributeError" in error_msg:
            issue_type = "attribute_error"
        elif "ValueError" in error_msg:
            issue_type = "value_error"

        # Generate test name based on file
        file_path = Path(target_ref["file"])
        if file_path.name == "streamlit_app.py":
            test_name = "streamlit_bugfix"
        else:
            test_name = f"{file_path.stem}_bugfix"

        return {
            "file": target_ref["file"],
            "line": target_ref["line"],
            "function": target_ref["function"],
            "issue": issue_type,
            "error_message": error_msg,
            "test_name": test_name,
        }

    def _propose_fix_approach(self, target_location: dict, stack_trace: str) -> dict | None:
        """Propose a minimal fix approach based on the issue type."""
        issue_type = target_location["issue"]

        approaches = {
            "null_attribute_access": {
                "strategy": "add_null_check",
                "description": "Add null/None safety check before attribute access",
                "pattern": "Add if obj and obj.get(...) or getattr(obj, attr, default)",
            },
            "missing_key": {
                "strategy": "safe_key_access",
                "description": "Use .get() method with default value instead of direct key access",
                "pattern": "Replace dict[key] with dict.get(key, default)",
            },
            "attribute_error": {
                "strategy": "add_hasattr_check",
                "description": "Add hasattr() check before accessing attribute",
                "pattern": "Add if hasattr(obj, attr) check",
            },
            "value_error": {
                "strategy": "add_validation",
                "description": "Add input validation with try/except or type checking",
                "pattern": "Add validation before problematic operation",
            },
        }

        approach = approaches.get(
            issue_type,
            {
                "strategy": "defensive_coding",
                "description": "Add defensive coding practices",
                "pattern": "Add appropriate error handling",
            },
        )

        print(f"\n🔧 **Proposed Fix Approach:**")
        print(f"Strategy: {approach['strategy']}")
        print(f"Description: {approach['description']}")
        print(f"Pattern: {approach['pattern']}")

        return approach

    def _create_focused_test(self, target_location: dict, fix_approach: dict) -> int:
        """Create or extend a focused unit test for the bugfix."""
        try:
            test_file_path = Path(f"tests/test_{target_location['test_name']}.py")

            # Create test content based on the issue type
            test_content = self._generate_test_content(target_location, fix_approach)

            if test_file_path.exists():
                # Extend existing test file
                with open(test_file_path, "a") as f:
                    f.write(f"\n\n{test_content}")
                self.log(f"✓ Extended existing test file: {test_file_path}")
            else:
                # Create new test file
                full_content = f'''"""Focused unit tests for bugfix: {target_location['issue']}."""
import sys
from pathlib import Path
import pytest
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

{test_content}
'''
                with open(test_file_path, "w") as f:
                    f.write(full_content)
                self.log(f"✓ Created new test file: {test_file_path}")

            return 0

        except Exception as e:
            self.error(f"Error creating focused test: {e}")
            return 1

    def _generate_test_content(self, target_location: dict, fix_approach: dict) -> str:
        """Generate appropriate test content based on the issue type."""
        function_name = target_location["function"]
        issue_type = target_location["issue"]

        if issue_type == "null_attribute_access":
            return f'''
def test_{function_name}_handles_none_input():
    """Test that {function_name} handles None input gracefully."""
    # This test should pass after the fix
    from app.streamlit_app import {function_name}

    # Test with None input
    result = {function_name}(None)
    assert result is not None, "Function should handle None input gracefully"

    # Test with empty/missing attributes
    test_obj = {{}})  # Empty dict or object
    result = {function_name}(test_obj)
    assert result is not None, "Function should handle objects without required attributes"
'''

        elif issue_type == "missing_key":
            return f'''
def test_{function_name}_handles_missing_keys():
    """Test that {function_name} handles missing dictionary keys."""
    from app.streamlit_app import {function_name}

    # Test with empty dict
    empty_dict = {{}}
    result = {function_name}(empty_dict)
    assert result is not None, "Function should handle missing keys gracefully"

    # Test with partial data
    partial_dict = {{"some_key": "some_value"}}
    result = {function_name}(partial_dict)
    assert result is not None, "Function should handle partial data gracefully"
'''

        else:
            return f'''
def test_{function_name}_error_handling():
    """Test that {function_name} handles edge cases properly."""
    from app.streamlit_app import {function_name}

    # Test with edge case input that previously caused the error
    try:
        result = {function_name}(None)  # or appropriate edge case
        assert result is not None, "Function should handle edge cases"
    except Exception as e:
        pytest.fail(f"Function should handle edge cases without throwing: {{e}}")
'''

    def _apply_minimal_fix(self, target_location: dict, fix_approach: dict) -> int:
        """Apply the minimal fix to the identified location."""
        try:
            file_path = Path(target_location["file"])

            if not file_path.exists():
                self.error(f"Target file does not exist: {file_path}")
                return 1

            # Read the current file
            with open(file_path, "r") as f:
                lines = f.readlines()

            # Find the target line (line numbers are 1-indexed)
            target_line_idx = target_location["line"] - 1

            if target_line_idx >= len(lines):
                self.error(f"Target line {target_location['line']} beyond file length")
                return 1

            original_line = lines[target_line_idx].rstrip()

            # Apply fix based on strategy
            fixed_line = self._apply_fix_strategy(original_line, fix_approach, target_location)

            if fixed_line == original_line:
                self.error("No changes made - fix strategy didn't modify the line")
                return 1

            # Replace the line
            lines[target_line_idx] = fixed_line + "\n"

            # Write back to file
            with open(file_path, "w") as f:
                f.writelines(lines)

            self.log(f"✓ Applied fix to {file_path}:{target_location['line']}")
            self.log(f"  Before: {original_line}")
            self.log(f"  After:  {fixed_line}")

            return 0

        except Exception as e:
            self.error(f"Error applying fix: {e}")
            return 1

    def _apply_fix_strategy(self, line: str, fix_approach: dict, target_location: dict) -> str:
        """Apply the specific fix strategy to the line."""
        strategy = fix_approach["strategy"]
        stripped = line.strip()
        indent = line[: len(line) - len(stripped)]

        if strategy == "add_null_check":
            # Look for attribute access patterns like obj.get() or obj.attribute
            if ".get(" in stripped:
                # Already using .get(), add None check
                if "if " not in stripped:
                    return f"{indent}if {stripped.split('.')[0]} and {stripped.split('.')[0]}.get("
                return line
            elif re.search(r"(\w+)\.(\w+)", stripped):
                # Direct attribute access, make it safe
                match = re.search(r"(\w+)\.(\w+)", stripped)
                if match:
                    obj, attr = match.groups()
                    safe_access = f"getattr({obj}, '{attr}', None)"
                    return indent + stripped.replace(f"{obj}.{attr}", safe_access)

        elif strategy == "safe_key_access":
            # Replace dict[key] with dict.get(key, default)
            if "[" in stripped and "]" in stripped:
                # Simple replacement for common dict access patterns
                if '"' in stripped or "'" in stripped:
                    # Handle string keys
                    pattern = r'(\w+)\[(["\'][^"\']+["\'])\]'
                    match = re.search(pattern, stripped)
                    if match:
                        dict_name, key = match.groups()
                        return indent + stripped.replace(
                            f"{dict_name}[{key}]", f"{dict_name}.get({key}, None)"
                        )

        elif strategy == "add_hasattr_check":
            # Add hasattr check for attribute access
            if re.search(r"(\w+)\.(\w+)", stripped):
                match = re.search(r"(\w+)\.(\w+)", stripped)
                if match:
                    obj, attr = match.groups()
                    return f"{indent}if hasattr({obj}, '{attr}') and {obj}.{attr}:"

        # Fallback: add basic None check
        if "=" in stripped and not stripped.startswith("if"):
            var_part = stripped.split("=")[0].strip()
            return f"{indent}if {var_part} is not None:\n{line}"

        return line

    def _provide_command_summary(self, target_location: dict) -> None:
        """Provide summary of commands to run for verification."""
        test_file = f"tests/test_{target_location['test_name']}.py"

        print(f"\n✅ **Bugfix Applied Successfully**")
        print(f"\n📋 **Commands to run:**")
        print(f"1. Test the fix:")
        print(f"   pytest -q {test_file}")
        print(f"\n2. Run edges computation (if relevant):")
        print(f"   make edges")
        print(f"\n3. Launch the app to verify:")
        print(f"   ./BetThat")
        print(f"\n🎯 **What was fixed:**")
        print(f"- File: {target_location['file']}:{target_location['line']}")
        print(f"- Function: {target_location['function']}")
        print(f"- Issue: {target_location['issue']}")
        print(f"- Test: {test_file}")

    def print_help(self) -> None:
        """Print detailed help for the bugfix command."""
        super().print_help()
        print("\nUsage:")
        print("  This command provides an interactive workflow for fixing bugs:")
        print("  1. Paste the stack trace when prompted")
        print("  2. Review the identified target location")
        print("  3. Confirm the proposed fix approach")
        print("  4. The command will create/extend tests and apply the minimal fix")
        print("  5. Run the provided verification commands")
        print("\nConstraints:")
        print("  - Focuses on minimal changes with small surface area")
        print("  - Uses defensive coding practices")
        print("  - Streamlit width API only (no heavy dependencies)")
        print("  - Includes focused unit tests for the fix")
