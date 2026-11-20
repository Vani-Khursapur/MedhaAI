
import uuid

from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.connection import Base


class User(Base):
    __tablename__ = "app_users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )

    firebase_uid = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    phone_number = Column(
        String,
        unique=True,
        nullable=True,
        index=True
    )

    display_name = Column(String, nullable=True)

    role = Column(
        String,
        nullable=False,
        default="user",
        server_default=text("'user'")
    )

    status = Column(
        String,
        nullable=False,
        default="active",
        server_default=text("'active'")
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    email = Column(String, nullable=True)
