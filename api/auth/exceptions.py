"""Authentication-specific exceptions for the Bet-That API"""

from typing import Optional

from fastapi import HTTPException, status


class AuthenticationError(HTTPException):
    """Base authentication error"""

    def __init__(self, detail: str = "Authentication failed", headers: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers or {"WWW-Authenticate": "Bearer"},
        )


class TokenExpiredError(AuthenticationError):
    """Raised when a JWT token has expired"""

    def __init__(self, detail: str = "Token has expired"):
        super().__init__(detail=detail)


class TokenInvalidError(AuthenticationError):
    """Raised when a JWT token is invalid or malformed"""

    def __init__(self, detail: str = "Invalid token"):
        super().__init__(detail=detail)


class TokenRevokedError(AuthenticationError):
    """Raised when a JWT token has been revoked/blacklisted"""

    def __init__(self, detail: str = "Token has been revoked"):
        super().__init__(detail=detail)


class PasswordTooWeakError(HTTPException):
    """Raised when password doesn't meet security requirements"""

    def __init__(self, detail: str = "Password does not meet security requirements"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class RateLimitExceededError(HTTPException):
    """Raised when rate limit is exceeded for authentication endpoints"""

    def __init__(self, detail: str = "Too many authentication attempts", retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": str(retry_after)},
        )


class UserNotFoundError(HTTPException):
    """Raised when user is not found"""

    def __init__(self, detail: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UserInactiveError(AuthenticationError):
    """Raised when user account is inactive"""

    def __init__(self, detail: str = "User account is inactive"):
        super().__init__(detail=detail)


class EmailNotVerifiedError(AuthenticationError):
    """Raised when user email is not verified"""

    def __init__(self, detail: str = "Email address not verified"):
        super().__init__(detail=detail)


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid"""

    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(detail=detail)


class RefreshTokenError(AuthenticationError):
    """Raised when refresh token operation fails"""

    def __init__(self, detail: str = "Invalid refresh token"):
        super().__init__(detail=detail)
