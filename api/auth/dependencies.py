"""FastAPI dependencies for JWT authentication

Provides dependency injection for JWT token validation, user extraction,
and role-based access control within FastAPI endpoints.
"""

import logging
from datetime import datetime, timezone
from typing import Annotated, List, Optional

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, UserStatus
from ..settings import settings
from .exceptions import (
    AuthenticationError,
    EmailNotVerifiedError,
    RateLimitExceededError,
    TokenExpiredError,
    TokenInvalidError,
    TokenRevokedError,
    UserInactiveError,
    UserNotFoundError,
)
from .jwt_auth import verify_token
from .security_utils import security_manager

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
bearer_scheme = HTTPBearer(auto_error=False)


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Check for forwarded IP from reverse proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    # Check for real IP from reverse proxy
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fall back to direct connection IP
    if request.client and hasattr(request.client, "host"):
        return request.client.host

    return "unknown"


def verify_jwt_token(
    request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> dict:
    """Verify JWT token from Authorization header

    Args:
        request: FastAPI request object
        credentials: Bearer token credentials

    Returns:
        Decoded token payload

    Raises:
        AuthenticationError: If token is missing or invalid
        TokenExpiredError: If token has expired
        TokenRevokedError: If token has been revoked
        RateLimitExceededError: If too many invalid attempts
    """
    if not credentials:
        raise AuthenticationError("Authorization header missing")

    if not credentials.credentials:
        raise AuthenticationError("Bearer token missing")

    # Check rate limiting for invalid token attempts
    client_ip = get_client_ip(request)

    try:
        # Verify the token
        payload = verify_token(credentials.credentials, token_type="access")

        # Reset rate limiting on successful verification
        security_manager.rate_limiter.reset_attempts(f"auth:{client_ip}")

        return payload

    except (TokenInvalidError, TokenExpiredError, TokenRevokedError) as e:
        # Record failed attempt for rate limiting
        security_manager.rate_limiter.record_attempt(f"auth:{client_ip}")

        # Check if IP should be rate limited
        if security_manager.rate_limiter.is_rate_limited(
            f"auth:{client_ip}",
            max_attempts=settings.auth_max_attempts_per_ip,
            window_minutes=settings.auth_rate_limit_window_minutes,
        ):
            raise RateLimitExceededError("Too many invalid token attempts")

        raise e


def get_current_user_from_token(
    token_payload: dict = Depends(verify_jwt_token), db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token payload

    Args:
        token_payload: Decoded JWT token payload
        db: Database session

    Returns:
        User model instance

    Raises:
        UserNotFoundError: If user doesn't exist
        UserInactiveError: If user account is inactive
        EmailNotVerifiedError: If email verification required
    """
    try:
        user_id = int(token_payload["sub"])
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            logger.warning(f"User not found for token: {user_id}")
            raise UserNotFoundError()

        # Check if user is active
        if not user.is_active or user.status in [UserStatus.SUSPENDED, UserStatus.BANNED]:
            logger.warning(f"Inactive user attempted access: {user_id}")
            raise UserInactiveError()

        # Check email verification if required
        if settings.enable_email_verification and not user.email_verified:
            logger.warning(f"Unverified user attempted access: {user_id}")
            raise EmailNotVerifiedError()

        # Update last activity
        db.query(User).filter(User.id == user_id).update({
            "last_activity_at": datetime.now(timezone.utc)
        })
        db.commit()

        logger.debug(f"Current user retrieved: {user_id}")
        return user

    except (ValueError, KeyError) as e:
        logger.error(f"Invalid token payload: {e}")
        raise TokenInvalidError("Invalid token payload")


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user from JWT token (optional authentication)

    Args:
        credentials: Bearer token credentials (optional)
        db: Database session

    Returns:
        User model instance or None if not authenticated
    """
    if not credentials or not credentials.credentials:
        return None

    try:
        payload = verify_token(credentials.credentials, token_type="access")
        user_id = int(payload["sub"])
        user = db.query(User).filter(User.id == user_id).first()

        if user and user.is_active:
            return user
        return None

    except Exception:
        return None


def require_roles(required_roles: List[str]):
    """Dependency factory for role-based access control

    Args:
        required_roles: List of required roles

    Returns:
        FastAPI dependency function
    """

    def check_roles(
        token_payload: dict = Depends(verify_jwt_token),
        current_user: User = Depends(get_current_user_from_token),
    ) -> User:
        """Check if user has required roles"""
        user_roles = token_payload.get("roles", [])

        # Check if user has any of the required roles
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {required_roles}",
            )

        return current_user

    return check_roles


def require_verified_user(current_user: User = Depends(get_current_user_from_token)) -> User:
    """Require user to have verified email and active status

    Args:
        current_user: Current authenticated user

    Returns:
        Verified user

    Raises:
        EmailNotVerifiedError: If email not verified
        UserInactiveError: If user inactive
    """
    if settings.enable_email_verification and not current_user.email_verified:
        raise EmailNotVerifiedError()

    if current_user.status != UserStatus.ACTIVE:
        raise UserInactiveError()

    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[dict]:
    """Get user information from token without strict validation

    Compatible with existing get_current_user dependency for gradual migration.

    Args:
        credentials: Bearer token credentials
        db: Database session

    Returns:
        User dict or None
    """
    if not credentials or not credentials.credentials:
        return None

    try:
        payload = verify_token(credentials.credentials)
        user_id = int(payload["sub"])
        user = db.query(User).filter(User.id == user_id).first()

        if user:
            return {
                "id": user.id,
                "external_id": user.external_id,
                "email": user.email,
                "name": user.name,
                "roles": payload.get("roles", []),
                "is_active": user.is_active,
            }

        return None

    except Exception:
        return None


# Legacy compatibility - gradually replace with JWT dependencies
def get_current_user_external_id_legacy(x_user_id: Optional[str] = Header(None)) -> str:
    """Legacy header-based auth for backward compatibility"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header required")
    return x_user_id


# Annotated dependencies for easier usage
CurrentUser = Annotated[User, Depends(get_current_user_from_token)]
OptionalUser = Annotated[Optional[User], Depends(get_current_user_optional)]
VerifiedUser = Annotated[User, Depends(require_verified_user)]
JWTPayload = Annotated[dict, Depends(verify_jwt_token)]
