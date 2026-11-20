from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from typing import Optional
from uuid import UUID
from typing import Optional, Literal
from pydantic import SecretStr, field_validator


class BillingOrderRequest(BaseModel):

    model_config = ConfigDict(populate_by_name=True)

    # Unique request ID
    request_id: UUID = Field(alias="requestId")

    # Subscription type
    offering: str = Field(
        pattern="^(individual|institute)$"
    )

    # AI mode
    ai_mode: str = Field(
        alias="aiMode",
        pattern="^(included|byok)$"
    )

    # Billing cycle
    billing: str = Field(
        pattern="^(monthly|yearly)$"
    )

    # Number of seats
    seats: int = Field(
        ge=1,
        le=1000
    )

    # Institute name (required only for institute subscriptions)
    institute_name: Optional[str] = Field(
        default=None,
        alias="instituteName",
        max_length=200
    )

    # Customer details
    name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    # API credential ID (required for BYOK, validated in database)
    credential_id: Optional[UUID] = Field(
        default=None,
        alias="credentialId"
    )

    # Cross-field validation
    @model_validator(mode="after")
    def validate_billing_details(self):

        # Individual subscriptions must have exactly one seat
        if self.offering == "individual" and self.seats != 1:
            raise ValueError(
                "Individual subscriptions must have exactly 1 seat"
            )

        # Institute subscriptions must have a valid institute name
        if self.offering == "institute":
            if (
                not self.institute_name
                or not self.institute_name.strip()
            ):
                raise ValueError(
                    "Institute name is required"
                )

            if not 1 <= len(self.institute_name.strip()) <= 200:
                raise ValueError(
                    "Institute name must contain 1 to 200 characters"
                )

        return self

class VerifyProviderKeyRequest(BaseModel):

    model_config = ConfigDict(populate_by_name=True)

    offering: Literal["individual", "institute"]

    provider: Literal["openai", "gemini"]

    api_key: SecretStr = Field(
        alias="apiKey",
        min_length=8,
        max_length=4096
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, value):

        key = value.get_secret_value().strip()

        if not 8 <= len(key) <= 4096:
            raise ValueError(
                "Enter a valid provider API key without spaces."
            )

        if not all(33 <= ord(char) <= 126 for char in key):
            raise ValueError(
                "Enter a valid provider API key without spaces."
            )

        return SecretStr(key)
