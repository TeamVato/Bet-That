"""JWT Authentication package for Bet-That API

This package provides comprehensive JWT-based authentication including:
- Token generation and validation
- Password hashing and verification
- Security utilities and blacklisting
- Rate limiting and CSRF protection
"""

from .exceptions import (
    AuthenticationError,
    PasswordTooWeakError,
    RateLimitExceededError,
    TokenExpiredError,
    TokenInvalidError,
    TokenRevokedError,
)
from .jwt_auth import (
    JWTAuthenticator,
    create_access_token,
    create_refresh_token,
    get_token_payload,
    is_token_expired,
    revoke_token,
    verify_token,
)
from .password_manager import (
    PasswordManager,
    generate_salt,
    hash_password,
    validate_password_strength,
    verify_password,
)
from .security_utils import (
    SecurityManager,
    generate_csrf_token,
    generate_secure_token,
    sanitize_auth_input,
    verify_csrf_token,
)

__all__ = [
    # JWT functions
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "get_token_payload",
    "is_token_expired",
    "revoke_token",
    "JWTAuthenticator",
    # Password functions
    "hash_password",
    "verify_password",
    "generate_salt",
    "validate_password_strength",
    "PasswordManager",
    # Security utilities
    "generate_csrf_token",
    "verify_csrf_token",
    "generate_secure_token",
    "sanitize_auth_input",
    "SecurityManager",
    # Exceptions
    "AuthenticationError",
    "TokenExpiredError",
    "TokenInvalidError",
    "TokenRevokedError",
    "PasswordTooWeakError",
    "RateLimitExceededError",
]
