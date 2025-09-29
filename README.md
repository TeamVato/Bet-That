# Bet-That Integration Guide

## Quick Start

- Install dependencies:
  - Backend: `python -m venv .venv && source .venv/bin/activate && pip install -r backend/requirements.txt`
  - Frontend: `cd frontend && pnpm install`
- Launch services: `docker-compose up --build`
- Frontend lives at http://localhost:5173, backend API at http://localhost:8000.
- Copy `.env.example` into `.env` for both `frontend/` and `backend/` before running locally.

## API Endpoints

- `GET /api/edges/current` → Returns the latest edge snapshot including beta gating metadata.
- `GET /api/edges/validate/{edge_id}` → Provides manual validation status for a specific edge.
- `GET /health` → Docker health probe checking API reachability and Redis connectivity.
- All endpoints require no authentication in beta; secure the network perimeter before production rollout.

## Frontend Components

- `Dashboard.tsx` renders the analyst-facing view of edge data, including filters, auto-refresh, and beta warnings.
- Components live in `frontend/src/components/`; tests reside in `frontend/src/components/__tests__/`.
- Configure the frontend via `frontend/.env` (`VITE_API_BASE_URL`, beta banner overrides, and demo user IDs).
- Run `pnpm dev` for local development or `pnpm build && pnpm preview` for a production preview.

## Docker Setup

- Compose file defines `frontend` and `backend` services; both expose health checks for production orchestrators.
- Environment variables flow from `.env` files—mount or inject them in your hosting platform.
- To rebuild after code changes: `docker-compose build --no-cache && docker-compose up`.
- Verify containers are healthy with `docker-compose ps`; both should report `healthy` state.

## Environment Variables

- Frontend (`frontend/.env`): `VITE_API_BASE_URL`, `VITE_BETA_VIEW_ONLY`, `VITE_BETA_DISCLAIMER`, `VITE_BETA_WARNING_TITLE`, `VITE_DEMO_USER_ID`.
- Backend (`backend/.env`): `ENVIRONMENT`, `REDIS_URL`, `CACHE_TTL_SECONDS`, `DAILY_REQUEST_LIMIT`, `EDGES_SNAPSHOT_PATH`, `ODDS_API_KEYS`.
- Validation: the React app throws during bootstrap if required variables (e.g., `VITE_API_BASE_URL`) are missing in production mode.
- Update deployment secrets whenever `.env.example` changes to keep containers in sync with local development.

## Troubleshooting Common Issues

- **Dashboard loads without data**: confirm backend container can reach `backend/data/edges_current.json`.
- **CORS errors in browser**: set `VITE_API_BASE_URL` to the deployed backend origin and restart `pnpm dev`.
- **Redis connection warnings**: the API logs a warning when Redis is unavailable but continues running; provide `REDIS_URL` in production.
- **Tests fail to locate mock data**: run `python -m pytest backend/tests/` and `pnpm test` from their respective directories.
- **Docker health checks failing**: inspect container logs (`docker-compose logs <service>`) to review request/response details.

# Test pre-commit hooks
