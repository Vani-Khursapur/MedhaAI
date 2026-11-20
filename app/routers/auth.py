from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.auth import RegisterRequest
from app.database.connection import get_db

from app.services.auth_service import (
    register_user,
    get_user_by_firebase_uid,
    get_user_entitlement
)

from app.services.firebase_service import verify_firebase_token


router = APIRouter(tags=["Authentication"])

security = HTTPBearer()

security = HTTPBearer()

def get_verified_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    id_token = credentials.credentials

    print("Firebase ID Token:", id_token)
    
    return verify_firebase_token(id_token)


@router.post("/auth/register")
def register(
    user: RegisterRequest,
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(get_verified_user)
):
    verified_phone = firebase_user["phone"]

    if user.phone_number and user.phone_number != verified_phone:
        raise HTTPException(
            status_code=403,
            detail="Phone number does not match Firebase account"
        )

    return register_user(
        db=db,
        firebase_uid=firebase_user["uid"],
        phone_number=verified_phone,
        name=user.name,
        email=str(user.email)
    )


@router.post("/auth/me")
def get_me(
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(get_verified_user)
):
    print(firebase_user["uid"])

    return get_user_by_firebase_uid(
        db=db,
        firebase_uid=firebase_user["uid"],
        phone_number=firebase_user["phone"]
        
    )


@router.get("/me/entitlement")
def get_entitlement(
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(get_verified_user)
):
    return get_user_entitlement(
        db=db,
        firebase_uid=firebase_user["uid"],
        phone_number=firebase_user["phone"]
    )
