
import re
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


class AIWorkspace(BaseModel):
    ownerScope: Literal["user", "organization"]
    ownerId: UUID


class AIPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    boardTitle: str | None = Field(default=None, max_length=200)
    sessionId: str | None = Field(default=None, max_length=256)
    chapterId: str | None = Field(default=None, max_length=256)
    imageDataUrl: str | None = None

    @field_validator("boardTitle", "sessionId", "chapterId", mode="before")
    @classmethod
    def normalize_optional_text(cls, value):
        if value is None:
            return None

        if isinstance(value, bool) or not isinstance(value, (str, int, float)):
            raise ValueError("Value must be text or a number")

        value = str(value).strip()

        if not value:
            raise ValueError("Value cannot be empty")

        return value

    @field_validator("imageDataUrl")
    @classmethod
    def validate_image(cls, value):
        if value is None:
            return value

        if len(value) > 8_000_000:
            raise ValueError("Image data is too large")

        if not re.fullmatch(
            r"data:image/(png|jpeg|webp);base64,[A-Za-z0-9+/]+={0,2}",
            value
        ):
            raise ValueError("Invalid image data URL")

        return value


class AISearchRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    requestId: UUID
    workspace: AIWorkspace

    boardId: str = Field(min_length=1, max_length=256)
    pageId: str = Field(min_length=1, max_length=256)
    prompt: str = Field(min_length=1, max_length=16000)

    action: Literal[
        "ai_chat",
        "circle_go",
        "circle_generate_image",
        "circle_mind_map",
        "document_question"
    ]

    payload: AIPayload = Field(default_factory=AIPayload)

    @field_validator("boardId", "pageId", "prompt")
    @classmethod
    def validate_text(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty")

        return value

    @model_validator(mode="after")
    def validate_action_payload(self):
        if self.action.startswith("circle_") and not self.payload.imageDataUrl:
            raise ValueError(
                "Select a drawing and send its PNG, JPEG or WebP crop"
            )

        if self.action == "document_question" and not self.payload.chapterId:
            raise ValueError(
                "Select a chapter before asking about its documents"
            )

        return self