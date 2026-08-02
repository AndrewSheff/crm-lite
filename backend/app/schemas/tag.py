"""Схемы тегов — создание и ответ."""

import uuid

from pydantic import BaseModel, field_validator


class TagCreate(BaseModel):
    name: str
    color: str = "#6366f1"

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Название тега не может быть пустым")
        return v.strip()


class TagResponse(BaseModel):
    id: uuid.UUID
    name: str
    color: str

    model_config = {"from_attributes": True}
