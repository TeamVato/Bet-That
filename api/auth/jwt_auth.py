"""JWT Authentication core functionality for Bet-That API

Provides secure JWT token generation, validation, and management with proper
algorithms, expiration handling, and blacklisting capabilities.
"""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

from jose import JWTError, jwt
from jose.constants import ALGORITHMS
from pydantic import BaseModel, Field

from ..settings import settings
from .exceptions import AuthenticationError, TokenExpiredError, TokenInvalidError, TokenRevokedError

logger = logging.getLogger(__name__)


class TokenPayload(BaseModel):
    """JWT token payload structure"""

    user_id: int = Field(..., description="User database ID")
    external_id: str = Field(..., description="External user ID")
    email: str = Field(..., description="User email address")
    roles: list[str] = Field(default_factory=list, description="User roles")
    issued_at: datetime = Field(..., description="Token issued timestamp")
    expires_at: datetime = Field(..., description="Token expiration timestamp")
    token_type: str = Field(..., description="Token type (access or refresh)")
    jti: str = Field(..., description="JWT ID for revocation tracking")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class JWTConfig:
    """JWT configuration with security best practices"""

    @classmethod
    def get_algorithm(cls) -> str:
        """Get JWT algorithm from settings"""
        return settings.jwt_algorithm

    @classmethod
    def get_access_token_expire_minutes(cls) -> int:
        """Get access token expiration from settings"""
        return settings.jwt_access_token_expire_minutes

    @classmethod
    def get_refresh_token_expire_days(cls) -> int:
        """Get refresh token expiration from settings"""
        return settings.jwt_refresh_token_expire_days

    @classmethod
    def get_issuer(cls) -> str:
        """Get JWT issuer from settings"""
        return settings.jwt_issuer

    @classmethod
    def get_audience(cls) -> str:
        """Get JWT audience from settings"""
        return settings.jwt_audience

    @classmethod
    def get_secret_key(cls) -> str:
        """Get JWT secret key from environment"""
        secret = settings.jwt_secret_key
        if not secret or secret.startswith("dev-"):
            if settings.environment == "production":
                raise ValueError("JWT secret key must be set in production")
            logger.warning("Using development JWT secret key")
        return secret

    @classmethod
    def should_use_rs256(cls) -> bool:
        """Check if RS256 should be used instead of HS256"""
        return (
            settings.jwt_algorithm == "RS256"
            and settings.jwt_private_key is not None
            and settings.jwt_public_key is not None
        )

    @classmethod
    def get_private_key(cls) -> Optional[str]:
        """Get RSA private key for RS256"""
        return settings.jwt_private_key

    @classmethod
    def get_public_key(cls) -> Optional[str]:
        """Get RSA public key for RS256"""
        return settings.jwt_public_key


class TokenBlacklist:
    """In-memory token blacklist for revoked tokens

    In production, this should be backed by Redis or database
    """

    _blacklisted_tokens: set[str] = set()
    _blacklisted_users: set[int] = set()

    @classmethod
    def add_token(cls, jti: str) -> None:
        """Add token JTI to blacklist"""
        cls._blacklisted_tokens.add(jti)
        logger.info(f"Token blacklisted: {jti}")

    @classmethod
    def add_user_tokens(cls, user_id: int) -> None:
        """Blacklist all tokens for a user (logout all sessions)"""
        cls._blacklisted_users.add(user_id)
        logger.info(f"All tokens blacklisted for user: {user_id}")

    @classmethod
    def is_token_revoked(cls, jti: str, user_id: int) -> bool:
        """Check if token is revoked"""
        return jti in cls._blacklisted_tokens or user_id in cls._blacklisted_users

    @classmethod
    def remove_user_from_blacklist(cls, user_id: int) -> None:
        """Remove user from global blacklist (re-enable login)"""
        cls._blacklisted_users.discard(user_id)
        logger.info(f"User removed from blacklist: {user_id}")

    @classmethod
    def cleanup_expired_tokens(cls) -> None:
        """Cleanup expired tokens from blacklist (should be called periodically)"""
        # Note: This is a simplified implementation
        # In production, track expiration times and remove expired JTIs
        pass


def generate_jti() -> str:
    """Generate unique JWT ID for token tracking"""
    return secrets.token_urlsafe(32)


def create_access_token(
    user_id: int,
    external_id: str,
    email: str,
    roles: Optional[list[str]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT access token

    Args:
        user_id: User database ID
        external_id: External user identifier
        email: User email address
        roles: User roles/permissions
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT token string

    Raises:
        AuthenticationError: If token creation fails
    """
    try:
        now = datetime.now(timezone.utc)
        expires_delta = expires_delta or timedelta(
            minutes=JWTConfig.get_access_token_expire_minutes()
        )
        expires_at = now + expires_delta

        payload = TokenPayload(
            user_id=user_id,
            external_id=external_id,
            email=email,
            roles=roles or [],
            issued_at=now,
            expires_at=expires_at,
            token_type="access",
            jti=generate_jti(),
        )

        # Convert to JWT claims
        claims = {
            "sub": str(user_id),  # Subject (user ID)
            "external_id": external_id,
            "email": email,
            "roles": payload.roles,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
            "iss": JWTConfig.get_issuer(),
            "aud": JWTConfig.get_audience(),
            "type": "access",
            "jti": payload.jti,
        }

        token = jwt.encode(claims, JWTConfig.get_secret_key(), algorithm=JWTConfig.get_algorithm())

        logger.info(f"Access token created for user {user_id}")
        return token

    except Exception as e:
        logger.error(f"Failed to create access token: {e}")
        raise AuthenticationError("Failed to create access token")


def create_refresh_token(
    user_id: int, external_id: str, email: str, expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT refresh token

    Args:
        user_id: User database ID
        external_id: External user identifier
        email: User email address
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT refresh token string

    Raises:
        AuthenticationError: If token creation fails
    """
    try:
        now = datetime.now(timezone.utc)
        expires_delta = expires_delta or timedelta(days=JWTConfig.get_refresh_token_expire_days())
        expires_at = now + expires_delta

        # Refresh tokens have minimal claims for security
        claims = {
            "sub": str(user_id),
            "external_id": external_id,
            "email": email,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
            "iss": JWTConfig.get_issuer(),
            "aud": JWTConfig.get_audience(),
            "type": "refresh",
            "jti": generate_jti(),
        }

        token = jwt.encode(claims, JWTConfig.get_secret_key(), algorithm=JWTConfig.get_algorithm())

        logger.info(f"Refresh token created for user {user_id}")
        return token

    except Exception as e:
        logger.error(f"Failed to create refresh token: {e}")
        raise AuthenticationError("Failed to create refresh token")


def verify_token(token: str, token_type: Optional[str] = None) -> Dict[str, Any]:
    """Verify and decode JWT token

    Args:
        token: JWT token string
        token_type: Expected token type ('access' or 'refresh')

    Returns:
        Decoded token payload

    Raises:
        TokenInvalidError: If token is malformed
        TokenExpiredError: If token has expired
        TokenRevokedError: If token has been revoked
    """
    try:
        # Decode token
        payload = jwt.decode(
            token,
            JWTConfig.get_secret_key(),
            algorithms=[JWTConfig.get_algorithm()],
            audience=JWTConfig.get_audience(),
            issuer=JWTConfig.get_issuer(),
        )

        # Validate token type if specified
        if token_type and payload.get("type") != token_type:
            raise TokenInvalidError(f"Expected {token_type} token")

        # Check if token is revoked
        jti = payload.get("jti")
        user_id = int(payload.get("sub"))

        if jti and TokenBlacklist.is_token_revoked(jti, user_id):
            raise TokenRevokedError()

        # Verify required claims
        required_claims = ["sub", "email", "exp", "iat", "jti"]
        for claim in required_claims:
            if claim not in payload:
                raise TokenInvalidError(f"Missing required claim: {claim}")

        logger.debug(f"Token verified for user {user_id}")
        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("Token verification failed: expired")
        raise TokenExpiredError()
    except jwt.JWTClaimsError as e:
        logger.warning(f"Token verification failed: claims error - {e}")
        raise TokenInvalidError("Invalid token claims")
    except jwt.JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        raise TokenInvalidError("Invalid token")
    except ValueError as e:
        logger.warning(f"Token verification failed: {e}")
        raise TokenInvalidError("Invalid token format")


def get_token_payload(token: str) -> TokenPayload:
    """Extract validated user data from JWT token

    Args:
        token: JWT token string

    Returns:
        TokenPayload object with user data

    Raises:
        TokenInvalidError: If token is invalid
        TokenExpiredError: If token has expired
        TokenRevokedError: If token has been revoked
    """
    payload = verify_token(token)

    return TokenPayload(
        user_id=int(payload["sub"]),
        external_id=payload["external_id"],
        email=payload["email"],
        roles=payload.get("roles", []),
        issued_at=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
        expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        token_type=payload["type"],
        jti=payload["jti"],
    )


def is_token_expired(token: str) -> bool:
    """Check if token is expired without raising exception

    Args:
        token: JWT token string

    Returns:
        True if token is expired, False otherwise
    """
    try:
        verify_token(token)
        return False
    except TokenExpiredError:
        return True
    except (TokenInvalidError, TokenRevokedError):
        # Invalid or revoked tokens are considered "expired" for this check
        return True


def revoke_token(token: str) -> None:
    """Revoke a specific JWT token

    Args:
        token: JWT token string to revoke

    Raises:
        TokenInvalidError: If token is invalid
    """
    try:
        payload = verify_token(token)
        jti = payload.get("jti")

        if jti:
            TokenBlacklist.add_token(jti)
            logger.info(f"Token revoked: {jti}")
        else:
            raise TokenInvalidError("Token missing JTI for revocation")

    except (TokenExpiredError, TokenRevokedError):
        # Already expired/revoked tokens don't need to be revoked again
        pass


def revoke_all_user_tokens(user_id: int) -> None:
    """Revoke all tokens for a specific user

    Args:
        user_id: User database ID
    """
    TokenBlacklist.add_user_tokens(user_id)


def generate_password_reset_token(user_id: int, email: str) -> str:
    """Generate secure token for password reset

    Args:
        user_id: User database ID
        email: User email address

    Returns:
        Secure password reset token
    """
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=1)  # Short-lived for security

    claims = {
        "sub": str(user_id),
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "iss": JWTConfig.get_issuer(),
        "aud": JWTConfig.get_audience(),
        "type": "password_reset",
        "jti": generate_jti(),
    }

    return jwt.encode(claims, JWTConfig.get_secret_key(), algorithm=JWTConfig.get_algorithm())


def verify_password_reset_token(token: str) -> Dict[str, Any]:
    """Verify password reset token

    Args:
        token: Password reset token

    Returns:
        Token payload with user information

    Raises:
        TokenInvalidError: If token is invalid
        TokenExpiredError: If token has expired
    """
    return verify_token(token, token_type="password_reset")


class JWTAuthenticator:
    """Main JWT authentication class with comprehensive token management"""

    def __init__(self):
        self.config = JWTConfig()

    def create_user_tokens(
        self, user_id: int, external_id: str, email: str, roles: Optional[list[str]] = None
    ) -> Dict[str, str]:
        """Create both access and refresh tokens for user

        Args:
            user_id: User database ID
            external_id: External user identifier
            email: User email address
            roles: User roles/permissions

        Returns:
            Dictionary with access_token and refresh_token
        """
        access_token = create_access_token(
            user_id=user_id, external_id=external_id, email=email, roles=roles
        )

        refresh_token = create_refresh_token(user_id=user_id, external_id=external_id, email=email)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def refresh_access_token(self, refresh_token: str) -> str:
        """Create new access token from valid refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access token

        Raises:
            TokenInvalidError: If refresh token is invalid
            TokenExpiredError: If refresh token has expired
            TokenRevokedError: If refresh token has been revoked
        """
        payload = verify_token(refresh_token, token_type="refresh")

        return create_access_token(
            user_id=int(payload["sub"]),
            external_id=payload["external_id"],
            email=payload["email"],
            roles=payload.get("roles", []),
        )

    def logout_user(self, access_token: str, refresh_token: Optional[str] = None) -> None:
        """Logout user by revoking tokens

        Args:
            access_token: User's access token
            refresh_token: User's refresh token (optional)
        """
        try:
            revoke_token(access_token)
            if refresh_token:
                revoke_token(refresh_token)
        except (TokenInvalidError, TokenExpiredError):
            # Invalid/expired tokens don't need explicit revocation
            pass

    def logout_all_user_sessions(self, user_id: int) -> None:
        """Logout user from all sessions by blacklisting all their tokens

        Args:
            user_id: User database ID
        """
        revoke_all_user_tokens(user_id)

    def validate_token_claims(self, payload: Dict[str, Any]) -> bool:
        """Validate token payload has required claims and format

        Args:
            payload: Decoded JWT payload

        Returns:
            True if valid, False otherwise
        """
        required_claims = ["sub", "email", "exp", "iat", "iss", "aud", "jti"]

        for claim in required_claims:
            if claim not in payload:
                return False

        # Validate issuer and audience
        if payload.get("iss") != JWTConfig.get_issuer():
            return False
        if payload.get("aud") != JWTConfig.get_audience():
            return False

        # Validate user_id format
        try:
            int(payload["sub"])
        except (ValueError, TypeError):
            return False

        return True

    def get_token_info(self, token: str) -> Dict[str, Any]:
        """Get token information without full validation

        Args:
            token: JWT token string

        Returns:
            Dictionary with token information
        """
        try:
            # Decode without verification for inspection
            unverified_payload = jwt.get_unverified_claims(token)

            return {
                "user_id": int(unverified_payload.get("sub", 0)),
                "email": unverified_payload.get("email"),
                "token_type": unverified_payload.get("type"),
                "issued_at": datetime.fromtimestamp(
                    unverified_payload.get("iat", 0), tz=timezone.utc
                ),
                "expires_at": datetime.fromtimestamp(
                    unverified_payload.get("exp", 0), tz=timezone.utc
                ),
                "jti": unverified_payload.get("jti"),
            }
        except Exception as e:
            logger.error(f"Failed to extract token info: {e}")
            return {}


# Global authenticator instance
jwt_auth = JWTAuthenticator()


# Convenience functions for backward compatibility
def create_token_pair(
    user_id: int, external_id: str, email: str, roles: Optional[list[str]] = None
) -> Dict[str, str]:
    """Create access and refresh token pair for user"""
    return jwt_auth.create_user_tokens(user_id, external_id, email, roles)


def refresh_token(refresh_token: str) -> str:
    """Refresh access token using refresh token"""
    return jwt_auth.refresh_access_token(refresh_token)
