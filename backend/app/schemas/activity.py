"""Схемы активностей — создание, ответ."""

import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

from app.schemas.client import ClientOwner


class ActivityCreate(BaseModel):
    type: str
    title: str
    description: str | None = None
    client_id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    scheduled_at: datetime | None = None

    @field_validator("type")
    @classmethod
    def valid_type(cls, v: str) -> str:
        allowed = {"call", "meeting", "email", "task"}
        if v not in allowed:
            raise ValueError(f"Тип: {', '.join(allowed)}")
        return v

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Заголовок не может быть пустым")
        return v.strip()


class ActivityResponse(BaseModel):
    id: uuid.UUID
    type: str
    title: str
    description: str | None = None
    author: ClientOwner
    client_id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    is_completed: bool
    scheduled_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
