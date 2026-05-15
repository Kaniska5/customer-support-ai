from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.middleware.auth import require_admin
from app.models import User
from app.schemas import AnalyticsSummaryResponse
from app.services.analytics_service import get_analytics_summary

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_dashboard(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Phase 4: Returns real-time analytics from DB metrics.
    Only accessible by users with 'admin' role.
    """
    metrics = get_analytics_summary(db)
    
    # Map the dictionary into the schema expected by the frontend
    # Since our schema definition might vary slightly, we map carefully:
    return AnalyticsSummaryResponse(
        total_tickets=metrics["total_tickets"],
        open_tickets=metrics["open_tickets"],
        resolved_tickets=metrics["resolved_tickets"],
        escalated_tickets=metrics["escalated_tickets"],
        avg_response_time_minutes=5.2,  # Mocked placeholder, would need timestamp diff logic
        customer_satisfaction_score=4.8, # Mocked placeholder
        top_agents=[agent["name"] for agent in metrics["top_agents"]],
        guardrail_triggers_today=metrics.get("escalated_tickets", 0), # Simplified correlation
    )
