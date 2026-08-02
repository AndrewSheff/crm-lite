"""Роутер активностей — CRUD, завершение."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, require_role
from app.database import get_db
from app.models.user import User
from app.schemas.activity import ActivityCreate
from app.services import activity_service

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("")
async def list_activities(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    client_id: UUID | None = None,
    deal_id: UUID | None = None,
    type: str | None = None,
    is_completed: bool | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Список активностей с фильтрами."""
    return await activity_service.list_activities(
        db, user, page, per_page, client_id, deal_id, type, is_completed
    )


@router.post("", status_code=201)
async def create_activity(
    data: ActivityCreate,
    user: User = Depends(require_role("admin", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """Создание активности."""
    return await activity_service.create_activity(data, user, db)


@router.patch("/{activity_id}/complete")
async def complete_activity(
    activity_id: UUID,
    user: User = Depends(require_role("admin", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """Отметить активность как выполненную."""
    return await activity_service.complete_activity(activity_id, user, db)


@router.delete("/{activity_id}")
async def delete_activity(
    activity_id: UUID,
    user: User = Depends(require_role("admin", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """Удаление активности."""
    return await activity_service.delete_activity(activity_id, user, db)
