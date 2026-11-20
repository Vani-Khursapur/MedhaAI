
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError
from fastapi import HTTPException


def activate_billing_order(
    db: Session,
    actor_uid: str,
    order_id,
    payment_reference: str
):
    try:
        result = db.execute(
            text("""
                SELECT public.api_admin_activate_order(
                    CAST(:actor_uid AS text),
                    CAST(:order_id AS uuid),
                    CAST(:payment_reference AS text)
                )
            """),
            {
                "actor_uid": actor_uid,
                "order_id": order_id,
                "payment_reference": payment_reference
            }
        )

        response = result.scalar_one()
        db.commit()

        return response

    except DBAPIError as error:
        db.rollback()

        original_error = getattr(error, "orig", None)
        message = str(original_error or error)

        print("Admin activation database error:", message)

        if "Platform admin required" in message:
            raise HTTPException(
                status_code=403,
                detail="Only platform administrators can activate orders."
            )

        if "Active registered user required" in message:
            raise HTTPException(
                status_code=403,
                detail="An active registered user is required."
            )

        if "Active user required" in message:
            raise HTTPException(
                status_code=403,
                detail="Your account is not active."
            )

        if "Billing order not found" in message:
            raise HTTPException(
                status_code=404,
                detail="Billing order not found."
            )

        if "Payment does not match the stored order" in message:
            raise HTTPException(
                status_code=400,
                detail="Payment details do not match the order."
            )

        if "Order already activated with another payment" in message:
            raise HTTPException(
                status_code=409,
                detail="Order was already activated with another payment."
            )

        if "Order is not pending" in message:
            raise HTTPException(
                status_code=409,
                detail="This order is not pending."
            )

        if "Preview prices require explicit admin confirmation" in message:
            raise HTTPException(
                status_code=403,
                detail="Admin confirmation is required for preview prices."
            )

        if "Plan is inactive" in message:
            raise HTTPException(
                status_code=403,
                detail="This subscription plan is inactive."
            )

        if "A verified active API key is required" in message:
            raise HTTPException(
                status_code=403,
                detail="A verified active API key is required."
            )

        raise HTTPException(
            status_code=500,
            detail="Unable to activate billing order."
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unexpected error while activating billing order."
        )


def list_admin_orders(
    db: Session,
    actor_uid: str,
    status: str = "pending",
    offering: str = "all",
    search: str = "",
    limit: int = 20,
    offset: int = 0
):
    try:
        result = db.execute(
            text("""
                SELECT public.api_admin_list_orders(
                    CAST(:actor_uid AS text),
                    CAST(:status AS text),
                    CAST(:offering AS text),
                    CAST(:search AS text),
                    CAST(:limit AS integer),
                    CAST(:offset AS integer)
                )
            """),
            {
                "actor_uid": actor_uid,
                "status": status,
                "offering": offering,
                "search": search,
                "limit": limit,
                "offset": offset
            }
        )

        return result.scalar_one()

    except DBAPIError as error:
        db.rollback()

        original_error = getattr(error, "orig", None)
        message = str(original_error or error)

        if "Platform admin required" in message:
            raise HTTPException(
                status_code=403,
                detail="Only an active platform admin can view activation requests."
            )

        if "Invalid activation queue filters" in message:
            raise HTTPException(
                status_code=400,
                detail="Check the activation queue filters."
            )

        if "Active registered user required" in message:
            raise HTTPException(
                status_code=403,
                detail="Only an active platform admin can view activation requests."
            )

        raise HTTPException(
            status_code=500,
            detail="Activation requests could not be loaded. Please try again."
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Activation requests could not be loaded. Please try again."
        )

