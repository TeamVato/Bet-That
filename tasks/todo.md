# 2025 Edges Fix Plan - Bet-That Join-Key Population

## Problem Summary
2025 season edges are not being generated due to missing join keys (season, week, opponent_def_code) when merging with defense ratings. The error "Warning: unable to merge defense ratings" results in 0 edges for 2025 season.

## Root Cause Analysis

**Missing Join Keys:**
- `jobs/compute_edges.py:296-305` - Defense ratings merge requires season, week, opponent_def_code
- `engine/edge_engine.py:100-107` - Edge computation may not populate week/opponent_def_code for all rows
- Schedule lookup exists in `adapters/nflverse_provider.py` but isn't being used for missing data

**UI/UX Issues:**
- `app/streamlit_app.py:857-859` - Season filter defaults to all seasons, should allow empty selection
- Missing debug controls for join diagnostics
- Potential Streamlit key collisions in dynamic UI elements

## Implementation Plan

### Phase 1: Edge Join Key Population

**1.1 Enhance week inference in `engine/edge_engine.py`**
- Lines 100-103: Add schedule-based week lookup fallback when `week_proj` and `week_props` are null
- Import `build_event_lookup` from `adapters.nflverse_provider`
- Use event_id parsing to get game_id, then lookup week from schedule

**1.2 Strengthen opponent_def_code in `engine/edge_engine.py`**
- Lines 104-107: Add fallback logic when opponent defense code is missing
- Use event_id parsing to infer opponent team when direct lookup fails
- Ensure consistent team code normalization via `engine.team_map.normalize_team_code`

**1.3 Add schedule lookup integration in `jobs/compute_edges.py`**
- Lines 241-243: Pass schedule_lookup to EdgeEngine constructor
- Modify EdgeEngine to use schedule data for missing week/opponent inference
- Ensure 2023-2025 seasons are covered in schedule fetch

### Phase 2: Enhanced Join Diagnostics

**2.1 Improve join logging in `jobs/compute_edges.py`**
- Lines 286-317: Enhance existing diagnostics with join key analysis
- Add logging for missing season/week/opponent_def_code before merge attempt
- Log join key coverage statistics (% of rows with complete keys)

**2.2 Add debug controls**
- Environment variable `DEBUG_EDGE_JOINS=1` for verbose logging
- Cap diagnostic output to prevent spam (already exists at line 316)
- Add join success rate metrics to console output

### Phase 3: UI Season Filter Fix

**3.1 Fix empty season selection in `app/streamlit_app.py`**
- Lines 857-859: Remove default=all_seasons, allow empty selection
- When no seasons selected, show "Select seasons to view edges" message
- Ensure edge loading only occurs with valid season selection

**3.2 Add debug panel controls**
- Toggle for join diagnostics display
- Show edge join key coverage in debug panel
- Display merge success rates per season

### Phase 4: Testing & Verification

**4.1 Unit tests for edge key population**
- Test `edge_engine.py` week inference with missing data
- Test opponent_def_code fallback logic
- Mock schedule lookup scenarios

**4.2 Integration test for 2025 edges**
- End-to-end test ensuring 2025 edges generate successfully
- Verify defense ratings merge success with populated keys
- Test edge count > 0 for 2025 season

## File Change Anchors

### Core Logic Changes
- `engine/edge_engine.py:100-107` - Add schedule-based week/opponent fallbacks
- `engine/edge_engine.py:__init__` - Accept schedule_lookup parameter
- `jobs/compute_edges.py:241-243` - Pass schedule to EdgeEngine
- `jobs/compute_edges.py:286-317` - Enhanced join diagnostics

### UI Changes
- `app/streamlit_app.py:857-859` - Remove default season selection
- `app/streamlit_app.py` - Add debug controls for join analysis

### Testing
- `tests/test_edge_engine.py` - New tests for join key population
- `tests/test_compute_edges_integration.py` - End-to-end 2025 test

## Success Criteria

✅ **2025 Edges Generated**: `./BetThat` shows edges count > 0 for 2025 season
✅ **Join Success**: Defense ratings merge succeeds with <5% unmatched rows
✅ **UI Behavior**: Empty season selection shows appropriate message
✅ **Diagnostics**: Clear join key coverage and success rate logging
✅ **Tests Pass**: All unit and integration tests verify the fix

## Risk Mitigation

- **Schedule Dependency**: Fallback to current_season() if schedule lookup fails
- **Performance**: Cache schedule lookup results, limit diagnostic logging
- **Backwards Compatibility**: Preserve existing behavior for 2023-2024 seasons
- **Testing**: Isolated unit tests prevent regression in edge computation

---

**Estimated Effort**: 2-3 hours for core fix + diagnostics + testing
**Files Modified**: 4-5 files (edge_engine.py, compute_edges.py, streamlit_app.py, tests)
**Approach**: Surgical changes with comprehensive logging and fallback safety