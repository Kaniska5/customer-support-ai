from langchain_core.tools import tool
from app.database.session import SessionLocal
from app.models import Order
from typing import Optional

@tool
def get_order_by_number(order_number: str, customer_id: str) -> str:
    """
    Retrieve details for a specific order by its order number.
    Args:
        order_number: The unique order number (e.g., ORD-12345678).
        customer_id: The ID of the authenticated customer requesting the order.
    Returns:
        A string containing the order details or an error message if not found.
    """
    db = SessionLocal()
    try:
        order = db.query(Order).filter(
            Order.order_number == order_number,
            Order.customer_id == customer_id
        ).first()
        
        if not order:
            return f"Order '{order_number}' not found for this account."
            
        return (
            f"Order Details:\n"
            f"- Status: {order.status}\n"
            f"- Total: {order.total_amount} {order.currency}\n"
            f"- Delivery Estimate: {order.estimated_delivery}\n"
            f"- Refund Eligible: {order.is_refund_eligible}\n"
            f"- Tracking: {order.tracking_number}"
        )
    finally:
        db.close()

@tool
def get_recent_orders(customer_id: str, limit: int = 3) -> str:
    """
    Retrieve the most recent orders for the customer.
    Args:
        customer_id: The ID of the authenticated customer.
        limit: The maximum number of orders to return.
    Returns:
        A string listing recent orders and their current status.
    """
    db = SessionLocal()
    try:
        orders = db.query(Order).filter(
            Order.customer_id == customer_id
        ).order_by(Order.created_at.desc()).limit(limit).all()
        
        if not orders:
            return "No recent orders found."
            
        result = "Recent Orders:\n"
        for o in orders:
            result += f"- {o.order_number}: {o.status} ({o.total_amount} {o.currency})\n"
        return result
    finally:
        db.close()
