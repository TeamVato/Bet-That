# Bet-That — Sprint 1 Frontend (React + Vite + TS)

Integrates with the FastAPI backend at `http://localhost:8000`.

## Quickstart

```bash
pnpm i
cp .env.example .env
pnpm dev
# open http://localhost:5173
```

### Environment

- `VITE_API_BASE_URL` — default `http://localhost:8000`
- `VITE_DEMO_USER_ID` — used for authenticated routes (`/me/*`)

### Pages

- **Dashboard** — `GET /odds/best?market=` with filter + refresh
- **My Bets** — list + create (client validation mirrors backend)
- **Digest** — `POST /digest/subscribe`
- **Account** — shows `VITE_DEMO_USER_ID` & compliance disclaimer

### Tests

```bash
pnpm test
```

### Docker

```bash
docker build -t bet-that-web .
docker run --rm -p 5173:80 \
  -e VITE_API_BASE_URL=http://host.docker.internal:8000 \
  -e VITE_DEMO_USER_ID=user_123 bet-that-web
```

## Compliance Disclaimer

> This platform provides sports analytics for entertainment purposes only. Not available to residents where prohibited. Users must be 21+. Gamble responsibly.
