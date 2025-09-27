# Browser Testing Plan - Customer Bet Placement

## Test Scenario: Place All 4 Edge Bets

### Prerequisites
- Frontend running at http://localhost:5173
- Backend running at http://127.0.0.1:8000
- 4 edges detected and displayed

### Step-by-Step Test

1. **Open Dashboard**
   - Navigate to http://localhost:5173
   - Verify "Bet-That Edge Tracker" header displays
   - Check token status shows (2121 remaining)

2. **View Available Edges**
   - Dashboard should show 4 edge cards
   - Each card displays:
     * Game names (e.g., "Vikings @ Steelers")
     * Recommendation (e.g., "UNDER 41.5")
     * Bookmaker (DraftKings/FanDuel/BetMGM)
     * Edge percentage (5.5%)
     * Confidence level (85%)

3. **Place First Bet**
   - Click "Place Bet" on Vikings @ Steelers edge
   - Bet slip modal opens
   - Verify details:
     * Game: Vikings @ Steelers
     * Selection: UNDER 41.5
     * Default stake: $50
     * Potential payout: $95.45
   - Click "Confirm Bet"
   - Success message appears
   - Modal closes

4. **Navigate to My Bets**
   - Click "My Bets" in navigation
   - Verify bet appears with:
     * Game ID
     * Market type (Total)
     * Selection (UNDER)
     * Stake ($50)
     * Odds (-110)
     * Status (Pending)

5. **Place Remaining Bets**
   - Return to Dashboard
   - Place bets on:
     * Panthers @ Patriots UNDER 43.5
     * Packers @ Cowboys UNDER 47.5
     * Bengals @ Broncos UNDER 44.5

6. **Verify Bet Slip**
   - Go to My Bets
   - Should show 4 pending bets
   - Total staked: $200
   - Total potential payout: $381.80

## Expected Results
- All bets placed successfully
- Bets persisted in backend
- UI updates immediately
- No console errors
