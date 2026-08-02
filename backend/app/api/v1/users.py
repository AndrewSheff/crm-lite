"""Роутер управления пользователями — только для admin."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_role
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = None,
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Список пользователей — только admin."""
    return await user_service.list_users(db, page, per_page, search)


@router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Юзер по ID — только admin."""
    return await user_service.get_user(user_id, db)


@router.post("", status_code=201)
async def create_user(
    data: UserCreate,
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Создание юзера — только admin."""
    return await user_service.create_user(data, db)


@router.patch("/{user_id}/block")
async def block_user(
    user_id: UUID,
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Блокировка/разблокировка юзера — только admin."""
    return await user_service.block_user(user_id, db)
