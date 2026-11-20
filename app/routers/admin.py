from typing import Literal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.routers.auth import get_verified_user
from app.schemas.admin import AdminActivateOrderRequest
from app.services.admin_service import (
    activate_billing_order,
    list_admin_orders
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.post("/activate-order")
def activate_order(
    order: AdminActivateOrderRequest,
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(get_verified_user)
):
    return activate_billing_order(
        db=db,
        actor_uid=firebase_user["uid"],
        order_id=order.order_id,
        payment_reference=order.payment_reference
    )

@router.get("/orders")
def get_admin_orders(
    status: Literal["pending", "active", "cancelled", "all"] = Query(
        default="pending"
    ),
    offering: Literal["individual", "institute", "all"] = Query(
        default="all"
    ),
    search: str = Query(default="", max_length=200),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=1000000),
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(get_verified_user)
):
    return list_admin_orders(
        db=db,
        actor_uid=firebase_user["uid"],
        status=status,
        offering=offering,
        search=search.strip(),
        limit=limit,
        offset=offset
    )