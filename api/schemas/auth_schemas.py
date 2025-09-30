"""Enhanced authentication schemas for user registration and login

Provides comprehensive request/response models for authentication operations
with username support, validation, and proper error handling.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserRegistrationRequest(BaseModel):
    """Enhanced user registration request with username support"""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        pattern="^[a-zA-Z0-9_]+$",
        description="Unique username (3-30 chars, alphanumeric + underscore)",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (8-100 characters with complexity requirements)",
    )
    confirm_password: str = Field(..., description="Password confirmation")
    first_name: str = Field(..., max_length=50, description="First name")
    last_name: str = Field(..., max_length=50, description="Last name")
    date_of_birth: Optional[date] = Field(None, description="Date of birth (must be 18+)")
    phone_number: Optional[str] = Field(
        None, pattern=r"^\+?[1-9]\d{1,14}$", description="Phone number in international format"
    )
    timezone: str = Field("UTC", description="User timezone")

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("passwords do not match")
        return v

    @validator("username")
    def username_not_reserved(cls, v):
        # Check for reserved usernames
        reserved = {"admin", "api", "www", "root", "support", "help", "null", "undefined"}
        if v.lower() in reserved:
            raise ValueError("username is reserved")
        return v.lower()  # Store username in lowercase

    @validator("date_of_birth")
    def validate_age(cls, v):
        if v and (datetime.now().date() - v).days < 6570:  # 18 years in days
            raise ValueError("must be at least 18 years old")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe123",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1990-01-01",
                "phone_number": "+1234567890",
                "timezone": "America/New_York",
            }
        }


class UserLoginRequest(BaseModel):
    """User login request supporting email or username"""

    email_or_username: str = Field(..., description="Email address or username for login")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(False, description="Extend session duration")

    class Config:
        json_schema_extra = {
            "example": {
                "email_or_username": "johndoe123",
                "password": "SecurePass123!",
                "remember_me": False,
            }
        }


class UserResponse(BaseModel):
    """User response model for public user data"""

    id: int
    email: str
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    name: Optional[str]  # Computed full name
    is_active: bool
    is_verified: bool
    email_verified: bool
    status: str
    timezone: str
    created_at: datetime
    last_login_at: Optional[datetime]
    verification_level: str

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Authentication response with tokens and user data"""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")
    user: UserResponse = Field(..., description="User information")

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
                    "username": "johndoe123",
                    "first_name": "John",
                    "last_name": "Doe",
                    "is_active": True,
                    "is_verified": True,
                },
            }
        }


class RegistrationResponse(BaseModel):
    """User registration response"""

    message: str = Field(..., description="Registration status message")
    user: UserResponse = Field(..., description="Created user information")
    verification_required: bool = Field(True, description="Whether email verification is required")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Registration successful. Please check your email to verify your account.",
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "username": "johndoe123",
                    "first_name": "John",
                    "last_name": "Doe",
                    "is_active": True,
                    "is_verified": False,
                },
                "verification_required": True,
            }
        }


class PasswordStrengthCheck(BaseModel):
    """Password strength validation response"""

    is_valid: bool = Field(..., description="Whether password meets requirements")
    score: float = Field(..., description="Password strength score (0-100)")
    strength: str = Field(..., description="Strength label")
    errors: list[str] = Field(default_factory=list, description="Validation errors")
    checks: dict[str, bool] = Field(default_factory=dict, description="Individual checks")


class UserProfileUpdate(BaseModel):
    """User profile update request"""

    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    timezone: Optional[str] = Field(None)

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "+1234567890",
                "timezone": "America/New_York",
            }
        }
