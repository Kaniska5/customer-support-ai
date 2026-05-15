from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


# ─── Auth Schemas ─────────────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)
    purpose: str = Field(default="email_verify")


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        return v


# ─── Auth Responses ───────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserOut(BaseModel):
    id: str
    email: str
    role: str
    is_verified: bool
    full_name: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    user: UserOut
    tokens: TokenResponse


class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


# ─── Order Schemas ────────────────────────────────────────────────────────────

class ProductItem(BaseModel):
    name: str
    sku: str
    qty: int
    price: float


class OrderOut(BaseModel):
    id: str
    order_number: str
    status: str
    total_amount: float
    currency: str
    product_details: list[ProductItem]
    shipping_address: Optional[str]
    tracking_number: Optional[str]
    estimated_delivery: Optional[datetime]
    delivered_at: Optional[datetime]
    is_refund_eligible: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    orders: list[OrderOut]
    total: int
    page: int
    page_size: int


# ─── Ticket Schemas ───────────────────────────────────────────────────────────

class TicketCreateRequest(BaseModel):
    subject: str = Field(..., min_length=5, max_length=500)
    description: Optional[str] = None
    priority: Optional[str] = "medium"


class TicketOut(BaseModel):
    id: str
    ticket_number: str
    subject: str
    description: Optional[str]
    status: str
    priority: str
    assigned_agent: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    tickets: list[TicketOut]
    total: int


# ─── Chat Schemas (Phase 2 ready) ─────────────────────────────────────────────

class ChatMessageRequest(BaseModel):
    session_id: str
    ticket_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=4000)
    metadata: Optional[dict[str, Any]] = None


class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    agent_name: Optional[str]
    confidence_score: Optional[float]
    sentiment: Optional[str]
    metadata: Optional[dict[str, Any]]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Analytics Schemas (Phase 4 ready) ───────────────────────────────────────

class AnalyticsSummaryResponse(BaseModel):
    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    escalated_tickets: int
    avg_response_time_minutes: float
    customer_satisfaction_score: Optional[float]
    top_agents: list[dict[str, Any]]
    guardrail_triggers_today: int


# ─── Common ───────────────────────────────────────────────────────────────────

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
