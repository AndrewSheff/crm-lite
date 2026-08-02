"""Схемы пользователей — ответы API, создание юзера (админ)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class UserResponse(BaseModel):
    """Публичное представление юзера — без пароля и прочих секретов."""

    id: uuid.UUID
    email: str
    name: str
    role: str
    is_active: bool
    must_change_password: bool
    avatar_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    """Создание юзера админом — с временным паролем."""

    email: EmailStr
    name: str
    password: str
    role: str = "manager"

    @field_validator("role")
    @classmethod
    def valid_role(cls, v: str) -> str:
        allowed = {"admin", "manager", "viewer"}
        if v not in allowed:
            raise ValueError(f"Роль должна быть одной из: {', '.join(allowed)}")
        return v

    @field_validator("password")
    @classmethod
    def password_strong_enough(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Пароль минимум 6 символов")
        return v
