"""Сервис авторизации — регистрация, логин, рефреш, смена пароля."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UpdateProfileRequest,
)
from app.schemas.user import UserResponse

log = get_logger(__name__)


async def register(data: RegisterRequest, db: AsyncSession) -> dict:
    """Регистрация нового юзера — проверяем дубликат email, хешим пароль."""
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise ConflictError("Пользователь с таким email уже существует")

    user = User(
        email=data.email,
        name=data.name,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    await db.flush()

    tokens = _create_tokens(str(user.id))
    log.info("user_registered", user_id=str(user.id), email=user.email)

    return {
        **tokens.model_dump(),
        "user": UserResponse.model_validate(user).model_dump(),
    }


async def login(data: LoginRequest, db: AsyncSession) -> dict:
    """Логин — проверяем email/пароль, выдаем токены."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise UnauthorizedError("Неверный email или пароль")

    if not user.is_active:
        raise UnauthorizedError("Аккаунт заблокирован")

    tokens = _create_tokens(str(user.id))
    log.info("user_logged_in", user_id=str(user.id))

    return {
        **tokens.model_dump(),
        "user": UserResponse.model_validate(user).model_dump(),
    }


async def refresh(refresh_token: str, db: AsyncSession) -> dict:
    """Обновление токенов по refresh_token."""
    user_id = decode_token(refresh_token, expected_type="refresh")
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise UnauthorizedError("Невалидный refresh token")

    tokens = _create_tokens(str(user.id))
    return tokens.model_dump()


async def change_password(
    data: ChangePasswordRequest, user: User, db: AsyncSession
) -> dict:
    """Смена пароля — проверяем текущий, ставим новый."""
    if not verify_password(data.current_password, user.hashed_password):
        raise UnauthorizedError("Неверный текущий пароль")

    user.hashed_password = hash_password(data.new_password)
    user.must_change_password = False
    await db.flush()

    log.info("password_changed", user_id=str(user.id))
    return {"message": "Пароль успешно изменен"}


async def get_me(user: User) -> dict:
    """Возвращаем данные текущего юзера."""
    return UserResponse.model_validate(user).model_dump()


async def update_me(
    data: UpdateProfileRequest, user: User, db: AsyncSession
) -> dict:
    """Обновляем профиль текущего юзера."""
    if data.name is not None:
        user.name = data.name
    if data.avatar_url is not None:
        user.avatar_url = data.avatar_url
    await db.flush()
    return UserResponse.model_validate(user).model_dump()


def _create_tokens(user_id: str) -> TokenResponse:
    """Вспомогательная — создаем пару токенов."""
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )
