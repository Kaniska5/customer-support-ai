from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Ticket, TicketStatus, AgentLog, ChatHistory


def get_analytics_summary(db: Session) -> dict:
    """
    Computes real-time observability metrics from the DB:
    - Total tickets
    - Open/Resolved/Escalated tickets
    - Top agents invoked
    - Average AI confidence score
    """
    now = datetime.now(timezone.utc)
    twenty_four_hours_ago = now - timedelta(days=1)

    # Ticket metrics
    total_tickets = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(Ticket.status == TicketStatus.open).count()
    resolved_tickets = db.query(Ticket).filter(Ticket.status == TicketStatus.resolved).count()
    escalated_tickets = db.query(Ticket).filter(Ticket.status == TicketStatus.escalated).count()

    # Agent invocations (Top Agents)
    top_agents_query = (
        db.query(AgentLog.agent_name, func.count(AgentLog.id).label("count"))
        .filter(AgentLog.agent_name != "orchestrator")
        .filter(AgentLog.agent_name != "unknown")
        .group_by(AgentLog.agent_name)
        .order_by(func.count(AgentLog.id).desc())
        .limit(5)
        .all()
    )
    top_agents = [{"name": row[0], "invocations": row[1]} for row in top_agents_query]

    # AI Confidence average over the last 24 hours
    avg_confidence_query = (
        db.query(func.avg(ChatHistory.confidence_score))
        .filter(ChatHistory.role == "assistant")
        .filter(ChatHistory.created_at >= twenty_four_hours_ago)
        .scalar()
    )
    avg_confidence = float(avg_confidence_query) if avg_confidence_query is not None else 0.0

    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "resolved_tickets": resolved_tickets,
        "escalated_tickets": escalated_tickets,
        "avg_confidence_score": round(avg_confidence, 2),
        "top_agents": top_agents,
    }
