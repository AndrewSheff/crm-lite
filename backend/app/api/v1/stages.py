"""Роутер стадий воронки — CRUD и переупорядочивание (admin)."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, require_role
from app.database import get_db
from app.models.user import User
from app.schemas.stage import ReorderRequest, StageCreate, StageUpdate
from app.services import stage_service

router = APIRouter(prefix="/stages", tags=["stages"])


@router.get("")
async def list_stages(
    _user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Список всех стадий по порядку."""
    return await stage_service.list_stages(db)


@router.post("", status_code=201)
async def create_stage(
    data: StageCreate,
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Создание стадии — только admin."""
    return await stage_service.create_stage(data, db)


@router.put("/{stage_id}")
async def update_stage(
    stage_id: UUID,
    data: StageUpdate,
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Обновление стадии — только admin."""
    return await stage_service.update_stage(stage_id, data, db)


@router.delete("/{stage_id}")
async def delete_stage(
    stage_id: UUID,
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Удаление стадии — только admin."""
    return await stage_service.delete_stage(stage_id, db)


@router.patch("/reorder")
async def reorder_stages(
    data: ReorderRequest,
    _admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Переупорядочивание стадий — только admin."""
    return await stage_service.reorder_stages(data.order, db)
