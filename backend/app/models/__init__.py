import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text,
    ForeignKey, Numeric, Integer, JSON, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.session import Base
import enum


def utcnow():
    return datetime.now(timezone.utc)


def new_uuid():
    return str(uuid.uuid4())


# ─── Enums ────────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    customer = "customer"
    admin = "admin"


class OrderStatus(str, enum.Enum):
    pending = "pending"
    shipped = "shipped"
    delivered = "delivered"
    delayed = "delayed"
    cancelled = "cancelled"


class RefundStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    refunded = "refunded"


class TicketStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    escalated = "escalated"
    closed = "closed"


class TicketPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class EscalationPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


# ─── User ─────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.customer)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    customer = relationship("Customer", back_populates="user", uselist=False)
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    otp_verifications = relationship("OTPVerification", back_populates="user", cascade="all, delete-orphan")
    password_resets = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")


# ─── Customer ─────────────────────────────────────────────────────────────────

class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="customer")
    orders = relationship("Order", back_populates="customer")
    tickets = relationship("Ticket", back_populates="customer")


# ─── Order ────────────────────────────────────────────────────────────────────

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    customer_id = Column(UUID(as_uuid=False), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(SAEnum(OrderStatus), nullable=False, default=OrderStatus.pending)
    total_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="USD")
    product_details = Column(JSON, nullable=False)       # [{name, qty, price, sku}]
    shipping_address = Column(Text, nullable=True)
    tracking_number = Column(String(100), nullable=True)
    estimated_delivery = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    is_refund_eligible = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    customer = relationship("Customer", back_populates="orders")
    refunds = relationship("Refund", back_populates="order")


# ─── Refund ───────────────────────────────────────────────────────────────────

class Refund(Base):
    __tablename__ = "refunds"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    order_id = Column(UUID(as_uuid=False), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(SAEnum(RefundStatus), nullable=False, default=RefundStatus.pending)
    amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(Text, nullable=False)
    rejection_reason = Column(Text, nullable=True)
    approved_by = Column(UUID(as_uuid=False), nullable=True)   # admin user_id
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    order = relationship("Order", back_populates="refunds")


# ─── Ticket ───────────────────────────────────────────────────────────────────

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    customer_id = Column(UUID(as_uuid=False), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_number = Column(String(50), unique=True, nullable=False, index=True)
    subject = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SAEnum(TicketStatus), nullable=False, default=TicketStatus.open)
    priority = Column(SAEnum(TicketPriority), nullable=False, default=TicketPriority.medium)
    assigned_agent = Column(String(100), nullable=True)    # agent name from Phase 2
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    customer = relationship("Customer", back_populates="tickets")
    chat_history = relationship("ChatHistory", back_populates="ticket", cascade="all, delete-orphan")
    escalation_logs = relationship("EscalationLog", back_populates="ticket")


# ─── ChatHistory ──────────────────────────────────────────────────────────────

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    ticket_id = Column(UUID(as_uuid=False), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)              # "user" | "assistant" | "system"
    content = Column(Text, nullable=False)
    agent_name = Column(String(100), nullable=True)        # Which agent responded (Phase 2)
    confidence_score = Column(Numeric(4, 3), nullable=True)  # 0.000–1.000 (Phase 3)
    sentiment = Column(String(20), nullable=True)          # Phase 4
    metadata = Column(JSON, nullable=True)                 # reasoning, tool calls, etc.
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    ticket = relationship("Ticket", back_populates="chat_history")


# ─── FAQ Documents ────────────────────────────────────────────────────────────

class FAQDocument(Base):
    __tablename__ = "faq_documents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    category = Column(String(100), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    embedding_ref = Column(String(255), nullable=True)    # FAISS vector ID (Phase 3)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


# ─── Agent Logs ───────────────────────────────────────────────────────────────

class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    session_id = Column(String(100), nullable=False, index=True)
    ticket_id = Column(UUID(as_uuid=False), nullable=True, index=True)
    agent_name = Column(String(100), nullable=False)       # orchestrator, order_agent, etc.
    action = Column(String(255), nullable=False)
    reasoning = Column(Text, nullable=True)                # LLM reasoning text
    tool_calls = Column(JSON, nullable=True)               # [{tool, input, output}]
    confidence_score = Column(Numeric(4, 3), nullable=True)
    latency_ms = Column(Integer, nullable=True)
    llm_model = Column(String(100), nullable=True)         # gemini-pro, gpt-4, etc.
    token_usage = Column(JSON, nullable=True)              # {prompt, completion, total}
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


# ─── Guardrail Events ─────────────────────────────────────────────────────────

class GuardrailEvent(Base):
    __tablename__ = "guardrail_events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    session_id = Column(String(100), nullable=False, index=True)
    rule_name = Column(String(100), nullable=False)        # e.g. "refund_threshold", "pii_filter"
    triggered = Column(Boolean, nullable=False)
    severity = Column(String(20), nullable=True)           # info, warning, critical
    payload = Column(JSON, nullable=True)                  # input that triggered guard
    action_taken = Column(String(255), nullable=True)      # blocked, escalated, warned
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


# ─── Escalation Logs ──────────────────────────────────────────────────────────

class EscalationLog(Base):
    __tablename__ = "escalation_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    ticket_id = Column(UUID(as_uuid=False), ForeignKey("tickets.id", ondelete="SET NULL"), nullable=True, index=True)
    session_id = Column(String(100), nullable=False)
    reason = Column(Text, nullable=False)
    priority = Column(SAEnum(EscalationPriority), nullable=False, default=EscalationPriority.medium)
    summary = Column(Text, nullable=True)                  # AI-generated summary (Phase 4)
    sentiment_score = Column(Numeric(4, 3), nullable=True) # Phase 4
    resolved = Column(Boolean, default=False)
    resolved_by = Column(UUID(as_uuid=False), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    ticket = relationship("Ticket", back_populates="escalation_logs")


# ─── Analytics Metrics ────────────────────────────────────────────────────────

class AnalyticsMetric(Base):
    __tablename__ = "analytics_metrics"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Numeric(20, 4), nullable=False)
    dimension = Column(String(100), nullable=True)         # e.g. agent_name, date, category
    recorded_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


# ─── User Sessions ────────────────────────────────────────────────────────────

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_token = Column(String(512), unique=True, nullable=False)
    user_agent = Column(String(512), nullable=True)
    ip_address = Column(String(50), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User", back_populates="sessions")


# ─── OTP Verification ─────────────────────────────────────────────────────────

class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    otp_code = Column(String(10), nullable=False)
    purpose = Column(String(50), nullable=False)           # "email_verify" | "login" | "password_reset"
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User", back_populates="otp_verifications")


# ─── Password Reset ───────────────────────────────────────────────────────────

class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(512), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User", back_populates="password_resets")
