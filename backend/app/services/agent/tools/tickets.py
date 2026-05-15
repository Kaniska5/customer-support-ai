from langchain_core.tools import tool
from app.database.session import SessionLocal
from app.models import (
    Ticket, EscalationLog, Customer, User,
    TicketStatus, TicketPriority, EscalationPriority,
)
from datetime import datetime, timezone
import uuid


def _generate_ticket_number() -> str:
    short = str(uuid.uuid4()).replace("-", "")[:8].upper()
    return f"TKT-{short}"


@tool
def create_support_ticket(
    customer_id: str,
    subject: str,
    description: str,
    priority: str,
    session_id: str,
    escalation_reason: str,
) -> str:
    """
    Create a support ticket and an escalation log entry for a customer issue
    that requires human agent intervention.

    Args:
        customer_id: The UUID of the customer's profile row.
        subject: A concise subject line for the ticket (max 500 chars).
        description: Full description of the customer's issue.
        priority: Ticket priority — one of: low, medium, high, urgent.
        session_id: The current chat session identifier.
        escalation_reason: Why the AI is escalating to a human agent.

    Returns:
        A confirmation string with the generated ticket number.
    """
    db = SessionLocal()
    try:
        # Validate priority — default to medium if invalid
        valid_priorities = {p.value for p in TicketPriority}
        safe_priority = priority if priority in valid_priorities else "medium"

        ticket_number = _generate_ticket_number()

        ticket = Ticket(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            ticket_number=ticket_number,
            subject=subject[:500],
            description=description,
            status=TicketStatus.escalated,
            priority=TicketPriority(safe_priority),
            assigned_agent="AI Escalation Agent",
        )
        db.add(ticket)
        db.flush()

        # Map ticket priority to escalation priority
        escalation_priority_map = {
            "low": EscalationPriority.low,
            "medium": EscalationPriority.medium,
            "high": EscalationPriority.high,
            "urgent": EscalationPriority.critical,
        }

        escalation_log = EscalationLog(
            id=str(uuid.uuid4()),
            ticket_id=ticket.id,
            session_id=session_id,
            reason=escalation_reason,
            priority=escalation_priority_map.get(safe_priority, EscalationPriority.medium),
            resolved=False,
        )
        db.add(escalation_log)
        db.commit()

        return (
            f"Escalation ticket **{ticket_number}** has been created with {safe_priority.upper()} priority. "
            f"A human support agent will review your case and contact you within 24 hours. "
            f"You can track this ticket in the Tickets section of your dashboard."
        )
    except Exception as e:
        db.rollback()
        return f"Failed to create support ticket: {str(e)}"
    finally:
        db.close()
