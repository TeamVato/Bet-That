# Bet-That Beta Readiness Report

## System Health
- Backend API: **RED** — `http://127.0.0.1:8000/health` unreachable (connection refused)
- Frontend UI: **GREEN** — `http://localhost:5173` responds 200 OK
- Redis Cache: **RED** — `redis-cli` not available; Redis status unknown
- CORS Configuration: **RED** — `backend/app/main.py` missing `CORSMiddleware`

## Edge Detection Accuracy
- Cached games analysed: 16 (generated 2025-09-27T07:45:02Z, age ≈0.54h)
- Bookmakers present: DraftKings, BetMGM, FanDuel
- Key-number proximity alerts: 14 games within 0.5 of [40,41,43,44,47,50,51,55]
- Edge findings: 0 high-confidence, 0 medium-confidence, 1 line-shopping opportunity (Ravens @ Chiefs under 48.5 +210¢ improvement)

## Token Burn Rate Projection
- Remaining tokens: 2,121 across 6 keys (879 consumed)
- Daily cap: 120 requests (20 per key) → ~2,400 tokens/day assuming 200 tokens per pull
- Current pace: ~12 pulls (1 cached dataset) → 120 tokens used today
- Projection: Sustain 5–8 refreshes before hitting per-key daily limits; rotate off exhausted key index #2 immediately

## Critical Bugs & Blockers
### P0 — Must Fix
- Backend API offline (no responses on `/health`, `/api/v1/odds/edges`, `/api/v1/odds/token-status`)
- Redis service unavailable (tooling missing or service down)
- Missing CORS middleware preventing cross-origin calls from frontend

### P1 — Should Fix
- Token rotation using exhausted key #2 (0 remaining) still marked `ok`
- Edge detection output lacks medium/high confidence edges → review detection thresholds vs data

### P2 — Nice to Have
- Surface key-number proximity badges on frontend edge cards
- Add freshness indicator per bookmaker to highlight stale feeds

## Recommended Fixes & Priorities
1. **P0:** Add `CORSMiddleware` in `backend/app/main.py` allowing `http://localhost:5173`
2. **P0:** Ensure Redis installed and running (install `redis-cli`, start daemon)
3. **P0:** Restart backend via `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
4. **P1:** Update token rotation to skip exhausted key #2 until reset
5. **P1:** Revisit edge thresholds (>2pt movement currently absent) or verify data ingestion for movement deltas
6. **P2:** Extend frontend UI with key-number and freshness UX improvements

## Next Verification Steps
- Re-run `backend/scripts/comprehensive_edge_analysis.py` after backend restart
- Validate API endpoints via curl (health, edges, token-status)
- Refresh cached odds carefully, ensuring token availability
