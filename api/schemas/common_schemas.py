"""Common schemas used across the API"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field

from ..models import EdgeStatus, TransactionStatus, TransactionType


# Email Digest Subscription Schemas
class DigestSubscriptionRequest(BaseModel):
    email: EmailStr = Field(description="Email address for weekly digest")
    frequency: Optional[str] = Field(default="weekly", description="Subscription frequency")


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


# Edge Schemas
class EdgeCreateRequest(BaseModel):
    sport_key: str = Field(description="Sport identifier")
    event_id: str = Field(description="Event identifier")
    market_type: str = Field(description="Market type")
    market_description: str = Field(description="Market description")
    player: Optional[str] = Field(default=None, description="Player name for props")
    position: Optional[str] = Field(default=None, description="Player position")
    line: Optional[float] = Field(default=None, description="Line value")
    side: str = Field(description="Side of the bet")
    best_odds_american: int = Field(description="Best American odds")
    best_odds_decimal: float = Field(gt=0, description="Best decimal odds")
    best_sportsbook: str = Field(description="Best sportsbook")
    implied_probability: float = Field(ge=0, le=1, description="Implied probability")
    fair_probability: float = Field(ge=0, le=1, description="Fair probability")
    edge_percentage: float = Field(description="Edge percentage")
    expected_value_per_dollar: float = Field(description="Expected value per dollar")
    kelly_fraction: float = Field(ge=0, le=1, description="Kelly fraction")
    model_probability: float = Field(ge=0, le=1, description="Model probability")
    strategy_tag: str = Field(description="Strategy identifier")
    expires_at: Optional[datetime] = Field(default=None, description="Edge expiration time")


class EdgeUpdateRequest(BaseModel):
    status: Optional[EdgeStatus] = Field(default=None, description="Edge status")
    best_odds_american: Optional[int] = Field(default=None, description="Updated best odds")
    best_odds_decimal: Optional[float] = Field(default=None, gt=0, description="Updated decimal odds")
    best_sportsbook: Optional[str] = Field(default=None, description="Updated best sportsbook")
    is_stale: Optional[bool] = Field(default=None, description="Mark as stale")
    expires_at: Optional[datetime] = Field(default=None, description="Updated expiration time")


class EdgeResponse(BaseModel):
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
    amount: Decimal = Field(description="Transaction amount")
    transaction_type: TransactionType = Field(description="Transaction type")
    bet_id: Optional[int] = Field(default=None, description="Associated bet ID")
    sportsbook_id: Optional[str] = Field(default=None, description="Sportsbook identifier")
    sportsbook_name: Optional[str] = Field(default=None, description="Sportsbook name")
    external_transaction_id: Optional[str] = Field(default=None, description="External transaction ID")
    description: Optional[str] = Field(default=None, description="Transaction description")
    reference: Optional[str] = Field(default=None, description="Internal reference")
    category: Optional[str] = Field(default=None, description="Transaction category")
    fee_amount: Optional[Decimal] = Field(default=Decimal("0.00"), ge=0, description="Fee amount")


class TransactionUpdateRequest(BaseModel):
    status: Optional[TransactionStatus] = Field(default=None, description="Transaction status")
    processed_at: Optional[datetime] = Field(default=None, description="Processing timestamp")
    processing_details: Optional[Dict[str, Any]] = Field(default=None, description="Processing details")
    failure_reason: Optional[str] = Field(default=None, description="Failure reason if failed")


class TransactionResponse(BaseModel):
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
