"""Comprehensive enums for the peer-to-peer betting system"""

from enum import Enum


class BetStatus(str, Enum):
    """Status of a bet throughout its lifecycle"""

    DRAFT = "draft"  # Created but not published
    ACTIVE = "active"  # Published and accepting participants
    LOCKED = "locked"  # No new participants, awaiting outcome
    COMPLETED = "completed"  # Outcome determined, payouts processed
    CANCELLED = "cancelled"  # Bet cancelled, stakes returned
    DISPUTED = "disputed"  # Outcome contested, under review
    EXPIRED = "expired"  # Bet expired without sufficient participants


class BetType(str, Enum):
    """Types of bets supported by the platform"""

    BINARY = "binary"  # Yes/No, Win/Lose (2 outcomes)
    MULTIPLE = "multiple"  # Multiple choice (3+ outcomes)
    OVER_UNDER = "over_under"  # Numeric prediction with threshold
    RANGE = "range"  # Prediction within a numeric range
    CUSTOM = "custom"  # Custom bet structure


class BetCategory(str, Enum):
    """Categories for organizing bets"""

    SPORTS = "sports"
    POLITICS = "politics"
    ENTERTAINMENT = "entertainment"
    FINANCE = "finance"
    WEATHER = "weather"
    PERSONAL = "personal"
    TECHNOLOGY = "technology"
    OTHER = "other"


class OutcomeStatus(str, Enum):
    """Status of individual bet outcomes"""

    PENDING = "pending"  # Awaiting resolution
    WON = "won"  # Winning outcome
    LOST = "lost"  # Losing outcome
    VOID = "void"  # Voided due to unforeseen circumstances


class ParticipantStatus(str, Enum):
    """Status of a user's participation in a bet"""

    ACTIVE = "active"  # Actively participating
    WITHDRAWN = "withdrawn"  # Withdrew before bet locked
    PAID_OUT = "paid_out"  # Received payout
    FORFEITED = "forfeited"  # Lost stake
