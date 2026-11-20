from datetime import datetime, timezone
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator


class CreateInstituteCodeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    organization_id: UUID = Field(alias="organizationId")

    max_redemptions: int = Field(
        alias="maxRedemptions",
        ge=1,
        le=1000
    )

    expires_at: datetime | None = Field(
        default=None,
        alias="expiresAt"
    )

    @field_validator("expires_at")
    @classmethod
    def validate_expiry(cls, value):
        if value is not None:
            if value.tzinfo is None:
                raise ValueError("Expiry must include a timezone")

            value = value.astimezone(timezone.utc)

            if value <= datetime.now(timezone.utc):
                raise ValueError("Expiry must be in the future")

        return value

class RedeemInstituteCodeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(
        min_length=1,
        max_length=256
    )