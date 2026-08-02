"""Роутер тегов — список, создание, удаление."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_role
from app.database import get_db
from app.models.user import User
from app.schemas.tag import TagCreate
from app.services import tag_service

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("")
async def list_tags(
    _user: User = Depends(require_role("admin", "manager", "viewer")),
    db: AsyncSession = Depends(get_db),
):
    """Список всех тегов."""
    return await tag_service.list_tags(db)


@router.post("", status_code=201)
async def create_tag(
    data: TagCreate,
    _user: User = Depends(require_role("admin", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """Создание тега."""
    return await tag_service.create_tag(data, db)


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: UUID,
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Удаление тега — только admin."""
    return await tag_service.delete_tag(tag_id, db)
