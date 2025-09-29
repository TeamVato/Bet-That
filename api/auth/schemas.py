"""Pydantic schemas for JWT authentication endpoints

Defines request/response models for authentication operations including
login, registration, token refresh, password reset, and email verification.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, SecretStr, validator

from ..models import UserStatus


class LoginRequest(BaseModel):
    """User login request"""

    email: EmailStr = Field(..., description="User email address")
    password: SecretStr = Field(..., description="User password")
    remember_me: bool = Field(False, description="Extend session duration")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!",
                "remember_me": False,
            }
        }


class LoginResponse(BaseModel):
    """User login response with tokens"""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")
    csrf_token: Optional[str] = Field(None, description="CSRF protection token")
    user: Dict[str, Any] = Field(..., description="User information")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 900,
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "name": "John Doe",
                    "status": "active",
                },
            }
        }


class RefreshTokenRequest(BaseModel):
    """Token refresh request"""

    refresh_token: str = Field(..., description="Valid refresh token")
    rotate_refresh_token: bool = Field(False, description="Generate new refresh token")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "rotate_refresh_token": False,
            }
        }


class RefreshTokenResponse(BaseModel):
    """Token refresh response"""

    access_token: str = Field(..., description="New JWT access token")
    refresh_token: str = Field(..., description="Refresh token (new if rotated)")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")


class UserRegisterRequest(BaseModel):
    """User registration request"""

    email: EmailStr = Field(..., description="User email address")
    password: SecretStr = Field(..., min_length=8, description="User password")
    name: Optional[str] = Field(None, max_length=255, description="Full name")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    timezone: Optional[str] = Field("UTC", description="User timezone")

    @validator("password")
    def validate_password_not_empty(cls, v):
        if isinstance(v, SecretStr):
            password = v.get_secret_value()
        else:
            password = v
        if not password or len(password.strip()) == 0:
            raise ValueError("Password cannot be empty")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "newuser@example.com",
                "password": "SecurePassword123!",
                "name": "John Doe",
                "first_name": "John",
                "last_name": "Doe",
                "timezone": "America/New_York",
            }
        }


class UserRegisterResponse(BaseModel):
    """User registration response"""

    id: int = Field(..., description="User database ID")
    email: str = Field(..., description="User email address")
    name: Optional[str] = Field(None, description="User name")
    status: UserStatus = Field(..., description="Account status")
    email_verified: bool = Field(..., description="Email verification status")
    verification_required: bool = Field(..., description="Whether email verification is required")
    message: str = Field(..., description="Registration status message")
    created_at: datetime = Field(..., description="Account creation timestamp")


class PasswordResetRequest(BaseModel):
    """Password reset request"""

    email: EmailStr = Field(..., description="User email address")

    class Config:
        json_schema_extra = {"example": {"email": "user@example.com"}}


class PasswordResetConfirmRequest(BaseModel):
    """Password reset confirmation request"""

    token: str = Field(..., description="Password reset token from email")
    new_password: SecretStr = Field(..., min_length=8, description="New password")

    @validator("new_password")
    def validate_password_not_empty(cls, v):
        if isinstance(v, SecretStr):
            password = v.get_secret_value()
        else:
            password = v
        if not password or len(password.strip()) == 0:
            raise ValueError("Password cannot be empty")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "token": "secure-reset-token-from-email",
                "new_password": "NewSecurePassword123!",
            }
        }


class PasswordChangeRequest(BaseModel):
    """Password change request (authenticated)"""

    current_password: SecretStr = Field(..., description="Current password")
    new_password: SecretStr = Field(..., min_length=8, description="New password")
    logout_other_sessions: bool = Field(False, description="Logout from other sessions")

    @validator("new_password")
    def validate_passwords_different(cls, v, values):
        current_password = values.get("current_password")
        if current_password and isinstance(current_password, SecretStr):
            current_pass = current_password.get_secret_value()
            new_pass = v.get_secret_value() if isinstance(v, SecretStr) else v
            if current_pass == new_pass:
                raise ValueError("New password must be different from current password")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "CurrentPassword123!",
                "new_password": "NewSecurePassword123!",
                "logout_other_sessions": False,
            }
        }


class EmailVerificationRequest(BaseModel):
    """Email verification request"""

    token: str = Field(..., description="Email verification token")
    user_id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="Email address to verify")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "email-verification-token-from-email",
                "user_id": 1,
                "email": "user@example.com",
            }
        }


class LogoutResponse(BaseModel):
    """Logout response"""

    message: str = Field(..., description="Logout status message")
    logged_out_at: datetime = Field(..., description="Logout timestamp")


class TokenValidationResponse(BaseModel):
    """Token validation response"""

    valid: bool = Field(..., description="Whether token is valid")
    user_id: Optional[int] = Field(None, description="User ID from token")
    email: Optional[str] = Field(None, description="Email from token")
    token_type: Optional[str] = Field(None, description="Token type")
    expires_at: Optional[int] = Field(None, description="Expiration timestamp")
    issued_at: Optional[int] = Field(None, description="Issued timestamp")
    roles: List[str] = Field(default_factory=list, description="User roles")


class PasswordStrengthResponse(BaseModel):
    """Password strength validation response"""

    is_valid: bool = Field(..., description="Whether password meets requirements")
    score: float = Field(..., description="Password strength score (0-100)")
    strength: str = Field(..., description="Strength label (weak/fair/good/strong/very_strong)")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    checks: Dict[str, bool] = Field(
        default_factory=dict, description="Individual requirement checks"
    )


class SecurityEventLog(BaseModel):
    """Security event log entry"""

    event_type: str = Field(..., description="Event type (login, logout, password_change, etc.)")
    user_id: Optional[int] = Field(None, description="User ID if applicable")
    ip_address: str = Field(..., description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    success: bool = Field(..., description="Whether event was successful")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional event details")
    timestamp: datetime = Field(..., description="Event timestamp")


class CSRFTokenResponse(BaseModel):
    """CSRF token response"""

    csrf_token: str = Field(..., description="CSRF protection token")
    expires_in: int = Field(..., description="Token expiration in seconds")


class PasswordChangeRequest(BaseModel):
    """Password change request (authenticated)"""

    current_password: SecretStr = Field(..., description="Current password")
    new_password: SecretStr = Field(..., min_length=8, description="New password")
    logout_other_sessions: bool = Field(False, description="Logout from other sessions")

    @validator("new_password")
    def validate_passwords_different(cls, v, values):
        current_password = values.get("current_password")
        if current_password and isinstance(current_password, SecretStr):
            current_pass = current_password.get_secret_value()
            new_pass = v.get_secret_value() if isinstance(v, SecretStr) else v
            if current_pass == new_pass:
                raise ValueError("New password must be different from current password")
        return v


class EmailVerificationRequest(BaseModel):
    """Email verification request"""

    token: str = Field(..., description="Email verification token")
    user_id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="Email address to verify")


class LogoutResponse(BaseModel):
    """Logout response"""

    message: str = Field(..., description="Logout status message")
    logged_out_at: datetime = Field(..., description="Logout timestamp")
