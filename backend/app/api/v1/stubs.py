from fastapi import APIRouter, Depends
from app.middleware.auth import require_verified, require_admin
from app.models import User
from app.schemas import ChatMessageRequest, AnalyticsSummaryResponse

# ─── Chat Router (Phase 2 stub) ───────────────────────────────────────────────
chat_router = APIRouter(prefix="/chat", tags=["Chat"])


@chat_router.post("/message")
def send_message(
    payload: ChatMessageRequest,
    current_user: User = Depends(require_verified),
):
    """
    Phase 2: This endpoint will invoke the LangGraph orchestrator.
    Orchestrator will route to: OrderAgent | RefundAgent | FAQAgent | HumanEscalationAgent
    """
    return {
        "status": "phase_2_pending",
        "message": "AI agent system coming in Phase 2.",
        "session_id": payload.session_id,
        "echo": payload.message,
    }


# ─── Analytics Router (Phase 4 stub) ─────────────────────────────────────────
analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])


@analytics_router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(admin: User = Depends(require_admin)):
    """
    Phase 4: Returns real-time analytics from DB + LangSmith metrics.
    """
    return AnalyticsSummaryResponse(
        total_tickets=0,
        open_tickets=0,
        resolved_tickets=0,
        escalated_tickets=0,
        avg_response_time_minutes=0.0,
        customer_satisfaction_score=None,
        top_agents=[],
        guardrail_triggers_today=0,
    )
