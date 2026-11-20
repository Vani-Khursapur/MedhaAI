
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


def get_usage(
    db: Session,
    firebase_uid: str,
    scope: str = "user",
    organization_id: str = None,
    month: str = None,
    search: str = "",
    member_id: str = None,
    limit: int = 10,
    offset: int = 0,
    member_offset: int = 0
):
    try:
        query = text("""
            SELECT public.api_get_usage(
                :firebase_uid,
                :scope,
                CAST(:organization_id AS uuid),
                :month,
                :search,
                CAST(:member_id AS uuid),
                :limit,
                :offset,
                :member_offset
            )
        """)

        result = db.execute(
            query,
            {
                "firebase_uid": firebase_uid,
                "scope": scope,
                "organization_id": organization_id,
                "month": month,
                "search": search,
                "member_id": member_id,
                "limit": limit,
                "offset": offset,
                "member_offset": member_offset
            }
        )

        return result.scalar_one()

    except SQLAlchemyError as e:
        db.rollback()

        original_error = getattr(e, "orig", e)
        error_message = str(original_error)

        sql_state = (
            getattr(original_error, "sqlstate", None)
            or getattr(original_error, "pgcode", None)
        )

        if sql_state == "42501":
            raise HTTPException(
                status_code=403,
                detail=error_message
            )

        if sql_state == "22023":
            raise HTTPException(
                status_code=400,
                detail=error_message
            )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve usage information."
        )
