from sqlalchemy.orm import Session
from app.models import AgentLog, GuardrailEvent
from typing import Optional, Dict, Any
from datetime import datetime, timezone

def log_agent_decision(
    db: Session,
    session_id: str,
    agent_name: str,
    action: str,
    ticket_id: Optional[str] = None,
    reasoning: Optional[str] = None,
    tool_calls: Optional[Dict[str, Any]] = None,
    confidence_score: Optional[float] = None,
    latency_ms: Optional[int] = None,
    llm_model: Optional[str] = None,
    token_usage: Optional[Dict[str, Any]] = None
) -> AgentLog:
    """Logs an agent decision to the database."""
    log_entry = AgentLog(
        session_id=session_id,
        ticket_id=ticket_id,
        agent_name=agent_name,
        action=action,
        reasoning=reasoning,
        tool_calls=tool_calls,
        confidence_score=confidence_score,
        latency_ms=latency_ms,
        llm_model=llm_model,
        token_usage=token_usage,
        created_at=datetime.now(timezone.utc)
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry

def log_guardrail_event(
    db: Session,
    session_id: str,
    rule_name: str,
    triggered: bool,
    severity: str = "info",
    payload: Optional[Dict[str, Any]] = None,
    action_taken: Optional[str] = None
) -> GuardrailEvent:
    """Logs a guardrail event to the database."""
    event = GuardrailEvent(
        session_id=session_id,
        rule_name=rule_name,
        triggered=triggered,
        severity=severity,
        payload=payload,
        action_taken=action_taken,
        created_at=datetime.now(timezone.utc)
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
