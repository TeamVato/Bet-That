"""User-related schemas for API request/response validation"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from ..models import UserStatus


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserRegistrationRequest(BaseModel):
    external_id: str = Field(..., description="External user ID from Supabase")
    email: EmailStr = Field(..., description="User email address")
    name: Optional[str] = Field(None, description="User display name")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    timezone: str = Field("UTC", description="User timezone")
    phone: Optional[str] = Field(None, description="Phone number")


class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="Display name")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    timezone: Optional[str] = Field(None, description="Timezone")
    phone: Optional[str] = Field(None, description="Phone number")
    max_bet_size: Optional[Decimal] = Field(None, description="Maximum bet size")
    daily_bet_limit: Optional[Decimal] = Field(None, description="Daily betting limit")
    monthly_bet_limit: Optional[Decimal] = Field(None, description="Monthly betting limit")
    risk_tolerance: Optional[str] = Field(None, description="Risk tolerance level")
    auto_kelly_sizing: Optional[bool] = Field(None, description="Enable auto Kelly sizing")
    max_kelly_fraction: Optional[float] = Field(None, description="Maximum Kelly fraction")
    preferred_sports: Optional[List[str]] = Field(None, description="Preferred sports")
    notification_preferences: Optional[Dict[str, Any]] = Field(
        None, description="Notification settings"
    )
    ui_preferences: Optional[Dict[str, Any]] = Field(None, description="UI preferences")


class UserResponse(BaseSchema):
    id: int
    external_id: str
    email: str
    name: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    timezone: str
    phone: Optional[str]
    status: UserStatus
    is_active: bool
    is_verified: bool
    verification_level: str
    max_bet_size: Decimal
    daily_bet_limit: Decimal
    monthly_bet_limit: Decimal
    risk_tolerance: str
    auto_kelly_sizing: bool
    max_kelly_fraction: float
    preferred_sports: Optional[List[str]]
    notification_preferences: Optional[Dict[str, Any]]
    ui_preferences: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
    last_activity_at: Optional[datetime]


class UserRegistrationResponse(BaseSchema):
    id: int
    external_id: str
    email: str
    name: Optional[str]
    status: UserStatus
    created_at: datetime
    is_active: bool
