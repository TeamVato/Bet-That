"""Transaction-related schemas for API request/response validation"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ..models import TransactionStatus, TransactionType


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TransactionCreateRequest(BaseModel):
    user_id: int = Field(description="User ID")
    bet_id: Optional[int] = Field(default=None, description="Associated bet ID")
    amount: Decimal = Field(description="Transaction amount")
    currency: str = Field(default="USD", description="Currency code")
    transaction_type: TransactionType = Field(description="Transaction type")
    sportsbook_id: Optional[str] = Field(default=None, description="Sportsbook identifier")
    sportsbook_name: Optional[str] = Field(default=None, description="Sportsbook name")
    external_transaction_id: Optional[str] = Field(default=None, description="External transaction ID")
    description: Optional[str] = Field(default=None, description="Transaction description")
    reference: Optional[str] = Field(default=None, description="Reference number")
    category: Optional[str] = Field(default=None, description="Transaction category")
    fee_amount: Optional[Decimal] = Field(default=None, description="Fee amount")
    net_amount: Optional[Decimal] = Field(default=None, description="Net amount after fees")


class TransactionUpdateRequest(BaseModel):
    status: Optional[TransactionStatus] = Field(default=None, description="Transaction status")
    description: Optional[str] = Field(default=None, description="Updated description")
    reference: Optional[str] = Field(default=None, description="Updated reference")
    category: Optional[str] = Field(default=None, description="Updated category")
    fee_amount: Optional[Decimal] = Field(default=None, description="Updated fee amount")
    net_amount: Optional[Decimal] = Field(default=None, description="Updated net amount")


class TransactionResponse(BaseSchema):
    id: int
    user_id: int
    bet_id: Optional[int]
    amount: Decimal
    currency: str
    transaction_type: TransactionType
    status: TransactionStatus
    sportsbook_id: Optional[str]
    sportsbook_name: Optional[str]
    external_transaction_id: Optional[str]
    description: Optional[str]
    reference: Optional[str]
    category: Optional[str]
    fee_amount: Optional[Decimal]
    net_amount: Optional[Decimal]
    processed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int
    page: int
    per_page: int
