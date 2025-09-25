"""Enhance empty state UX for Bet-That Streamlit application."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from .base import BaseCommand


class EnhanceEmptyStateCommand(BaseCommand):
    """Add enhanced empty-state callout and reset filters functionality."""

    name = "enhance-empty-state"
    description = "Add empty-state callout with reset filters button and unit tests"

    def run(self, *args, **kwargs) -> int:
        """Run the empty state UX enhancement."""
        self.log("Enhancing empty state UX")

        # Enhance the render_empty_explainer function
        success = self._enhance_empty_explainer()
        if not success:
            return 1

        # Add helper functions for filter reset
        success = self._add_filter_reset_helpers()
        if not success:
            return 1

        # Create and run unit tests
        success = self._create_unit_tests()
        if not success:
            return 1

        test_result = self.run_pytest("tests/test_empty_state_enhancements.py", verbose=True)
        if test_result != 0:
            self.error("Empty state enhancement tests failed")
            return test_result

        self.success("Empty state UX enhancement completed successfully")
        return 0

    def _enhance_empty_explainer(self) -> bool:
        """Enhance the render_empty_explainer function with reset functionality."""
        try:
            streamlit_app_path = Path("app/streamlit_app.py")

            # Read the current file
            with open(streamlit_app_path, "r") as f:
                content = f.read()

            # Find the render_empty_explainer function
            old_function = '''def render_empty_explainer(
    edges_source: pd.DataFrame,
    filters_obj: EmptyFilters,
    database_path: Path,
    force_open: bool,
    ctx_key: str,
) -> None:
    """Render the explainer, optionally forced open via the context key."""

    tips = explain_empty(edges_source, filters_obj, database_path)
    with st.expander("ℹ️ Why is this empty (or limited)?", expanded=force_open):
        for line in tips.get("tips", []):
            st.write(line)
        for extra in tips.get("extras", []):
            st.caption(extra)
    if force_open:
        st.session_state[ctx_key] = False'''

            new_function = '''def render_empty_explainer(
    edges_source: pd.DataFrame,
    filters_obj: EmptyFilters,
    database_path: Path,
    force_open: bool,
    ctx_key: str,
) -> None:
    """Render the explainer, optionally forced open via the context key."""

    tips = explain_empty(edges_source, filters_obj, database_path)
    with st.expander("ℹ️ Why is this empty (or limited)?", expanded=force_open):
        # Enhanced explanation with more context
        if not tips.get("tips"):
            st.warning("🚫 **No data available**")
            st.write("**Likely causes:**")
            st.write("- No matching markets for current filters")
            st.write("- Stale odds data (refresh needed)")
            st.write("- Missing projections for this timeframe")
        else:
            st.info("📊 **Filter Analysis Results**")
            for line in tips.get("tips", []):
                st.write(line)

        # Add reset filters button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Reset All Filters", key=f"reset_filters_{ctx_key}", use_container_width=True):
                reset_all_filters()
                st.experimental_rerun()

        # Coverage information
        for extra in tips.get("extras", []):
            st.caption(extra)
    if force_open:
        st.session_state[ctx_key] = False'''

            if old_function in content:
                content = content.replace(old_function, new_function)

                # Write the updated content
                with open(streamlit_app_path, "w") as f:
                    f.write(content)

                self.log("✓ Enhanced render_empty_explainer function")
                return True
            else:
                self.error("Could not find render_empty_explainer function to update")
                return False

        except Exception as e:
            self.error(f"Error enhancing empty explainer: {e}")
            return False

    def _add_filter_reset_helpers(self) -> bool:
        """Add helper functions for resetting filters."""
        try:
            streamlit_app_path = Path("app/streamlit_app.py")

            # Read the current file
            with open(streamlit_app_path, "r") as f:
                content = f.read()

            # Add the reset_all_filters function after the render_empty_explainer function
            reset_function = '''

def reset_all_filters() -> None:
    """Reset all filter controls to their default values."""
    # Season filter - reset to all available seasons
    if "season_filter" in st.session_state:
        # Don't modify directly, let the UI component handle defaults
        del st.session_state["season_filter"]

    # Odds range - reset to default range
    if "odds_range" in st.session_state:
        st.session_state["odds_range"] = (-250, 250)

    # EV minimum - reset to 0
    if "min_ev" in st.session_state:
        st.session_state["min_ev"] = 0.0

    # Checkboxes - reset to default states
    checkbox_defaults = {
        "hide_stale": True,
        "show_best_only": True,
        "only_generous": False,
        "pos_stingy": False,
        "pos_generous": False
    }

    for key, default_value in checkbox_defaults.items():
        if key in st.session_state:
            st.session_state[key] = default_value

    # Position and book filters
    filter_keys_to_clear = [
        key for key in st.session_state.keys()
        if key.startswith(("position_", "book_", "preset_"))
    ]
    for key in filter_keys_to_clear:
        del st.session_state[key]


def format_empty_explanation(tips: list[str], max_items: int = 3) -> str:
    """Format empty state explanation into a concise, helpful string."""
    if not tips:
        return "No specific issues identified. Try widening filters or refreshing data."

    # Take the most relevant tips
    ranked_tips = tips[:max_items]

    # Create user-friendly explanations
    explanations = []
    for tip in ranked_tips:
        if "Season filter" in tip:
            explanations.append("Selected seasons may not have data")
        elif "Odds range" in tip:
            explanations.append("Odds range too narrow")
        elif "EV threshold" in tip:
            explanations.append("Expected value threshold too high")
        elif "stale" in tip.lower():
            explanations.append("Most lines are stale (need fresh data)")
        elif "best" in tip.lower():
            explanations.append("No best-priced edges available")
        else:
            explanations.append(tip.split("—")[0].strip() if "—" in tip else tip)

    if len(explanations) == 1:
        return f"Issue: {explanations[0]}"
    else:
        return "Issues: " + "; ".join(explanations)'''

            # Find a good place to insert the function (after render_empty_explainer)
            insertion_point = content.find("def export_picks(")
            if insertion_point == -1:
                # Fallback: insert before main function
                insertion_point = content.find("def main():")
                if insertion_point == -1:
                    self.error("Could not find suitable insertion point for helper functions")
                    return False

            # Insert the new functions
            content = content[:insertion_point] + reset_function + "\n\n" + content[insertion_point:]

            # Write the updated content
            with open(streamlit_app_path, "w") as f:
                f.write(content)

            self.log("✓ Added filter reset helper functions")
            return True

        except Exception as e:
            self.error(f"Error adding filter reset helpers: {e}")
            return False

    def _create_unit_tests(self) -> bool:
        """Create unit tests for the empty state enhancements."""
        try:
            test_content = '''"""Unit tests for empty state UX enhancements."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.streamlit_app import format_empty_explanation


def test_format_empty_explanation_no_tips():
    """Test formatting when no tips are provided."""
    result = format_empty_explanation([])
    expected = "No specific issues identified. Try widening filters or refreshing data."
    assert result == expected


def test_format_empty_explanation_single_tip():
    """Test formatting with a single tip."""
    tips = ["Season filter removed 15 rows — Fix: Add more seasons"]
    result = format_empty_explanation(tips)
    assert result == "Issue: Selected seasons may not have data"


def test_format_empty_explanation_multiple_tips():
    """Test formatting with multiple tips."""
    tips = [
        "Season filter removed 15 rows — Fix: Add more seasons",
        "Odds range filter removed 8 rows — Fix: Widen range",
        "EV threshold removed 5 rows — Fix: Lower threshold"
    ]
    result = format_empty_explanation(tips)
    expected = "Issues: Selected seasons may not have data; Odds range too narrow; Expected value threshold too high"
    assert result == expected


def test_format_empty_explanation_max_items_limit():
    """Test that formatting respects max_items parameter."""
    tips = [
        "Season filter removed 15 rows",
        "Odds range filter removed 8 rows",
        "EV threshold removed 5 rows",
        "Hide stale removed 3 rows",
        "Best priced only removed 2 rows"
    ]
    result = format_empty_explanation(tips, max_items=2)
    # Should only include first 2 items
    assert "Selected seasons may not have data" in result
    assert "Odds range too narrow" in result
    assert "Expected value threshold too high" not in result


def test_format_empty_explanation_stale_detection():
    """Test detection of stale-related issues."""
    tips = ["Hide stale removed 25 rows — Fix: Uncheck hide stale"]
    result = format_empty_explanation(tips)
    assert result == "Issue: Most lines are stale (need fresh data)"


def test_format_empty_explanation_best_priced_detection():
    """Test detection of best-priced issues."""
    tips = ["Best-priced only removed 10 rows — Fix: Uncheck best-priced filter"]
    result = format_empty_explanation(tips)
    assert result == "Issue: No best-priced edges available"


def test_format_empty_explanation_generic_tip():
    """Test handling of generic tips without specific keywords."""
    tips = ["Missing opponent_def_code removed 5 rows — Fix: Run defense ratings"]
    result = format_empty_explanation(tips)
    assert result == "Issue: Missing opponent_def_code removed 5 rows"


if __name__ == "__main__":
    # Run basic test to verify functionality
    test_format_empty_explanation_no_tips()
    test_format_empty_explanation_single_tip()
    test_format_empty_explanation_multiple_tips()
    print("✓ All empty state enhancement tests passed")
'''

            test_file_path = Path("tests/test_empty_state_enhancements.py")
            with open(test_file_path, "w") as f:
                f.write(test_content)

            self.log("✓ Created unit tests for empty state enhancements")
            return True

        except Exception as e:
            self.error(f"Error creating unit tests: {e}")
            return False