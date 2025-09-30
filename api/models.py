"""SQLAlchemy models for existing and new tables"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    DECIMAL,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

from .database import Base
from .enums.betting_enums import BetCategory
from .enums.betting_enums import BetStatus as PeerBetStatus
from .enums.betting_enums import BetType, OutcomeStatus, ParticipantStatus


# Enums for type safety
class BetStatus(str, Enum):
    PENDING = "pending"
    MATCHED = "matched"
    SETTLED = "settled"
    CANCELLED = "cancelled"
    VOIDED = "voided"


class EdgeStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    STALE = "stale"
    INVALID = "invalid"


class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    BET_PLACED = "bet_placed"
    BET_PAYOUT = "bet_payout"
    BET_REFUND = "bet_refund"
    BONUS = "bonus"
    FEE = "fee"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    BANNED = "banned"


# EXISTING TABLES (Read-only)
class CurrentBestLine(Base):
    __tablename__ = "current_best_lines"
    player = Column(String, primary_key=True)
    market = Column(String, primary_key=True)
    book = Column(String, primary_key=True)
    line = Column(Float)
    pos = Column(String)
    over_odds = Column(Integer)
    under_odds = Column(Integer)
    updated_at = Column(String)
    event_id = Column(String)
    commence_time = Column(String)
    home_team = Column(String)
    away_team = Column(String)
    season = Column(Integer)
    week = Column(Integer)
    team_code = Column(String)
    opponent_def_code = Column(String)
    is_stale = Column(Integer)


class Event(Base):
    """Enhanced Event model with comprehensive sports data"""

    __tablename__ = "events"

    event_id = Column(String, primary_key=True)
    sport_key = Column(String, nullable=False, index=True)
    commence_time = Column(DateTime, nullable=True, index=True)
    home_team = Column(String, nullable=True, index=True)
    away_team = Column(String, nullable=True, index=True)
    season = Column(Integer, nullable=True, index=True)
    week = Column(Integer, nullable=True, index=True)
    venue = Column(String, nullable=True)
    region = Column(String, default="us", nullable=False)

    # Event status
    status = Column(
        String(20), default="scheduled", nullable=False
    )  # scheduled, live, completed, cancelled

    # Results (when available)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Audit fields
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    bets = relationship("Bet", back_populates="event")
    edges = relationship("Edge", back_populates="event")

    __table_args__ = (
        CheckConstraint(
            "status IN ('scheduled', 'live', 'completed', 'cancelled')",
            name="check_event_status_valid",
        ),
        Index("idx_events_season_week", "season", "week"),
        Index("idx_events_commence_time", "commence_time"),
        Index("idx_events_teams", "home_team", "away_team"),
        Index("idx_events_status", "status"),
    )


# NEW USER TABLES
class User(Base):
    """Enhanced User model with authentication and risk management"""

    __tablename__ = "users"

    # Primary key and identity
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(255), unique=True, nullable=False, index=True)

    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(30), unique=True, nullable=True, index=True)  # Added for registration
    password_hash = Column(String(255), nullable=True)  # For future local auth
    salt = Column(String(64), nullable=True)  # Added for PBKDF2 compatibility
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime, nullable=True)

    # Profile information
    name = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)  # Added for registration
    timezone = Column(String(50), default="UTC", nullable=False)
    phone = Column(String(20), nullable=True)
    phone_number = Column(String(20), nullable=True)  # Added for consistency

    # Account status and verification
    status = Column(String(50), default=UserStatus.PENDING_VERIFICATION, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_level = Column(
        String(20), default="basic", nullable=False
    )  # basic, enhanced, premium

    # Risk management fields
    max_bet_size: Column[Decimal] = Column(DECIMAL(12, 2), default=1000.00, nullable=False)
    daily_bet_limit: Column[Decimal] = Column(DECIMAL(12, 2), default=5000.00, nullable=False)
    monthly_bet_limit: Column[Decimal] = Column(DECIMAL(12, 2), default=50000.00, nullable=False)
    risk_tolerance = Column(String(20), default="medium", nullable=False)  # low, medium, high
    auto_kelly_sizing = Column(Boolean, default=False, nullable=False)
    max_kelly_fraction = Column(Float, default=0.25, nullable=False)

    # Preferences
    preferred_sports = Column(Text, nullable=True)  # JSON array of sports
    notification_preferences = Column(Text, nullable=True)  # JSON object
    ui_preferences = Column(Text, nullable=True)  # JSON object for UI settings

    # Audit trail
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, nullable=True)
    created_by = Column(String(255), nullable=True)  # Admin who created account

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    bets = relationship("Bet", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    blacklisted_tokens = relationship(
        "JWTTokenBlacklist", back_populates="user", cascade="all, delete-orphan"
    )
    auth_logs = relationship("AuthLog", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    # Peer-to-peer betting relationships
    created_peer_bets = relationship(
        "PeerBet", back_populates="creator", cascade="all, delete-orphan"
    )
    peer_bet_participations = relationship(
        "PeerBetParticipant", back_populates="user", cascade="all, delete-orphan"
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint("max_bet_size > 0", name="check_max_bet_size_positive"),
        CheckConstraint("daily_bet_limit > 0", name="check_daily_limit_positive"),
        CheckConstraint("monthly_bet_limit >= daily_bet_limit", name="check_monthly_gte_daily"),
        CheckConstraint(
            "max_kelly_fraction > 0 AND max_kelly_fraction <= 1", name="check_kelly_fraction_valid"
        ),
        CheckConstraint(
            "risk_tolerance IN ('low', 'medium', 'high')", name="check_risk_tolerance_valid"
        ),
        CheckConstraint(
            "verification_level IN ('basic', 'enhanced', 'premium')",
            name="check_verification_level_valid",
        ),
        Index("idx_users_status_active", "status", "is_active"),
        Index("idx_users_last_activity", "last_activity_at"),
        Index("idx_users_deleted", "deleted_at"),
    )

    @validates("email")
    def validate_email(self, key, email):
        """Basic email validation"""
        if "@" not in email or "." not in email:
            raise ValueError("Invalid email format")
        return email.lower()

    @validates("max_kelly_fraction")
    def validate_kelly_fraction(self, key, value):
        """Validate Kelly fraction is within reasonable bounds"""
        if value <= 0 or value > 1:
            raise ValueError("Kelly fraction must be between 0 and 1")
        return value

    def is_deleted(self) -> bool:
        """Check if user is soft deleted"""
        return self.deleted_at is not None

    def can_place_bet(self, amount: float) -> bool:
        """Check if user can place a bet of given amount"""
        if not self.is_active or self.is_deleted():
            return False
        return amount <= float(self.max_bet_size)

    @property
    def total_peer_bets_created(self) -> int:
        """Count of peer bets created by this user"""
        return len(self.created_peer_bets)

    @property
    def total_peer_bets_participated(self) -> int:
        """Count of peer bets this user has participated in"""
        return len(self.peer_bet_participations)

    @property
    def active_peer_participations(self) -> list:
        """Get user's active peer bet participations"""
        return [p for p in self.peer_bet_participations if p.status == ParticipantStatus.ACTIVE]


class Edge(Base):
    """Enhanced Edge model for arbitrage opportunities"""

    __tablename__ = "edges"

    # Primary key
    edge_id = Column(Integer, primary_key=True, autoincrement=True)

    # Market identification
    sport_key = Column(String(50), nullable=False, index=True)
    event_id = Column(String(255), ForeignKey("events.event_id"), nullable=False, index=True)
    market_type = Column(String(50), nullable=False, index=True)  # spread, total, moneyline, prop
    market_description = Column(String(255), nullable=False)
    player = Column(String(255), nullable=True, index=True)  # For player props
    position = Column(String(10), nullable=True)  # QB, RB, WR, TE

    # Line information
    line = Column(Float, nullable=True)
    side = Column(String(20), nullable=False)  # over/under, home/away, etc.

    # Arbitrage opportunity data
    best_odds_american = Column(Integer, nullable=False)
    best_odds_decimal = Column(Float, nullable=False)
    best_sportsbook = Column(String(100), nullable=False, index=True)
    implied_probability = Column(Float, nullable=False)
    fair_probability = Column(Float, nullable=False)

    # Profitability metrics
    edge_percentage = Column(Float, nullable=False, index=True)
    expected_value_per_dollar = Column(Float, nullable=False)
    kelly_fraction = Column(Float, nullable=False)
    recommended_stake: Column[Optional[Decimal]] = Column(DECIMAL(12, 2), nullable=True)
    max_stake: Column[Optional[Decimal]] = Column(DECIMAL(12, 2), nullable=True)

    # Model data
    model_probability = Column(Float, nullable=False)
    model_confidence = Column(Float, nullable=True)
    shrunk_probability = Column(Float, nullable=True)
    strategy_tag = Column(String(100), nullable=False, index=True)

    # Temporal data
    discovered_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_odds_check = Column(DateTime, nullable=True)

    # Status and validation
    status = Column(String(50), default=EdgeStatus.ACTIVE, nullable=False, index=True)
    is_stale = Column(Boolean, default=False, nullable=False, index=True)
    is_arbitrage = Column(Boolean, default=False, nullable=False)
    validation_score = Column(Float, nullable=True)

    # Context data
    season = Column(Integer, nullable=True, index=True)
    week = Column(Integer, nullable=True, index=True)
    team = Column(String(10), nullable=True)
    opponent_team = Column(String(10), nullable=True)
    home_team = Column(String(100), nullable=True)
    away_team = Column(String(100), nullable=True)
    is_home = Column(Boolean, nullable=True)

    # Defense and matchup context
    defense_tier = Column(String(20), nullable=True)  # generous, stingy, neutral
    defense_score = Column(Float, nullable=True)
    opponent_defense_code = Column(String(10), nullable=True)

    # Market depth and liquidity
    market_liquidity = Column(String(20), nullable=True)  # high, medium, low
    bet_limit: Column[Optional[Decimal]] = Column(DECIMAL(12, 2), nullable=True)
    overround = Column(Float, nullable=True)

    # Tracking metadata
    source = Column(String(100), nullable=True)  # odds_api, manual, calculated
    calculation_version = Column(String(20), nullable=True)
    raw_data_hash = Column(String(64), nullable=True)

    # Audit fields
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(255), nullable=True)

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    event = relationship("Event", back_populates="edges")
    bets = relationship("Bet", back_populates="edge")

    # Table constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "edge_percentage >= -1.0 AND edge_percentage <= 5.0",
            name="check_edge_percentage_bounds",
        ),
        CheckConstraint(
            "expected_value_per_dollar >= -1.0 AND expected_value_per_dollar <= 10.0",
            name="check_ev_bounds",
        ),
        CheckConstraint(
            "kelly_fraction >= 0 AND kelly_fraction <= 1", name="check_kelly_fraction_bounds"
        ),
        CheckConstraint(
            "implied_probability >= 0 AND implied_probability <= 1",
            name="check_implied_prob_bounds",
        ),
        CheckConstraint(
            "fair_probability >= 0 AND fair_probability <= 1", name="check_fair_prob_bounds"
        ),
        CheckConstraint(
            "model_probability >= 0 AND model_probability <= 1", name="check_model_prob_bounds"
        ),
        CheckConstraint("best_odds_american != 0", name="check_odds_nonzero"),
        CheckConstraint("best_odds_decimal > 0", name="check_decimal_odds_positive"),
        CheckConstraint(
            "side IN ('over', 'under', 'home', 'away', 'yes', 'no')", name="check_side_valid"
        ),
        CheckConstraint(
            "defense_tier IS NULL OR defense_tier IN ('generous', 'stingy', 'neutral')",
            name="check_defense_tier_valid",
        ),
        Index("idx_edges_event_market", "event_id", "market_type"),
        Index("idx_edges_player_market", "player", "market_type"),
        Index("idx_edges_ev_desc", "expected_value_per_dollar"),
        Index("idx_edges_kelly_desc", "kelly_fraction"),
        Index("idx_edges_season_week", "season", "week"),
        Index("idx_edges_discovered_at", "discovered_at"),
        Index("idx_edges_expires_at", "expires_at"),
        Index("idx_edges_status_stale", "status", "is_stale"),
        Index("idx_edges_sportsbook", "best_sportsbook"),
        Index("idx_edges_strategy", "strategy_tag"),
        Index("idx_edges_deleted", "deleted_at"),
        UniqueConstraint(
            "event_id",
            "market_type",
            "player",
            "side",
            "line",
            "best_sportsbook",
            name="uq_edge_market_line",
        ),
    )

    @validates("edge_percentage")
    def validate_edge_percentage(self, key, value):
        """Validate edge percentage is within reasonable bounds"""
        if value < -1.0 or value > 5.0:
            raise ValueError("Edge percentage must be between -100% and 500%")
        return value

    @validates("kelly_fraction")
    def validate_kelly_fraction(self, key, value):
        """Validate Kelly fraction"""
        if value < 0 or value > 1:
            raise ValueError("Kelly fraction must be between 0 and 1")
        return value

    def is_expired(self) -> bool:
        """Check if edge has expired"""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at.replace(tzinfo=timezone.utc)

    def is_deleted(self) -> bool:
        """Check if edge is soft deleted"""
        return self.deleted_at is not None

    def calculate_recommended_stake(self, bankroll: float, max_fraction: float = 0.25) -> float:
        """Calculate recommended stake using Kelly criterion with max fraction cap"""
        kelly_stake = bankroll * self.kelly_fraction
        max_stake = bankroll * max_fraction
        return min(kelly_stake, max_stake)


class Bet(Base):
    """Enhanced Bet model with comprehensive tracking and risk management"""

    __tablename__ = "bets"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    external_user_id = Column(String(255), nullable=False, index=True)  # Backward compatibility

    # Core betting information
    event_id = Column(String(255), ForeignKey("events.event_id"), nullable=False, index=True)
    edge_id = Column(Integer, ForeignKey("edges.edge_id"), nullable=True, index=True)
    market_type = Column(String(50), nullable=False)  # spread, total, moneyline, prop
    market_description = Column(String(255), nullable=False)
    selection = Column(String(255), nullable=False)
    line = Column(Float, nullable=True)  # Point spread or total
    side = Column(String(20), nullable=True)  # over/under for totals, home/away for spreads

    # Financial data
    stake: Column[Decimal] = Column(DECIMAL(12, 2), nullable=False)
    odds_american = Column(Integer, nullable=False)
    odds_decimal = Column(Float, nullable=False)
    potential_return: Column[Decimal] = Column(DECIMAL(12, 2), nullable=False)
    actual_return: Column[Optional[Decimal]] = Column(DECIMAL(12, 2), nullable=True)
    net_profit: Column[Optional[Decimal]] = Column(DECIMAL(12, 2), nullable=True)

    # Status tracking
    status = Column(String(50), default=BetStatus.PENDING, nullable=False, index=True)
    result = Column(String(20), nullable=True)  # win, loss, push, void
    settled_at = Column(DateTime, nullable=True)
    graded_at = Column(DateTime, nullable=True)

    # Platform integration
    sportsbook_id = Column(String(100), nullable=False, index=True)
    sportsbook_name = Column(String(100), nullable=False)
    external_bet_id = Column(String(255), nullable=True, index=True)
    external_ticket_id = Column(String(255), nullable=True)

    # Edge relationship and analytics
    edge_percentage = Column(Float, nullable=True)
    kelly_fraction_used = Column(Float, nullable=True)
    expected_value: Column[Optional[Decimal]] = Column(DECIMAL(12, 2), nullable=True)

    # CLV (Closing Line Value) tracking
    clv_cents = Column(Float, nullable=True)
    beat_close = Column(Boolean, nullable=True)
    closing_odds_american = Column(Integer, nullable=True)
    closing_odds_decimal = Column(Float, nullable=True)

    # Risk metadata
    risk_score = Column(Float, nullable=True)
    confidence_level = Column(Float, nullable=True)
    model_probability = Column(Float, nullable=True)

    # Additional metadata
    notes = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array for categorization
    source = Column(String(50), default="manual", nullable=False)  # manual, automated, copied

    # Timestamps and audit
    placed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(255), nullable=True)

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="bets")
    edge = relationship("Edge", back_populates="bets")
    event = relationship("Event", back_populates="bets")
    transactions = relationship("Transaction", back_populates="bet", cascade="all, delete-orphan")

    # Table constraints and indexes
    __table_args__ = (
        CheckConstraint("stake > 0", name="check_stake_positive"),
        CheckConstraint("odds_decimal > 0", name="check_odds_decimal_positive"),
        CheckConstraint("potential_return > 0", name="check_potential_return_positive"),
        CheckConstraint("odds_american != 0", name="check_odds_american_nonzero"),
        CheckConstraint(
            "result IS NULL OR result IN ('win', 'loss', 'push', 'void')", name="check_result_valid"
        ),
        CheckConstraint("source IN ('manual', 'automated', 'copied')", name="check_source_valid"),
        Index("idx_bets_user_status", "user_id", "status"),
        Index("idx_bets_event_market", "event_id", "market_type"),
        Index("idx_bets_sportsbook_status", "sportsbook_id", "status"),
        Index("idx_bets_placed_at", "placed_at"),
        Index("idx_bets_edge_id", "edge_id"),
        Index("idx_bets_deleted", "deleted_at"),
        UniqueConstraint("external_bet_id", "sportsbook_id", name="uq_external_bet_sportsbook"),
    )

    @validates("odds_american")
    def validate_odds_american(self, key, value):
        """Validate American odds format"""
        if value == 0 or value < -10000 or value > 10000:
            raise ValueError("Invalid American odds")
        return value

    @validates("stake")
    def validate_stake(self, key, value):
        """Validate stake is positive"""
        if value <= 0:
            raise ValueError("Stake must be positive")
        return value

    def calculate_potential_return(self) -> float:
        """Calculate potential return based on stake and odds"""
        return float(self.stake) * self.odds_decimal

    def is_settled(self) -> bool:
        """Check if bet is settled"""
        return self.status == BetStatus.SETTLED

    def is_deleted(self) -> bool:
        """Check if bet is soft deleted"""
        return self.deleted_at is not None


# PEER-TO-PEER BETTING MODELS
class PeerBet(Base):
    """Core peer-to-peer bet entity representing a wager between users"""

    __tablename__ = "peer_bets"

    # Primary Information
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(50), default=BetCategory.OTHER, nullable=False, index=True)
    bet_type = Column(String(50), default=BetType.BINARY, nullable=False, index=True)

    # Creator Information
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Betting Parameters
    minimum_stake = Column(DECIMAL(12, 2), nullable=False)
    maximum_stake = Column(DECIMAL(12, 2), nullable=True)
    total_stake_pool = Column(DECIMAL(12, 2), default=0.00, nullable=False)
    participant_limit = Column(Integer, nullable=True)
    current_participants = Column(Integer, default=0, nullable=False)

    # Timing
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    starts_at = Column(DateTime, nullable=True, index=True)  # When betting opens
    locks_at = Column(DateTime, nullable=True, index=True)  # When betting closes
    resolves_at = Column(DateTime, nullable=True, index=True)  # Expected resolution
    resolved_at = Column(DateTime, nullable=True)  # Actual resolution

    # Status and Configuration
    status = Column(String(50), default=PeerBetStatus.DRAFT, nullable=False, index=True)
    is_public = Column(Boolean, default=True, nullable=False, index=True)
    requires_approval = Column(Boolean, default=False, nullable=False)
    auto_resolve = Column(Boolean, default=False, nullable=False)

    # Outcome Management
    possible_outcomes = Column(Text, nullable=False)  # JSON string of possible outcomes
    winning_outcome = Column(String(255), nullable=True)
    outcome_source = Column(Text, nullable=True)  # URL or description of outcome source

    # Platform Configuration
    platform_fee_percentage = Column(DECIMAL(5, 2), default=5.0, nullable=False)
    creator_fee_percentage = Column(DECIMAL(5, 2), default=0.0, nullable=False)

    # Metadata
    tags = Column(Text, nullable=True)  # JSON array of tags
    external_reference = Column(String(255), nullable=True)  # External event/game ID
    notes = Column(String(500), nullable=True)

    # Audit fields
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    creator = relationship("User", back_populates="created_peer_bets")
    participants = relationship(
        "PeerBetParticipant", back_populates="bet", cascade="all, delete-orphan"
    )
    outcomes = relationship("PeerBetOutcome", back_populates="bet", cascade="all, delete-orphan")

    # Table constraints
    __table_args__ = (
        CheckConstraint("minimum_stake > 0", name="check_peer_bet_min_stake_positive"),
        CheckConstraint(
            "maximum_stake IS NULL OR maximum_stake >= minimum_stake",
            name="check_peer_bet_max_stake_valid",
        ),
        CheckConstraint(
            "participant_limit IS NULL OR participant_limit >= 2",
            name="check_peer_bet_participant_limit_valid",
        ),
        CheckConstraint(
            "platform_fee_percentage >= 0 AND platform_fee_percentage <= 100",
            name="check_peer_bet_platform_fee_valid",
        ),
        CheckConstraint(
            "creator_fee_percentage >= 0 AND creator_fee_percentage <= 100",
            name="check_peer_bet_creator_fee_valid",
        ),
        CheckConstraint("total_stake_pool >= 0", name="check_peer_bet_total_stake_non_negative"),
        CheckConstraint(
            "current_participants >= 0", name="check_peer_bet_current_participants_non_negative"
        ),
        Index("idx_peer_bets_creator_status", "creator_id", "status"),
        Index("idx_peer_bets_category_status", "category", "status"),
        Index("idx_peer_bets_public_active", "is_public", "status"),
        Index("idx_peer_bets_locks_at", "locks_at"),
        Index("idx_peer_bets_resolves_at", "resolves_at"),
        Index("idx_peer_bets_deleted", "deleted_at"),
    )

    @property
    def is_active(self) -> bool:
        """Check if bet is currently accepting participants"""
        now = datetime.now(timezone.utc)
        return (
            self.status == PeerBetStatus.ACTIVE
            and (self.starts_at is None or self.starts_at <= now)
            and (self.locks_at is None or self.locks_at > now)
            and (
                self.participant_limit is None or self.current_participants < self.participant_limit
            )
        )

    @property
    def is_locked(self) -> bool:
        """Check if bet is locked (no new participants)"""
        now = datetime.now(timezone.utc)
        return self.status in [PeerBetStatus.LOCKED, PeerBetStatus.COMPLETED] or (
            self.locks_at is not None and self.locks_at <= now
        )

    @property
    def can_be_resolved(self) -> bool:
        """Check if bet can be resolved"""
        return (
            self.status == PeerBetStatus.LOCKED
            and self.current_participants >= 2
            and (self.resolves_at is None or self.resolves_at <= datetime.now(timezone.utc))
        )

    def is_deleted(self) -> bool:
        """Check if peer bet is soft deleted"""
        return self.deleted_at is not None


class PeerBetOutcome(Base):
    """Individual outcomes for a peer bet (e.g., Team A wins, Team B wins)"""

    __tablename__ = "peer_bet_outcomes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bet_id = Column(Integer, ForeignKey("peer_bets.id"), nullable=False, index=True)

    # Outcome Details
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    odds = Column(DECIMAL(8, 2), nullable=True)

    # Betting Pool for this outcome
    total_stakes = Column(DECIMAL(12, 2), default=0.00, nullable=False)
    participant_count = Column(Integer, default=0, nullable=False)

    # Resolution
    status = Column(String(50), default=OutcomeStatus.PENDING, nullable=False, index=True)
    probability = Column(DECIMAL(6, 4), nullable=True)

    # Metadata
    order_index = Column(Integer, default=0, nullable=False)  # For display ordering
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    bet = relationship("PeerBet", back_populates="outcomes")

    # Table constraints
    __table_args__ = (
        CheckConstraint("odds IS NULL OR odds >= 1.0", name="check_peer_bet_outcome_odds_valid"),
        CheckConstraint(
            "probability IS NULL OR (probability >= 0.0 AND probability <= 1.0)",
            name="check_peer_bet_outcome_probability_valid",
        ),
        CheckConstraint(
            "total_stakes >= 0", name="check_peer_bet_outcome_total_stakes_non_negative"
        ),
        CheckConstraint(
            "participant_count >= 0", name="check_peer_bet_outcome_participant_count_non_negative"
        ),
        Index("idx_peer_bet_outcomes_bet_status", "bet_id", "status"),
        Index("idx_peer_bet_outcomes_order", "bet_id", "order_index"),
    )


class PeerBetParticipant(Base):
    """User participation in a specific peer bet"""

    __tablename__ = "peer_bet_participants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bet_id = Column(Integer, ForeignKey("peer_bets.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Participation Details
    chosen_outcome = Column(String(255), nullable=False)  # The outcome they're betting on
    stake_amount = Column(DECIMAL(12, 2), nullable=False)
    potential_payout = Column(DECIMAL(12, 2), nullable=False)

    # Status and Timing
    status = Column(String(50), default=ParticipantStatus.ACTIVE, nullable=False, index=True)
    joined_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    withdrawn_at = Column(DateTime, nullable=True)
    paid_out_at = Column(DateTime, nullable=True)

    # Payout Information
    actual_payout = Column(DECIMAL(12, 2), nullable=True)
    platform_fee = Column(DECIMAL(12, 2), nullable=True)
    creator_fee = Column(DECIMAL(12, 2), nullable=True)

    # Relationships
    bet = relationship("PeerBet", back_populates="participants")
    user = relationship("User", back_populates="peer_bet_participations")

    # Table constraints
    __table_args__ = (
        CheckConstraint("stake_amount > 0", name="check_peer_bet_participant_stake_positive"),
        CheckConstraint(
            "potential_payout >= 0", name="check_peer_bet_participant_potential_payout_non_negative"
        ),
        CheckConstraint(
            "actual_payout IS NULL OR actual_payout >= 0",
            name="check_peer_bet_participant_actual_payout_non_negative",
        ),
        CheckConstraint(
            "platform_fee IS NULL OR platform_fee >= 0",
            name="check_peer_bet_participant_platform_fee_non_negative",
        ),
        CheckConstraint(
            "creator_fee IS NULL OR creator_fee >= 0",
            name="check_peer_bet_participant_creator_fee_non_negative",
        ),
        UniqueConstraint("bet_id", "user_id", name="unique_user_peer_bet_participation"),
        Index("idx_peer_bet_participants_user_status", "user_id", "status"),
        Index("idx_peer_bet_participants_bet_status", "bet_id", "status"),
        Index("idx_peer_bet_participants_joined_at", "joined_at"),
    )


class Transaction(Base):
    """Financial transaction model for comprehensive record keeping"""

    __tablename__ = "transactions"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Bet relationship (optional - not all transactions are bet-related)
    bet_id = Column(Integer, ForeignKey("bets.id"), nullable=True, index=True)

    # Financial data
    amount: Column[Decimal] = Column(DECIMAL(12, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    transaction_type = Column(String(50), nullable=False, index=True)
    status = Column(String(50), default=TransactionStatus.PENDING, nullable=False, index=True)

    # Platform/sportsbook tracking
    sportsbook_id = Column(String(100), nullable=True, index=True)
    sportsbook_name = Column(String(100), nullable=True)
    external_transaction_id = Column(String(255), nullable=True, unique=True, index=True)

    # Transaction details
    description = Column(String(500), nullable=True)
    reference = Column(String(255), nullable=True, index=True)  # Internal reference
    category = Column(String(50), nullable=True)  # betting, account, bonus, etc.

    # Financial reconciliation
    running_balance: Column[Optional[Decimal]] = Column(DECIMAL(12, 2), nullable=True)
    fee_amount: Column[Decimal] = Column(DECIMAL(12, 2), default=0.00, nullable=False)
    net_amount: Column[Decimal] = Column(DECIMAL(12, 2), nullable=False)  # amount - fee_amount

    # Processing information
    processed_at = Column(DateTime, nullable=True)
    processing_details = Column(Text, nullable=True)  # JSON object with processing info
    failure_reason = Column(String(500), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)

    # Audit trail
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="transactions")
    bet = relationship("Bet", back_populates="transactions")

    # Table constraints and indexes
    __table_args__ = (
        CheckConstraint("amount != 0", name="check_amount_nonzero"),
        CheckConstraint("fee_amount >= 0", name="check_fee_amount_non_negative"),
        CheckConstraint("retry_count >= 0", name="check_retry_count_non_negative"),
        CheckConstraint("currency IN ('USD', 'EUR', 'GBP', 'CAD')", name="check_currency_valid"),
        CheckConstraint(
            "category IS NULL OR category IN ('betting', 'account', 'bonus', 'fee', 'adjustment')",
            name="check_category_valid",
        ),
        Index("idx_transactions_user_type", "user_id", "transaction_type"),
        Index("idx_transactions_user_status", "user_id", "status"),
        Index("idx_transactions_sportsbook", "sportsbook_id"),
        Index("idx_transactions_created_at", "created_at"),
        Index("idx_transactions_processed_at", "processed_at"),
        Index("idx_transactions_reference", "reference"),
        Index("idx_transactions_bet_id", "bet_id"),
    )

    @validates("amount")
    def validate_amount(self, key, value):
        """Validate amount is not zero"""
        if value == 0:
            raise ValueError("Transaction amount cannot be zero")
        return value

    @validates("fee_amount")
    def validate_fee_amount(self, key, value):
        """Validate fee amount is non-negative"""
        if value < 0:
            raise ValueError("Fee amount cannot be negative")
        return value

    def is_credit(self) -> bool:
        """Check if transaction is a credit (positive amount)"""
        return float(self.amount) > 0

    def is_debit(self) -> bool:
        """Check if transaction is a debit (negative amount)"""
        return float(self.amount) < 0


class DigestSubscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    frequency = Column(String(50), default="weekly", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


# JWT Authentication Tables
class JWTTokenBlacklist(Base):
    """JWT token blacklist for revoked tokens"""

    __tablename__ = "jwt_token_blacklist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_type = Column(String(50), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked_at = Column(DateTime, default=func.now(), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="blacklisted_tokens")

    __table_args__ = (
        CheckConstraint(
            "token_type IN ('access', 'refresh', 'password_reset')", name="check_token_type_valid"
        ),
        Index("idx_jwt_blacklist_user_type", "user_id", "token_type"),
    )


class AuthLog(Base):
    """Authentication event logging for security auditing"""

    __tablename__ = "auth_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, index=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, nullable=False, index=True)
    failure_reason = Column(Text, nullable=True)
    additional_data = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="auth_logs")

    __table_args__ = (
        CheckConstraint(
            "event_type IN ('login', 'logout', 'register', 'password_change', 'password_reset', 'token_refresh', 'email_verify', 'two_factor')",
            name="check_event_type_valid",
        ),
        Index("idx_auth_logs_user_event", "user_id", "event_type"),
        Index("idx_auth_logs_ip_success", "ip_address", "success"),
    )


class UserSession(Base):
    """User session tracking for JWT token management"""

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token_jti = Column(String(255), unique=True, nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    last_activity_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")

    __table_args__ = (
        Index("idx_user_sessions_user_active", "user_id", "is_active"),
        Index("idx_user_sessions_expires_active", "expires_at", "is_active"),
    )
