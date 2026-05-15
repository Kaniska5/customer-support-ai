from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Ticket, TicketStatus, AgentLog, GuardrailEvent, ChatHistory
from typing import Dict, Any

class KPIEngine:
    """Calculates enterprise success metrics (KPIs) for the platform."""

    @staticmethod
    def calculate_auto_resolution_rate(db: Session) -> float:
        """Percentage of tickets resolved without human escalation."""
        total = db.query(Ticket).count()
        if total == 0:
            return 0.0
        resolved = db.query(Ticket).filter(Ticket.status == TicketStatus.resolved).count()
        return round((resolved / total) * 100, 2)

    @staticmethod
    def calculate_escalation_rate(db: Session) -> float:
        """Percentage of tickets escalated to humans."""
        total = db.query(Ticket).count()
        if total == 0:
            return 0.0
        escalated = db.query(Ticket).filter(Ticket.status == TicketStatus.escalated).count()
        return round((escalated / total) * 100, 2)

    @staticmethod
    def calculate_guardrail_violation_rate(db: Session) -> float:
        """Percentage of sessions that triggered a guardrail."""
        total_sessions = db.query(func.count(func.distinct(AgentLog.session_id))).scalar() or 1
        sessions_with_violations = db.query(func.count(func.distinct(GuardrailEvent.session_id))).scalar() or 0
        return round((sessions_with_violations / total_sessions) * 100, 2)

    @staticmethod
    def calculate_avg_response_time_seconds(db: Session) -> float:
        """Average latency for agent responses."""
        avg_latency = db.query(func.avg(AgentLog.latency_ms)).filter(AgentLog.latency_ms.isnot(None)).scalar() or 0.0
        return round(float(avg_latency) / 1000.0, 2)

    @staticmethod
    def get_all_kpis(db: Session) -> Dict[str, Any]:
        """Returns all KPIs."""
        return {
            "auto_resolution_rate": KPIEngine.calculate_auto_resolution_rate(db),
            "escalation_rate": KPIEngine.calculate_escalation_rate(db),
            "guardrail_violation_rate": KPIEngine.calculate_guardrail_violation_rate(db),
            "avg_response_time_seconds": KPIEngine.calculate_avg_response_time_seconds(db)
        }

kpi_engine = KPIEngine()
