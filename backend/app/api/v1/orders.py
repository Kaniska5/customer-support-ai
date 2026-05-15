from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.middleware.auth import get_current_user, require_verified
from app.models import User, Order, Customer
from app.schemas import OrderOut, OrderListResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/", response_model=OrderListResponse)
def list_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    status: str = Query(default=None),
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
):
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        return OrderListResponse(orders=[], total=0, page=page, page_size=page_size)

    query = db.query(Order).filter(Order.customer_id == customer.id)
    if status:
        query = query.filter(Order.status == status)

    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return OrderListResponse(
        orders=[OrderOut.model_validate(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: str,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
):
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    order = db.query(Order).filter(Order.id == order_id, Order.customer_id == customer.id).first()
    if not order:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderOut.model_validate(order)
