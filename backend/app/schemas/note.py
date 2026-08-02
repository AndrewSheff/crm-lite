"""Схемы заметок — создание, обновление, ответ."""

import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator, model_validator

from app.schemas.client import ClientOwner


class NoteCreate(BaseModel):
    content: str
    client_id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    is_pinned: bool = False

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Содержимое заметки не может быть пустым")
        return v.strip()

    @model_validator(mode="after")
    def at_least_one_target(self):
        if self.client_id is None and self.deal_id is None:
            raise ValueError("Нужно указать client_id или deal_id")
        return self


class NoteUpdate(BaseModel):
    content: str | None = None
    is_pinned: bool | None = None


class NoteResponse(BaseModel):
    id: uuid.UUID
    content: str
    author: ClientOwner
    client_id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    is_pinned: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
