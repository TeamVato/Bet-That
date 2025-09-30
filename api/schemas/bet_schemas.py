"""Bet-related schemas for API request/response validation"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, validator

from ..enums.betting_enums import BetCategory
from ..enums.betting_enums import BetStatus as PeerBetStatus
from ..enums.betting_enums import BetType, OutcomeStatus, ParticipantStatus
from ..models import BetStatus


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


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


# PEER-TO-PEER BETTING SCHEMAS


class PeerBetOutcomeSchema(BaseModel):
    """Schema for peer bet outcomes"""

    name: str = Field(..., min_length=1, max_length=100, description="Outcome name")
    description: Optional[str] = Field(None, max_length=500, description="Outcome description")
    odds: Optional[Decimal] = Field(None, ge=1.0, description="Outcome odds")
    order_index: int = Field(default=0, description="Display order")


class PeerBetCreateRequest(BaseModel):
    """Request schema for creating a new peer bet"""

    title: str = Field(..., min_length=5, max_length=200, description="Bet title")
    description: str = Field(..., min_length=10, max_length=2000, description="Bet description")
    category: BetCategory = Field(default=BetCategory.OTHER, description="Bet category")
    bet_type: BetType = Field(default=BetType.BINARY, description="Type of bet")

    minimum_stake: Decimal = Field(..., gt=0, description="Minimum stake amount")
    maximum_stake: Optional[Decimal] = Field(None, gt=0, description="Maximum stake amount")
    participant_limit: Optional[int] = Field(
        None, ge=2, description="Maximum number of participants"
    )

    starts_at: Optional[datetime] = Field(None, description="When betting opens")
    locks_at: Optional[datetime] = Field(None, description="When betting closes")
    resolves_at: Optional[datetime] = Field(None, description="Expected resolution time")

    is_public: bool = Field(default=True, description="Whether bet is public")
    requires_approval: bool = Field(default=False, description="Whether participants need approval")
    auto_resolve: bool = Field(default=False, description="Whether to auto-resolve")

    possible_outcomes: List[PeerBetOutcomeSchema] = Field(
        ..., min_items=2, description="Possible outcomes"
    )
    tags: Optional[List[str]] = Field(None, description="Bet tags")
    external_reference: Optional[str] = Field(
        None, max_length=255, description="External reference"
    )
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")

    @validator("maximum_stake")
    def max_stake_greater_than_min(cls, v, values):
        if v is not None and "minimum_stake" in values and v <= values["minimum_stake"]:
            raise ValueError("maximum_stake must be greater than minimum_stake")
        return v

    @validator("locks_at")
    def locks_after_starts(cls, v, values):
        if v is not None and "starts_at" in values and values["starts_at"] is not None:
            if v <= values["starts_at"]:
                raise ValueError("locks_at must be after starts_at")
        return v

    @validator("resolves_at")
    def resolves_after_locks(cls, v, values):
        if v is not None and "locks_at" in values and values["locks_at"] is not None:
            if v <= values["locks_at"]:
                raise ValueError("resolves_at must be after locks_at")
        return v


class PeerBetOutcomeResponse(BaseSchema):
    """Response schema for bet outcomes"""

    id: int
    bet_id: int
    name: str
    description: Optional[str]
    odds: Optional[Decimal]
    total_stakes: Decimal
    participant_count: int
    status: OutcomeStatus
    probability: Optional[Decimal]
    order_index: int
    is_active: bool
    created_at: datetime


class PeerBetParticipantResponse(BaseSchema):
    """Response schema for bet participants"""

    id: int
    bet_id: int
    user_id: int
    chosen_outcome: str
    stake_amount: Decimal
    potential_payout: Decimal
    status: ParticipantStatus
    joined_at: datetime
    withdrawn_at: Optional[datetime]
    paid_out_at: Optional[datetime]
    actual_payout: Optional[Decimal]
    platform_fee: Optional[Decimal]
    creator_fee: Optional[Decimal]


class PeerBetResponse(BaseSchema):
    """Response schema for peer bet data"""

    id: int
    title: str
    description: str
    category: BetCategory
    bet_type: BetType
    status: PeerBetStatus

    creator_id: int
    minimum_stake: Decimal
    maximum_stake: Optional[Decimal]
    total_stake_pool: Decimal
    current_participants: int
    participant_limit: Optional[int]

    created_at: datetime
    starts_at: Optional[datetime]
    locks_at: Optional[datetime]
    resolves_at: Optional[datetime]
    resolved_at: Optional[datetime]

    is_public: bool
    requires_approval: bool
    auto_resolve: bool

    possible_outcomes: str  # JSON string
    winning_outcome: Optional[str]
    outcome_source: Optional[str]

    platform_fee_percentage: Decimal
    creator_fee_percentage: Decimal

    tags: Optional[str]  # JSON string
    external_reference: Optional[str]
    notes: Optional[str]

    updated_at: datetime

    # Computed properties
    is_active: bool
    is_locked: bool
    can_be_resolved: bool


class PeerBetSummaryResponse(BaseSchema):
    """Lightweight schema for peer bet listings"""

    id: int
    title: str
    category: BetCategory
    status: PeerBetStatus
    total_stake_pool: Decimal
    current_participants: int
    participant_limit: Optional[int]
    created_at: datetime
    locks_at: Optional[datetime]
    is_public: bool
    is_active: bool
    is_locked: bool


class PeerBetParticipateRequest(BaseModel):
    """Request schema for participating in a peer bet"""

    chosen_outcome: str = Field(..., min_length=1, max_length=255, description="Chosen outcome")
    stake_amount: Decimal = Field(..., gt=0, description="Stake amount")


class PeerBetUpdateRequest(BaseModel):
    """Request schema for updating a peer bet"""

    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    category: Optional[BetCategory] = None
    minimum_stake: Optional[Decimal] = Field(None, gt=0)
    maximum_stake: Optional[Decimal] = Field(None, gt=0)
    participant_limit: Optional[int] = Field(None, ge=2)
    starts_at: Optional[datetime] = None
    locks_at: Optional[datetime] = None
    resolves_at: Optional[datetime] = None
    is_public: Optional[bool] = None
    requires_approval: Optional[bool] = None
    auto_resolve: Optional[bool] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = Field(None, max_length=500)


class PeerBetResolveRequest(BaseModel):
    """Request schema for resolving a peer bet"""

    winning_outcome: str = Field(..., min_length=1, max_length=255, description="Winning outcome")
    outcome_source: Optional[str] = Field(None, description="Source of outcome determination")


class PeerBetListResponse(BaseModel):
    """Response schema for peer bet listings"""

    bets: List[PeerBetSummaryResponse]
    total: int
    page: int
    per_page: int
