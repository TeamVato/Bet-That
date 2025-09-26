# tests/test_freshness_controls.py
"""Unit tests for the freshness controls functionality."""

import pandas as pd
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch


class TestFreshnessControls:
    """Test suite for freshness controls in Streamlit app."""

    def test_compute_minutes_since_update_current_time(self):
        """Test computation for current timestamp."""
        current_time = datetime.now(timezone.utc)

        def compute_minutes_since_update(updated_at):
            if pd.isna(updated_at) or updated_at is None:
                return 9999
            try:
                if isinstance(updated_at, str):
                    update_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                else:
                    update_time = pd.to_datetime(updated_at, utc=True)
                delta = current_time - update_time
                return delta.total_seconds() / 60.0
            except Exception:
                return 9999

        # Test current timestamp
        current_iso = current_time.isoformat()
        result = compute_minutes_since_update(current_iso)
        assert result < 1.0  # Should be very recent

    def test_compute_minutes_since_update_past_timestamps(self):
        """Test computation for timestamps in the past."""
        current_time = datetime.now(timezone.utc)

        def compute_minutes_since_update(updated_at):
            if pd.isna(updated_at) or updated_at is None:
                return 9999
            try:
                if isinstance(updated_at, str):
                    update_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                else:
                    update_time = pd.to_datetime(updated_at, utc=True)
                delta = current_time - update_time
                return delta.total_seconds() / 60.0
            except Exception:
                return 9999

        # Test 30 minutes ago
        past_time = current_time - timedelta(minutes=30)
        past_iso = past_time.isoformat()
        result = compute_minutes_since_update(past_iso)
        assert 29.0 <= result <= 31.0

        # Test 2 hours ago
        past_time = current_time - timedelta(hours=2)
        past_iso = past_time.isoformat()
        result = compute_minutes_since_update(past_iso)
        assert 119.0 <= result <= 121.0

    def test_compute_minutes_since_update_edge_cases(self):
        """Test computation edge cases."""
        current_time = datetime.now(timezone.utc)

        def compute_minutes_since_update(updated_at):
            if pd.isna(updated_at) or updated_at is None:
                return 9999
            try:
                if isinstance(updated_at, str):
                    update_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                else:
                    update_time = pd.to_datetime(updated_at, utc=True)
                delta = current_time - update_time
                return delta.total_seconds() / 60.0
            except Exception:
                return 9999

        # Test None
        assert compute_minutes_since_update(None) == 9999

        # Test NaN
        assert compute_minutes_since_update(pd.NA) == 9999

        # Test invalid string
        assert compute_minutes_since_update("invalid-date") == 9999

        # Test Z suffix handling
        z_time = "2024-09-25T10:00:00Z"
        result = compute_minutes_since_update(z_time)
        assert result > 0  # Should be a positive number of minutes

    def test_custom_stale_threshold_filtering(self):
        """Test that custom stale threshold correctly filters data."""
        # Create test data with various ages
        current_time = datetime.now(timezone.utc)
        df = pd.DataFrame({
            'updated_at': [
                current_time.isoformat(),  # Fresh
                (current_time - timedelta(minutes=45)).isoformat(),  # Medium
                (current_time - timedelta(minutes=150)).isoformat(),  # Stale
                None  # Missing
            ],
            'player': ['A', 'B', 'C', 'D']
        })

        # Compute minutes since update
        def compute_minutes_since_update(updated_at):
            if pd.isna(updated_at) or updated_at is None:
                return 9999
            try:
                if isinstance(updated_at, str):
                    update_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                else:
                    update_time = pd.to_datetime(updated_at, utc=True)
                delta = current_time - update_time
                return delta.total_seconds() / 60.0
            except Exception:
                return 9999

        df['minutes_since_update'] = df['updated_at'].apply(compute_minutes_since_update)

        # Test 60-minute threshold
        threshold_60 = 60
        df['is_stale_60'] = (df['minutes_since_update'] > threshold_60).astype(int)
        fresh_60 = df[df['is_stale_60'] == 0]
        assert len(fresh_60) == 2  # A and B should be fresh

        # Test 180-minute threshold (C at 150 min should be fresh)
        threshold_180 = 180
        df['is_stale_180'] = (df['minutes_since_update'] > threshold_180).astype(int)
        fresh_180 = df[df['is_stale_180'] == 0]
        assert len(fresh_180) == 3  # A, B, and C should be fresh

    def test_nullable_integer_handling(self):
        """Test that nullable integers are handled properly in freshness logic."""
        df = pd.DataFrame({
            'minutes_since_update': [30.5, 90.0, 180.5, 9999.0],
            'original_is_stale': [0, pd.NA, 1, 0]
        })

        # Custom threshold logic
        custom_threshold = 120
        df['is_stale_custom'] = (df['minutes_since_update'] > custom_threshold).astype(int)

        expected = [0, 0, 1, 1]  # 30, 90 are fresh; 180, 9999 are stale
        assert df['is_stale_custom'].tolist() == expected

    def test_freshness_column_display_logic(self):
        """Test that freshness columns are added to display when requested."""
        # Simulate the display column logic
        base_display_cols = ["player", "market", "odds", "ev_per_dollar"]
        show_freshness_info = True

        # Mock edges_view with minutes_since_update column
        mock_columns = base_display_cols + ["minutes_since_update"]

        display_cols = base_display_cols.copy()
        if show_freshness_info and "minutes_since_update" in mock_columns:
            display_cols.append("minutes_since_update")

        assert "minutes_since_update" in display_cols

        # Test when show_freshness_info is False
        show_freshness_info = False
        display_cols = base_display_cols.copy()
        if show_freshness_info and "minutes_since_update" in mock_columns:
            display_cols.append("minutes_since_update")

        assert "minutes_since_update" not in display_cols

    def test_different_iso_formats(self):
        """Test handling of different ISO timestamp formats."""
        current_time = datetime.now(timezone.utc)

        def compute_minutes_since_update(updated_at):
            if pd.isna(updated_at) or updated_at is None:
                return 9999
            try:
                if isinstance(updated_at, str):
                    update_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                else:
                    update_time = pd.to_datetime(updated_at, utc=True)
                delta = current_time - update_time
                return delta.total_seconds() / 60.0
            except Exception:
                return 9999

        past_time = current_time - timedelta(minutes=60)

        # Test different formats
        formats = [
            past_time.isoformat(),  # Standard ISO
            past_time.strftime("%Y-%m-%dT%H:%M:%SZ"),  # With Z
            past_time.strftime("%Y-%m-%dT%H:%M:%S+00:00"),  # With timezone
        ]

        for fmt in formats:
            result = compute_minutes_since_update(fmt)
            assert 59.0 <= result <= 61.0, f"Failed for format: {fmt}"

    def test_pandas_datetime_handling(self):
        """Test that pandas datetime objects are handled correctly."""
        current_time = datetime.now(timezone.utc)
        past_time = current_time - timedelta(minutes=30)

        def compute_minutes_since_update(updated_at):
            if pd.isna(updated_at) or updated_at is None:
                return 9999
            try:
                if isinstance(updated_at, str):
                    update_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                else:
                    update_time = pd.to_datetime(updated_at, utc=True)
                delta = current_time - update_time
                return delta.total_seconds() / 60.0
            except Exception:
                return 9999

        # Test pandas Timestamp
        pandas_timestamp = pd.to_datetime(past_time, utc=True)
        result = compute_minutes_since_update(pandas_timestamp)
        assert 29.0 <= result <= 31.0

    def test_extreme_age_values(self):
        """Test handling of very old timestamps."""
        current_time = datetime.now(timezone.utc)

        def compute_minutes_since_update(updated_at):
            if pd.isna(updated_at) or updated_at is None:
                return 9999
            try:
                if isinstance(updated_at, str):
                    update_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                else:
                    update_time = pd.to_datetime(updated_at, utc=True)
                delta = current_time - update_time
                return delta.total_seconds() / 60.0
            except Exception:
                return 9999

        # Test very old timestamp
        very_old = "2020-01-01T00:00:00Z"
        result = compute_minutes_since_update(very_old)
        assert result > 1000000  # Should be a very large number of minutes

        # Test future timestamp (edge case)
        future_time = current_time + timedelta(hours=1)
        future_iso = future_time.isoformat()
        result = compute_minutes_since_update(future_iso)
        assert result < 0  # Should be negative