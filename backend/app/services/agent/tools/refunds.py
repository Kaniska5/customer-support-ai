from langchain_core.tools import tool
from app.database.session import SessionLocal
from app.models import Order, Refund, RefundStatus
from typing import Optional

@tool
def check_refund_eligibility(order_number: str, customer_id: str) -> str:
    """
    Check if a specific order is eligible for a refund.
    Args:
        order_number: The unique order number (e.g., ORD-12345678).
        customer_id: The ID of the authenticated customer.
    Returns:
        A string explaining if the order is eligible, and if not, the reason why.
    """
    db = SessionLocal()
    try:
        order = db.query(Order).filter(
            Order.order_number == order_number,
            Order.customer_id == customer_id
        ).first()
        
        if not order:
            return f"Order '{order_number}' not found."
            
        if not order.is_refund_eligible:
            return f"Order '{order_number}' is NOT eligible for a refund. Only 'delivered' or 'cancelled' orders within 30 days are eligible."
            
        # Check if refund already exists
        existing_refund = db.query(Refund).filter(Refund.order_id == order.id).first()
        if existing_refund:
            return f"A refund request for order '{order_number}' already exists with status: {existing_refund.status}."
            
        return f"Order '{order_number}' is eligible for a refund. Amount: {order.total_amount} {order.currency}."
    finally:
        db.close()

@tool
def recommend_refund_approval(order_number: str, reason: str, customer_id: str) -> str:
    """
    Creates a preliminary refund recommendation. 
    NOTE: Actual approval requires human intervention or guardrail checks in future phases.
    Args:
        order_number: The unique order number.
        reason: The reason provided by the customer for the refund.
        customer_id: The ID of the authenticated customer.
    Returns:
        A confirmation string.
    """
    db = SessionLocal()
    try:
        order = db.query(Order).filter(
            Order.order_number == order_number,
            Order.customer_id == customer_id
        ).first()
        
        if not order:
            return f"Order '{order_number}' not found."
            
        # Instead of directly writing to DB (Phase 3 Guardrails), we log the intent.
        return f"Recommended processing refund for order '{order_number}' due to: {reason}. This will be queued for review."
    finally:
        db.close()
