"""Pydantic models for API request/response validation"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, validator

# Import our SQLAlchemy enums for consistency
from .models import BetStatus, EdgeStatus, TransactionStatus, TransactionType, UserStatus


# Configuration for Pydantic V2
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# User Registration & Authentication Schemas
class UserRegistrationRequest(BaseModel):
    external_id: str = Field(..., description="External user ID from Supabase")
    email: EmailStr = Field(..., description="User email address")
    name: Optional[str] = Field(None, description="User display name")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    timezone: str = Field("UTC", description="User timezone")
    phone: Optional[str] = Field(None, description="Phone number")


class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="Display name")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    timezone: Optional[str] = Field(None, description="Timezone")
    phone: Optional[str] = Field(None, description="Phone number")
    max_bet_size: Optional[Decimal] = Field(None, description="Maximum bet size")
    daily_bet_limit: Optional[Decimal] = Field(None, description="Daily betting limit")
    monthly_bet_limit: Optional[Decimal] = Field(None, description="Monthly betting limit")
    risk_tolerance: Optional[str] = Field(None, description="Risk tolerance level")
    auto_kelly_sizing: Optional[bool] = Field(None, description="Enable auto Kelly sizing")
    max_kelly_fraction: Optional[float] = Field(None, description="Maximum Kelly fraction")
    preferred_sports: Optional[List[str]] = Field(None, description="Preferred sports")
    notification_preferences: Optional[Dict[str, Any]] = Field(
        None, description="Notification settings"
    )
    ui_preferences: Optional[Dict[str, Any]] = Field(None, description="UI preferences")


class UserResponse(BaseSchema):
    id: int
    external_id: str
    email: str
    name: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    timezone: str
    phone: Optional[str]
    status: UserStatus
    is_active: bool
    is_verified: bool
    verification_level: str
    max_bet_size: Decimal
    daily_bet_limit: Decimal
    monthly_bet_limit: Decimal
    risk_tolerance: str
    auto_kelly_sizing: bool
    max_kelly_fraction: float
    preferred_sports: Optional[List[str]]
    notification_preferences: Optional[Dict[str, Any]]
    ui_preferences: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
    last_activity_at: Optional[datetime]


class UserRegistrationResponse(BaseSchema):
    id: int
    external_id: str
    email: str
    name: Optional[str]
    status: UserStatus
    created_at: datetime
    is_active: bool


# Bet Tracking Schemas
class BetCreateRequest(BaseModel):
    event_id: str = Field(..., description="Event identifier")
    edge_id: Optional[int] = Field(None, description="Associated edge ID")
    market_type: str = Field(..., description="Market type (spread, total, moneyline, prop)")
    market_description: str = Field(..., description="Market description")
    selection: str = Field(..., description="Bet selection")
    line: Optional[float] = Field(None, description="Point spread or total line")
    side: Optional[str] = Field(None, description="Side of the bet (over/under, home/away)")
    stake: Decimal = Field(..., gt=0, description="Bet stake amount")
    odds_american: int = Field(..., description="American odds format")
    odds_decimal: float = Field(..., gt=0, description="Decimal odds")
    sportsbook_id: str = Field(..., description="Sportsbook identifier")
    sportsbook_name: str = Field(..., description="Sportsbook name")
    external_bet_id: Optional[str] = Field(None, description="External bet ID from sportsbook")
    notes: Optional[str] = Field(None, description="Optional bet notes")
    tags: Optional[List[str]] = Field(None, description="Bet tags for categorization")

    @validator("odds_american")
    def validate_odds_american(cls, v):
        if v == 0 or abs(v) > 10000:
            raise ValueError("American odds must be non-zero and within reasonable range")
        return v


class BetUpdateRequest(BaseModel):
    status: Optional[BetStatus] = Field(None, description="Bet status")
    result: Optional[str] = Field(None, description="Bet result (win/loss/push/void)")
    actual_return: Optional[Decimal] = Field(None, description="Actual return amount")
    notes: Optional[str] = Field(None, description="Updated notes")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    external_bet_id: Optional[str] = Field(None, description="External bet ID")
    closing_odds_american: Optional[int] = Field(
        None, description="Closing odds in American format"
    )
    closing_odds_decimal: Optional[float] = Field(
        None, description="Closing odds in decimal format"
    )


class BetResponse(BaseSchema):
    id: int
    user_id: int
    event_id: str
    edge_id: Optional[int]
    market_type: str
    market_description: str
    selection: str
    line: Optional[float]
    side: Optional[str]
    stake: Decimal
    odds_american: int
    odds_decimal: float
    potential_return: Decimal
    actual_return: Optional[Decimal]
    net_profit: Optional[Decimal]
    status: BetStatus
    result: Optional[str]
    settled_at: Optional[datetime]
    sportsbook_id: str
    sportsbook_name: str
    external_bet_id: Optional[str]
    edge_percentage: Optional[float]
    kelly_fraction_used: Optional[float]
    expected_value: Optional[Decimal]
    clv_cents: Optional[float]
    beat_close: Optional[bool]
    closing_odds_american: Optional[int]
    closing_odds_decimal: Optional[float]
    notes: Optional[str]
    tags: Optional[List[str]]
    source: str
    placed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class BetListResponse(BaseModel):
    bets: List[BetResponse]
    total: int
    page: int
    per_page: int


# Edge Schemas
class EdgeCreateRequest(BaseModel):
    sport_key: str = Field(..., description="Sport identifier")
    event_id: str = Field(..., description="Event identifier")
    market_type: str = Field(..., description="Market type")
    market_description: str = Field(..., description="Market description")
    player: Optional[str] = Field(None, description="Player name for props")
    position: Optional[str] = Field(None, description="Player position")
    line: Optional[float] = Field(None, description="Line value")
    side: str = Field(..., description="Side of the bet")
    best_odds_american: int = Field(..., description="Best American odds")
    best_odds_decimal: float = Field(..., gt=0, description="Best decimal odds")
    best_sportsbook: str = Field(..., description="Best sportsbook")
    implied_probability: float = Field(..., ge=0, le=1, description="Implied probability")
    fair_probability: float = Field(..., ge=0, le=1, description="Fair probability")
    edge_percentage: float = Field(..., description="Edge percentage")
    expected_value_per_dollar: float = Field(..., description="Expected value per dollar")
    kelly_fraction: float = Field(..., ge=0, le=1, description="Kelly fraction")
    model_probability: float = Field(..., ge=0, le=1, description="Model probability")
    strategy_tag: str = Field(..., description="Strategy identifier")
    expires_at: Optional[datetime] = Field(None, description="Edge expiration time")


class EdgeUpdateRequest(BaseModel):
    status: Optional[EdgeStatus] = Field(None, description="Edge status")
    best_odds_american: Optional[int] = Field(None, description="Updated best odds")
    best_odds_decimal: Optional[float] = Field(None, gt=0, description="Updated decimal odds")
    best_sportsbook: Optional[str] = Field(None, description="Updated best sportsbook")
    is_stale: Optional[bool] = Field(None, description="Mark as stale")
    expires_at: Optional[datetime] = Field(None, description="Updated expiration time")


class EdgeResponse(BaseSchema):
    edge_id: int
    sport_key: str
    event_id: str
    market_type: str
    market_description: str
    player: Optional[str]
    position: Optional[str]
    line: Optional[float]
    side: str
    best_odds_american: int
    best_odds_decimal: float
    best_sportsbook: str
    implied_probability: float
    fair_probability: float
    edge_percentage: float
    expected_value_per_dollar: float
    kelly_fraction: float
    recommended_stake: Optional[Decimal]
    model_probability: float
    model_confidence: Optional[float]
    strategy_tag: str
    discovered_at: datetime
    expires_at: Optional[datetime]
    last_updated: datetime
    status: EdgeStatus
    is_stale: bool
    is_arbitrage: bool
    season: Optional[int]
    week: Optional[int]
    team: Optional[str]
    home_team: Optional[str]
    away_team: Optional[str]
    defense_tier: Optional[str]
    created_at: datetime


class EdgeListResponse(BaseModel):
    edges: List[EdgeResponse]
    total: int
    page: int
    per_page: int


# Transaction Schemas
class TransactionCreateRequest(BaseModel):
    amount: Decimal = Field(..., description="Transaction amount")
    transaction_type: TransactionType = Field(..., description="Transaction type")
    bet_id: Optional[int] = Field(None, description="Associated bet ID")
    sportsbook_id: Optional[str] = Field(None, description="Sportsbook identifier")
    sportsbook_name: Optional[str] = Field(None, description="Sportsbook name")
    external_transaction_id: Optional[str] = Field(None, description="External transaction ID")
    description: Optional[str] = Field(None, description="Transaction description")
    reference: Optional[str] = Field(None, description="Internal reference")
    category: Optional[str] = Field(None, description="Transaction category")
    fee_amount: Optional[Decimal] = Field(0.00, ge=0, description="Fee amount")


class TransactionUpdateRequest(BaseModel):
    status: Optional[TransactionStatus] = Field(None, description="Transaction status")
    processed_at: Optional[datetime] = Field(None, description="Processing timestamp")
    processing_details: Optional[Dict[str, Any]] = Field(None, description="Processing details")
    failure_reason: Optional[str] = Field(None, description="Failure reason if failed")


class TransactionResponse(BaseSchema):
    id: int
    user_id: int
    bet_id: Optional[int]
    amount: Decimal
    currency: str
    transaction_type: TransactionType
    status: TransactionStatus
    sportsbook_id: Optional[str]
    sportsbook_name: Optional[str]
    external_transaction_id: Optional[str]
    description: Optional[str]
    reference: Optional[str]
    category: Optional[str]
    running_balance: Optional[Decimal]
    fee_amount: Decimal
    net_amount: Decimal
    processed_at: Optional[datetime]
    failure_reason: Optional[str]
    created_at: datetime
    updated_at: datetime


class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int
    page: int
    per_page: int


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
