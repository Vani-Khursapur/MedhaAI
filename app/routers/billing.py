
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.schemas.billing import (
    BillingOrderRequest,
    VerifyProviderKeyRequest
)

from app.services.billing_service import (
    create_billing_order,
    verify_provider_key
)

from app.routers.auth import get_verified_user


router = APIRouter(tags=["Billing"])


# --------------------------------------------------
# 1. CREATE BILLING ORDER
# --------------------------------------------------

@router.post("/billing/orders")
def create_order(
    order: BillingOrderRequest,
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(get_verified_user)
):
    return create_billing_order(
        db=db,
        firebase_uid=firebase_user["uid"],
        request_id=order.request_id,
        offering=order.offering,
        ai_mode=order.ai_mode,
        billing=order.billing,
        seats=order.seats,
        institute_name=order.institute_name,
        name=order.name,
        email=str(order.email),
        credential_id=order.credential_id
    )


# --------------------------------------------------
# 2. VERIFY PROVIDER API KEY (BYOK)
# --------------------------------------------------

@router.post("/billing/verify-key")
def verify_key(
    request: VerifyProviderKeyRequest,
    response: Response,
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(get_verified_user)
):
    # Prevent caching of sensitive verification responses
    response.headers["Cache-Control"] = "no-store"

    return verify_provider_key(
        db=db,
        firebase_uid=firebase_user["uid"],
        offering=request.offering,
        provider=request.provider,
        api_key=request.api_key.get_secret_value()
    )
