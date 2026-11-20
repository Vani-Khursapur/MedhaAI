
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError
from fastapi import HTTPException


def handle_database_error(error: DBAPIError):
    original_error = getattr(error, "orig", None)
    sqlstate = getattr(original_error, "sqlstate", None)

    if sqlstate == "22023":
        raise HTTPException(
            status_code=400,
            detail="Invalid registration or request data"
        )

    if sqlstate == "42501":
        raise HTTPException(
            status_code=403,
            detail="Account is disabled or access is denied"
        )

    raise HTTPException(
        status_code=500,
        detail="Database operation failed"
    )


def execute_function(db: Session, query: str, params: dict):
    try:
        result = db.execute(text(query), params)
        data = result.scalar_one()
        db.commit()
        return data

    except DBAPIError as error:
        db.rollback()
        handle_database_error(error)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unexpected database error"
        )


def register_user(
    db: Session,
    firebase_uid: str,
    phone_number: str,
    name: str,
    email: str
):
    return execute_function(
        db,
        """
        SELECT public.api_register_account(
            :firebase_uid, :phone_number, :name, :email
        )
        """,
        {
            "firebase_uid": firebase_uid,
            "phone_number": phone_number,
            "name": name,
            "email": email
        }
    )


def get_user_by_firebase_uid(
    db: Session,
    firebase_uid: str,
    phone_number: str
):
    return execute_function(
        db,
        """
        SELECT public.api_auth_me(
            :firebase_uid, :phone_number
        )
        """,
        {
            "firebase_uid": firebase_uid,
            "phone_number": phone_number
        }
    )


def get_user_entitlement(
    db: Session,
    firebase_uid: str,
    phone_number: str
):
    return execute_function(
        db,
        """
        SELECT public.api_get_entitlement(
            :firebase_uid, :phone_number
        )
        """,
        {
            "firebase_uid": firebase_uid,
            "phone_number": phone_number
        }
    )
