"""Schema definitions for API models"""

# Import all schemas for backward compatibility
from .bet_schemas import BetCreateRequest, BetListResponse, BetResponse, BetUpdateRequest
from .common_schemas import (
    DeepHealthResponse,
    DigestSubscriptionRequest,
    DigestSubscriptionResponse,
    EdgeCreateRequest,
    EdgeListResponse,
    EdgeResponse,
    EdgeUpdateRequest,
    HealthResponse,
    OddsBestLinesResponse,
    OddsResponse,
    TransactionCreateRequest,
    TransactionListResponse,
    TransactionResponse,
    TransactionUpdateRequest,
)
from .user_schemas import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    UserResponse,
    UserUpdateRequest,
)

__all__ = [
    "BetCreateRequest",
    "BetUpdateRequest",
    "BetResponse",
    "BetListResponse",
    "UserRegistrationRequest",
    "UserRegistrationResponse",
    "UserResponse",
    "UserUpdateRequest",
    "TransactionCreateRequest",
    "TransactionUpdateRequest",
    "TransactionResponse",
    "TransactionListResponse",
    "DigestSubscriptionRequest",
    "DigestSubscriptionResponse",
    "OddsBestLinesResponse",
    "OddsResponse",
    "DeepHealthResponse",
    "HealthResponse",
    "EdgeCreateRequest",
    "EdgeListResponse",
    "EdgeResponse",
    "EdgeUpdateRequest",
]
