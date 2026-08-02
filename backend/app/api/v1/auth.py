"""Роутер авторизации — логин, регистрация, рефреш, смена пароля, профиль."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import limiter
from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    UpdateProfileRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
@limiter.limit("5/minute")
async def register(request: Request, data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Регистрация нового юзера — лимит 5 запросов/мин."""
    return await auth_service.register(data, db)


@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Логин — email + пароль → токены, лимит 10 запросов/мин."""
    return await auth_service.login(data, db)


@router.post("/refresh")
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Обновление пары токенов."""
    return await auth_service.refresh(data.refresh_token, db)


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Смена пароля текущего юзера."""
    return await auth_service.change_password(data, user, db)


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    """Данные текущего юзера из токена."""
    return await auth_service.get_me(user)


@router.put("/me")
async def update_me(
    data: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обновление профиля текущего юзера."""
    return await auth_service.update_me(data, user, db)
