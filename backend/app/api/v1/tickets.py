import uuid
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.middleware.auth import require_verified
from app.models import User, Ticket, Customer
from app.schemas import TicketCreateRequest, TicketOut, TicketListResponse
from datetime import datetime, timezone

router = APIRouter(prefix="/tickets", tags=["Tickets"])


def _ticket_number() -> str:
    return f"TKT-{uuid.uuid4().hex[:8].upper()}"


@router.post("/", response_model=TicketOut, status_code=201)
def create_ticket(
    payload: TicketCreateRequest,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
):
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    ticket = Ticket(
        customer_id=customer.id,
        ticket_number=_ticket_number(),
        subject=payload.subject,
        description=payload.description,
        priority=payload.priority or "medium",
        status="open",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return TicketOut.model_validate(ticket)


@router.get("/", response_model=TicketListResponse)
def list_tickets(
    status: str = Query(default=None),
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
):
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        return TicketListResponse(tickets=[], total=0)

    query = db.query(Ticket).filter(Ticket.customer_id == customer.id)
    if status:
        query = query.filter(Ticket.status == status)

    tickets = query.order_by(Ticket.created_at.desc()).all()
    return TicketListResponse(
        tickets=[TicketOut.model_validate(t) for t in tickets],
        total=len(tickets),
    )


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: str,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
):
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.customer_id == customer.id,
    ).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketOut.model_validate(ticket)
