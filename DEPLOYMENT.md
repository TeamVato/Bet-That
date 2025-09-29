# Deployment Checklist

## Pre-deployment Verification

- Confirm `pnpm build` (frontend) and `uvicorn api.main:app --host 0.0.0.0 --port 8000` (backend) succeed locally.
- Run automated tests: `pnpm test` in `frontend/` and `python -m pytest backend/tests/` in project root.
- Ensure `backend/data/edges_current.json` reflects the latest pipeline output and contains at least one edge.
- Review Docker images via `docker-compose build` to catch missing dependencies before release.

## Environment Setup

- Copy `frontend/.env.example` to `frontend/.env` and `backend/.env.example` to `backend/.env` with production values.
- Set `VITE_API_BASE_URL` to the public API hostname and align `REDIS_URL` with your managed Redis instance.
- Provide Odds API credentials (`ODDS_API_KEYS` or `ODDS_API_KEY_*`) when enabling automated odds ingestion.
- Configure secrets in your orchestrator (e.g., ECS, Fly.io) so the containers inherit the same variables as local `.env` files.

## Health Check Procedures

- After deployment, verify Docker health checks report `healthy` via `docker-compose ps` or your orchestrator dashboard.
- Hit `GET /health` directly to ensure the backend returns `{"status": "healthy"}` and reports Redis as `connected`.
- Load the dashboard at `/` and confirm the beta banner, edge count, and timestamps render without a hard refresh.
- Inspect container logs for warnings (`Redis connection failed`) that may require attention in production.

## Rollback Procedures

- Keep the last known-good Docker image tags available (e.g., `bet-that-frontend:<sha>`, `bet-that-api:<sha>`).
- Revert the orchestrator service to the previous task definition or deployment slot if validation fails.
- Restore `backend/data/edges_current.json` from the last successful artifact if the snapshot becomes corrupted.
- Notify stakeholders and disable betting actions until the dashboard confirms healthy edges again.
