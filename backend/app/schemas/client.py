"""Схемы клиентов — создание, обновление, ответ."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from app.schemas.tag import TagResponse


class ClientOwner(BaseModel):
    id: uuid.UUID
    name: str

    model_config = {"from_attributes": True}


class ClientCreate(BaseModel):
    name: str
    email: EmailStr | None = None
    phone: str | None = None
    company: str | None = None
    industry: str | None = None
    website: str | None = None
    address: str | None = None
    status: str = "lead"
    source: str | None = None
    tag_ids: list[uuid.UUID] = []

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Имя клиента не может быть пустым")
        return v.strip()

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        allowed = {"lead", "active", "inactive"}
        if v not in allowed:
            raise ValueError(f"Статус должен быть: {', '.join(allowed)}")
        return v


class ClientUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    company: str | None = None
    industry: str | None = None
    website: str | None = None
    address: str | None = None
    status: str | None = None
    source: str | None = None
    tag_ids: list[uuid.UUID] | None = None

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str | None) -> str | None:
        if v is not None:
            allowed = {"lead", "active", "inactive"}
            if v not in allowed:
                raise ValueError(f"Статус должен быть: {', '.join(allowed)}")
        return v


class ClientResponse(BaseModel):
    """Ответ API — клиент с owner, tags, deals_count, total_revenue."""

    id: uuid.UUID
    name: str
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    industry: str | None = None
    website: str | None = None
    address: str | None = None
    status: str
    source: str | None = None
    owner: ClientOwner
    tags: list[TagResponse] = []
    deals_count: int = 0
    total_revenue: float = 0.0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
