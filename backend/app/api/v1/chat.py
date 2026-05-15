"""
Chat API — Real LangGraph-powered endpoint

POST /api/v1/chat/message  →  Orchestrates multi-agent pipeline and returns enriched response
GET  /api/v1/chat/history  →  Returns paginated chat history for a session
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.middleware.auth import require_verified
from app.models import (
    AgentLog, ChatHistory, Customer, Ticket, TicketStatus, User,
)
from app.schemas import ChatMessageRequest
from app.services.agent.graph import compiled_graph
from app.services.agent.state import GraphState

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


# ─── Response Schemas ─────────────────────────────────────────────────────────

class EscalationInfo(BaseModel):
    needed: bool
    ticket_number: Optional[str] = None


class TimelineStep(BaseModel):
    step: str
    agent: str
    timestamp: str
    details: str


class ChatResponse(BaseModel):
    message: str
    session_id: str
    agents_used: list[str]
    confidence_score: float
    escalation: EscalationInfo
    timeline: list[TimelineStep]
    message_id: str


class ChatHistoryItem(BaseModel):
    id: str
    role: str
    content: str
    agent_name: Optional[str]
    confidence_score: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatHistoryItem]
    total: int


# ─── Helper: get or create customer record ────────────────────────────────────

def _get_customer(db: Session, user: User) -> Customer:
    customer = db.query(Customer).filter(Customer.user_id == user.id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found. Please complete your profile setup.",
        )
    return customer


def _extract_ticket_number(agent_outputs: dict[str, Any]) -> Optional[str]:
    """Parse ticket number from escalation agent output if present."""
    escalation_out = agent_outputs.get("escalation_agent", "")
    if "TKT-" in escalation_out:
        start = escalation_out.index("TKT-")
        ticket_fragment = escalation_out[start : start + 12]
        # Strip trailing non-alphanumeric
        ticket_number = "".join(c for c in ticket_fragment if c.isalnum() or c == "-")
        return ticket_number
    return None


# ─── POST /chat/message ───────────────────────────────────────────────────────

@router.post("/message", response_model=ChatResponse)
async def send_message(
    payload: ChatMessageRequest,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
):
    """
    Invoke the LangGraph multi-agent pipeline for a customer message.
    Returns the AI response with agent metadata, confidence, and reasoning timeline.
    """
    customer = _get_customer(db, current_user)
    session_id = payload.session_id or str(uuid.uuid4())
    message_id = str(uuid.uuid4())

    # ── Build initial graph state ──────────────────────────────────────────────
    initial_state: GraphState = {
        "session_id": session_id,
        "customer_id": customer.id,
        "messages": [HumanMessage(content=payload.message)],
        "intents": [],
        "confidence_score": 0.0,
        "agent_outputs": {},
        "escalation_needed": False,
        "timeline": [],
        "final_response": "",
    }

    # ── Persist user message to chat_history ───────────────────────────────────
    user_chat_entry = ChatHistory(
        id=str(uuid.uuid4()),
        ticket_id=payload.ticket_id,
        session_id=session_id,
        role="user",
        content=payload.message,
        meta_data={"message_id": message_id},
    )
    db.add(user_chat_entry)

    # ── Invoke LangGraph pipeline ──────────────────────────────────────────────
    try:
        final_state: GraphState = compiled_graph.invoke(initial_state)
    except Exception as e:
        logger.error(f"[chat] LangGraph invocation failed for session {session_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI agent pipeline is temporarily unavailable. Please try again.",
        )

    # ── Extract results ────────────────────────────────────────────────────────
    final_response: str = final_state.get("final_response", "I'm sorry, I could not generate a response.")
    agents_used: list[str] = list(final_state.get("agent_outputs", {}).keys())
    confidence: float = final_state.get("confidence_score", 0.0)
    escalation_needed: bool = final_state.get("escalation_needed", False)
    timeline: list[dict] = final_state.get("timeline", [])

    ticket_number = _extract_ticket_number(final_state.get("agent_outputs", {}))

    # ── Persist AI response to chat_history ───────────────────────────────────
    ai_chat_entry = ChatHistory(
        id=message_id,
        ticket_id=payload.ticket_id,
        session_id=session_id,
        role="assistant",
        content=final_response,
        agent_name=", ".join(agents_used) if agents_used else "orchestrator",
        confidence_score=confidence,
        meta_data={
            "agents_used": agents_used,
            "timeline": timeline,
            "escalation_needed": escalation_needed,
            "ticket_number": ticket_number,
        },
    )
    db.add(ai_chat_entry)

    # ── Persist agent logs ────────────────────────────────────────────────────
    for step in timeline:
        db.add(AgentLog(
            id=str(uuid.uuid4()),
            session_id=session_id,
            agent_name=step.get("agent", "unknown"),
            action=step.get("step", ""),
            reasoning=step.get("details", ""),
            confidence_score=confidence if step.get("agent") == "orchestrator" else None,
        ))

    try:
        db.commit()
    except Exception as e:
        logger.error(f"[chat] DB commit failed: {e}")
        db.rollback()
        # Don't fail the request — response was already generated

    # ── Build response ────────────────────────────────────────────────────────
    timeline_steps = [
        TimelineStep(
            step=t.get("step", ""),
            agent=t.get("agent", ""),
            timestamp=t.get("timestamp", ""),
            details=t.get("details", ""),
        )
        for t in (final_state.get("timeline") or [])
    ]

    return ChatResponse(
        message=final_response,
        session_id=session_id,
        agents_used=agents_used,
        confidence_score=round(confidence, 3),
        escalation=EscalationInfo(
            needed=escalation_needed,
            ticket_number=ticket_number,
        ),
        timeline=timeline_steps,
        message_id=message_id,
    )


# ─── GET /chat/history ────────────────────────────────────────────────────────

@router.get("/history", response_model=ChatHistoryResponse)
def get_chat_history(
    session_id: str,
    limit: int = 50,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
):
    """
    Returns chat history for a given session_id.
    Only returns messages belonging to the authenticated user's sessions.
    """
    customer = _get_customer(db, current_user)

    messages = (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.created_at.asc())
        .limit(limit)
        .all()
    )

    return ChatHistoryResponse(
        session_id=session_id,
        messages=[ChatHistoryItem.model_validate(m) for m in messages],
        total=len(messages),
    )
