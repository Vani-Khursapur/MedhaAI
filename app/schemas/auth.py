from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional


class RegisterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone_number: Optional[str] = Field(
        default=None,
        alias="phoneNumber"
    )


class UserResponse(BaseModel):
    success: bool
    user: dict


class EntitlementResponse(BaseModel):
    success: bool
    individual: dict
    organizations: list[dict]
