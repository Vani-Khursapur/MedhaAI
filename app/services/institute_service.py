from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

def create_institute_code(
    db: Session,
    firebase_uid: str,
    organization_id: str,
    max_redemptions: int,
    expires_at=None
):
    try:
        query = text("""
            SELECT public.api_create_institute_code(
                :firebase_uid,
                CAST(:organization_id AS uuid),
                :max_redemptions,
                CAST(:expires_at AS timestamptz),
                'member'
            )
        """)

        result = db.execute(
            query,
            {
                "firebase_uid": firebase_uid,
                "organization_id": organization_id,
                "max_redemptions": max_redemptions,
                "expires_at": expires_at
            }
        )

        response = result.scalar_one()

        db.commit()

        return response

    except SQLAlchemyError as e:
        db.rollback()

        error_message = str(getattr(e, "orig", e))

        if "Institute owner or admin required" in error_message:
            raise HTTPException(
                status_code=403,
                detail="Institute owner or admin required"
            )

        if "Institute access is not active" in error_message:
            raise HTTPException(
                status_code=403,
                detail="Institute access is not active"
            )

        if "Invalid maximum redemptions for this plan" in error_message:
            raise HTTPException(
                status_code=400,
                detail="Invalid maximum redemptions for this plan"
            )

        if "Code expiry must be a finite future timestamp" in error_message:
            raise HTTPException(
                status_code=400,
                detail="Code expiry must be in the future"
            )

        if "Owner not found or inactive" in error_message:
            raise HTTPException(
                status_code=404,
                detail="Organization not found or inactive"
            )

        if "Active user required" in error_message:
            raise HTTPException(
                status_code=403,
                detail="Active user required"
            )

        raise HTTPException(
            status_code=500,
            detail="Unable to create institute joining code"
        )


def redeem_institute_code(
    db: Session,
    firebase_uid: str,
    code: str
):
    try:
        query = text("""
            SELECT public.api_redeem_license(
                :firebase_uid,
                :code
            )
        """)

        result = db.execute(
            query,
            {
                "firebase_uid": firebase_uid,
                "code": code.strip()
            }
        )

        response = result.scalar_one()

        db.commit()

        return response

    except SQLAlchemyError as e:
        db.rollback()

        original_error = getattr(e, "orig", e)
        error_message = str(original_error)

        sql_state = (
            getattr(original_error, "sqlstate", None)
            or getattr(original_error, "pgcode", None)
        )

        # Duplicate membership/redemption
        if sql_state == "23505":
            raise HTTPException(
                status_code=409,
                detail="Your membership changed during this request. Refresh your account or retry the same code."
            )

        error_mapping = {
            "Account is disabled": (
                403, "This Medha account is disabled."
            ),
            "Active user required": (
                403, "An active account is required."
            ),
            "Active registered user required": (
                403, "Complete your account before redeeming an institute code."
            ),
            "Institute code is required": (
                400, "Enter your institute code."
            ),
            "Invalid institute code": (
                400, "This institute code is invalid. Check it with your institute owner or admin."
            ),
            "Institute code is invalid, revoked, or expired": (
                400, "This institute code is invalid, revoked or expired. Ask your institute owner or admin for a new one."
            ),
            "Institute access is not active": (
                403, "The institute subscription is not active. Contact your institute owner or admin."
            ),
            "Membership is disabled; contact your institute admin": (
                403, "Your institute membership is disabled. Contact your institute admin."
            ),
            "Code already redeemed by this user": (
                409, "You already redeemed this code. Contact your institute admin if access is missing."
            ),
            "Institute code has reached its redemption limit": (
                409, "This code has reached its redemption limit. Ask your institute owner or admin for another code."
            ),
            "Institute seat limit reached": (
                409, "The institute has no available seats. Contact your institute owner or admin."
            ),
            "Owner not found or inactive": (
                404, "This institute is no longer available. Contact your institute owner or admin."
            )
        }

        for error_key, (status_code, message) in error_mapping.items():
            if error_key in error_message:
                raise HTTPException(
                    status_code=status_code,
                    detail=message
                )

        raise HTTPException(
            status_code=500,
            detail="The institute code could not be redeemed. Please try again."
        )
