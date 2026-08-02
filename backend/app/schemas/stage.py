"""Схемы стадий воронки — создание, обновление, ответ, переупорядочивание."""

import uuid

from pydantic import BaseModel, field_validator


class StageCreate(BaseModel):
    name: str
    color: str = "#6366f1"
    is_won: bool = False
    is_lost: bool = False

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Название стадии не может быть пустым")
        return v.strip()


class StageUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    is_won: bool | None = None
    is_lost: bool | None = None


class StageResponse(BaseModel):
    id: uuid.UUID
    name: str
    position: int
    color: str
    is_won: bool
    is_lost: bool

    model_config = {"from_attributes": True}


class ReorderRequest(BaseModel):
    """Массив ID стадий в новом порядке."""
    order: list[uuid.UUID]
