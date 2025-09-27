"""
Bet-That FastAPI Application
Sprint 1 MVP: User layer extension for existing betting analytics system
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from .endpoints import health, odds, bets, digest, edges
from .utils.logging_middleware import LoggingMiddleware
from .utils.ratelimit import RateLimiter
from .errors import add_error_handlers
from .database import init_database
from .settings import settings

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Bet-That API v0.2")
    init_database()
    logger.info(f"Database initialized at {settings.db_path}")
    yield
    logger.info("Shutting down Bet-That API")

app = FastAPI(
    title="Bet-That Analytics API",
    description=f"""
    NFL betting analytics platform providing odds data, bet tracking, and CLV analysis.
    
    **Compliance Notice:** {settings.compliance_disclaimer}
    
    ## Features
    - Real-time NFL odds from The Odds API
    - User bet tracking and CLV calculation  
    - Weekly digest subscription management
    - Production observability and rate limiting
    
    ## Authentication
    Sprint 1: Include `X-User-Id` header with external user ID from Supabase auth.
    """,
    version="0.2.0",
    lifespan=lifespan
)

app.openapi_extra = {
    "x-compliance": {
        "disclaimer": settings.compliance_disclaimer,
        "age_restriction": "21+",
        "purpose": "entertainment_only"
    }
}

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(LoggingMiddleware)
add_error_handlers(app)

rate_limiter = RateLimiter(requests_per_minute=settings.rate_limit_requests, window_seconds=settings.rate_limit_window)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or (request.client.host if request.client else "unknown")
    route_key = f"{request.method}:{request.url.path}"
    
    if not rate_limiter.is_allowed(client_ip, route_key):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded", "detail": "Too many requests"},
            headers={
                "Retry-After": str(settings.rate_limit_window),
                "X-RateLimit-Limit": str(settings.rate_limit_requests),
                "X-Compliance-Disclaimer": settings.compliance_disclaimer,
                "X-User-IP-Logged": "true"
            }
        )
    
    response = await call_next(request)
    response.headers["X-Compliance-Disclaimer"] = settings.compliance_disclaimer
    response.headers["X-User-IP-Logged"] = "true"
    return response

app.include_router(health.router, tags=["Health"])
app.include_router(odds.router, prefix="/odds", tags=["Odds"])
app.include_router(bets.router, prefix="/me", tags=["User Bets"])
app.include_router(digest.router, prefix="/digest", tags=["Digest"])
app.include_router(edges.router)

@app.get("/")
async def root():
    return {
        "message": "Bet-That Analytics API v0.2",
        "description": "NFL betting analytics platform",
        "docs": "/docs",
        "health": "/health",
        "compliance": settings.compliance_disclaimer
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
