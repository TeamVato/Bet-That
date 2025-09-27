from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis
from app.api.endpoints import odds
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Redis connection on startup
    app.state.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
    try:
        await app.state.redis.ping()
        print("✅ Redis connected successfully")
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}")
        app.state.redis = None
    yield
    if app.state.redis:
        await app.state.redis.close()

app = FastAPI(title="Bet-That API", version="1.0.0", lifespan=lifespan)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(odds.router, prefix="/api/v1/odds", tags=["odds"])

@app.get("/health")
async def health_check():
    redis_status = "connected" if hasattr(app.state, 'redis') and app.state.redis else "disconnected"
    return {"status": "healthy", "service": "bet-that-api", "redis": redis_status}
