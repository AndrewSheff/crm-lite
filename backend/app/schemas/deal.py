"""Схемы сделок — CRUD, канбан, перемещение."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.client import ClientOwner
from app.schemas.stage import StageResponse
from app.schemas.tag import TagResponse


class DealCreate(BaseModel):
    title: str
    client_id: uuid.UUID
    stage_id: uuid.UUID
    amount: float | None = None
    currency: str = "RUB"
    probability: int = 50
    expected_close_date: date | None = None
    priority: str = "medium"
    description: str | None = None
    tag_ids: list[uuid.UUID] = []

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Название сделки не может быть пустым")
        return v.strip()

    @field_validator("priority")
    @classmethod
    def valid_priority(cls, v: str) -> str:
        allowed = {"low", "medium", "high", "urgent"}
        if v not in allowed:
            raise ValueError(f"Приоритет: {', '.join(allowed)}")
        return v

    @field_validator("probability")
    @classmethod
    def valid_probability(cls, v: int) -> int:
        if not 0 <= v <= 100:
            raise ValueError("Вероятность от 0 до 100")
        return v


class DealUpdate(BaseModel):
    title: str | None = None
    client_id: uuid.UUID | None = None
    stage_id: uuid.UUID | None = None
    amount: float | None = None
    currency: str | None = None
    probability: int | None = None
    expected_close_date: date | None = None
    priority: str | None = None
    description: str | None = None
    tag_ids: list[uuid.UUID] | None = None

    @field_validator("priority")
    @classmethod
    def valid_priority(cls, v: str | None) -> str | None:
        if v is not None:
            allowed = {"low", "medium", "high", "urgent"}
            if v not in allowed:
                raise ValueError(f"Приоритет: {', '.join(allowed)}")
        return v

    @field_validator("probability")
    @classmethod
    def valid_probability(cls, v: int | None) -> int | None:
        if v is not None and not 0 <= v <= 100:
            raise ValueError("Вероятность от 0 до 100")
        return v


class DealResponse(BaseModel):
    id: uuid.UUID
    title: str
    client: ClientOwner
    stage: StageResponse
    owner: ClientOwner
    amount: float | None = None
    currency: str
    probability: int
    expected_close_date: date | None = None
    priority: str
    description: str | None = None
    position: int
    tags: list[TagResponse] = []
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None

    model_config = {"from_attributes": True}


class KanbanCard(BaseModel):
    id: uuid.UUID
    title: str
    client: ClientOwner
    owner: ClientOwner
    amount: float | None = None
    currency: str
    probability: int
    priority: str
    expected_close_date: date | None = None
    position: int
    tags: list[TagResponse] = []

    model_config = {"from_attributes": True}


class KanbanColumn(BaseModel):
    id: uuid.UUID
    name: str
    color: str
    position: int
    is_won: bool
    is_lost: bool
    deals: list[KanbanCard] = []
    total_amount: float = 0.0
    deals_count: int = 0


class KanbanResponse(BaseModel):
    stages: list[KanbanColumn]


class MoveStageRequest(BaseModel):
    stage_id: uuid.UUID
    position: int = Field(default=0, ge=0)
