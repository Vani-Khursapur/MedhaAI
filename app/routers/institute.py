
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.routers.auth import get_verified_user
from app.schemas.institute import CreateInstituteCodeRequest
from app.services.institute_service import create_institute_code
from app.schemas.institute import RedeemInstituteCodeRequest
from app.services.institute_service import redeem_institute_code

router = APIRouter(tags=["Institute"])


@router.post("/org/codes/create")
def create_code(
    request: CreateInstituteCodeRequest,
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(get_verified_user)
):
    return create_institute_code(
        db=db,
        firebase_uid=firebase_user["uid"],
        organization_id=str(request.organization_id),
        max_redemptions=request.max_redemptions,
        expires_at=request.expires_at
    )


@router.post("/license/redeem")
def redeem_code(
    request: RedeemInstituteCodeRequest,
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(get_verified_user)
):
    return redeem_institute_code(
        db=db,
        firebase_uid=firebase_user["uid"],
        code=request.code
    )

