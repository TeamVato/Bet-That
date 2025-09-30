"""FastAPI dependencies for authentication and database access

Enhanced to support both JWT and legacy authentication during migration period.
"""

from typing import Optional, Union

from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import User


def get_current_user_external_id(x_user_id: Optional[str] = Header(None)) -> str:
    """Extract external user ID from header. Simple auth for Sprint 1."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header required")
    return x_user_id


# Bearer token scheme for JWT authentication
bearer_scheme = HTTPBearer(auto_error=False)


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    if hasattr(request.client, "host"):
        return request.client.host

    return "unknown"


async def get_current_user_jwt(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user from JWT token"""
    if not credentials or not credentials.credentials:
        return None

    try:
        from .auth.exceptions import TokenExpiredError, TokenInvalidError, TokenRevokedError
        from .auth.jwt_auth import verify_token

        # Verify JWT token
        payload = verify_token(credentials.credentials, token_type="access")
        user_id = int(payload["sub"])

        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()

        if user and user.is_active:
            # Update last activity
            from datetime import datetime, timezone

            user.last_activity_at = datetime.now(timezone.utc)
            db.commit()
            return user

        return None

    except (TokenExpiredError, TokenInvalidError, TokenRevokedError, ImportError):
        return None
    except Exception:
        return None


async def get_current_user_legacy(
    external_id: str = Depends(get_current_user_external_id), db: Session = Depends(get_db)
) -> Optional[dict]:
    """Legacy user authentication via external ID header"""
    user = db.query(User).filter(User.external_id == external_id).first()

    if not user:
        # For backward compatibility, return external_id info
        return {"external_id": external_id, "id": None, "email": None, "name": None}

    return {
        "id": user.id,
        "external_id": user.external_id,
        "email": user.email,
        "name": user.name,
        "is_active": user.is_active,
        "status": user.status,
    }


async def get_current_user(
    request: Request,
    # JWT authentication (preferred)
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    # Legacy authentication (fallback)
    x_user_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Optional[Union[User, dict]]:
    """Unified user authentication supporting both JWT and legacy methods

    Priority:
    1. JWT Bearer token authentication (returns User model)
    2. Legacy X-User-Id header authentication (returns dict)

    Returns:
        User model (JWT auth) or dict (legacy auth) or None
    """
    # Try JWT authentication first
    if credentials and credentials.credentials:
        user = await get_current_user_jwt(request, credentials, db)
        if user:
            return user

    # Fall back to legacy authentication
    if x_user_id:
        try:
            return await get_current_user_legacy(x_user_id, db)
        except HTTPException:
            pass

    return None


async def require_authentication(
    current_user: Optional[Union[User, dict]] = Depends(get_current_user)
) -> Union[User, dict]:
    """Require user to be authenticated (either JWT or legacy)

    Returns:
        Authenticated user (User model or dict)

    Raises:
        HTTPException: If user is not authenticated
    """
    if current_user is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return current_user


async def require_jwt_authentication(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Require JWT authentication specifically (no legacy fallback)

    Returns:
        User model from JWT token

    Raises:
        HTTPException: If JWT authentication fails
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=401, detail="JWT token required", headers={"WWW-Authenticate": "Bearer"}
        )

    user = await get_current_user_jwt(request, credentials, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
