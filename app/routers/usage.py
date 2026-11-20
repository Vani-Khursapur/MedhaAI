
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.connection import get_db
from app.routers.auth import get_verified_user
from app.services.usage_service import get_usage

router = APIRouter(tags=["Usage"])


@router.get("/me/usage")
def read_usage(
    scope: str = Query(default="user"),
    organization_id: Optional[str] = Query(default=None),
    month: Optional[str] = Query(default=None),
    search: str = Query(default="", max_length=200),
    member_id: Optional[str] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=1000000),
    member_offset: int = Query(default=0, ge=0, le=1000000),
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(get_verified_user)
):
    return get_usage(
        db=db,
        firebase_uid=firebase_user["uid"],
        scope=scope,
        organization_id=organization_id,
        month=month,
        search=search,
        member_id=member_id,
        limit=limit,
        offset=offset,
        member_offset=member_offset
    )
