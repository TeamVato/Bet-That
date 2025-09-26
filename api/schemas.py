"""Pydantic models for API request/response validation"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

# User Registration & Authentication Schemas
class UserRegistrationRequest(BaseModel):
    external_id: str = Field(..., description="External user ID from Supabase")
    email: EmailStr = Field(..., description="User email address") 
    name: Optional[str] = Field(None, description="User display name")
    
class UserRegistrationResponse(BaseModel):
    id: int
    external_id: str
    email: str
    name: Optional[str]
    created_at: datetime
    is_active: bool

# Bet Tracking Schemas
class UserBetCreateRequest(BaseModel):
    game_id: str = Field(..., description="Event/Game identifier")
    market: str = Field(..., description="Market type (spread, total, etc.)")
    selection: str = Field(..., description="Bet selection")
    stake: float = Field(..., gt=0, description="Bet stake amount")
    odds: float = Field(..., description="Decimal odds for the bet")
    notes: Optional[str] = Field(None, description="Optional bet notes")
    
class UserBetResponse(BaseModel):
    id: int
    game_id: str
    market: str
    selection: str
    stake: float
    odds: float
    created_at: datetime
    notes: Optional[str]
    clv_cents: Optional[float]
    beat_close: Optional[bool]
    is_settled: bool

class UserBetsListResponse(BaseModel):
    bets: List[UserBetResponse]
    total: int

# Odds Data Schemas
class OddsResponse(BaseModel):
    event_id: str
    market: str
    selection: str
    book: str
    odds_american: int
    odds_decimal: float
    points: Optional[float]
    updated_at: str

class OddsBestLinesResponse(BaseModel):
    lines: List[OddsResponse]
    count: int
    market: str

# Email Digest Subscription Schemas
class DigestSubscriptionRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address for weekly digest")
    frequency: Optional[str] = Field("weekly", description="Subscription frequency")

class DigestSubscriptionResponse(BaseModel):
    id: int
    email: str
    frequency: str
    is_active: bool
    created_at: datetime

# Health Check Schemas
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database: str

class DeepHealthResponse(HealthResponse):
    database_connection: bool
    current_best_lines_count: int
    events_count: int
    users_count: int
    last_odds_update: Optional[str]

# Error Schemas
class ErrorResponse(BaseModel):
    error: str
    detail: str
    status_code: int
    timestamp: datetime
