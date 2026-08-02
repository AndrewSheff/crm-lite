"""Роутер сделок — CRUD, канбан, перемещение, AI-резюме."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, require_role
from app.database import get_db
from app.models.user import User
from app.schemas.deal import DealCreate, DealUpdate, MoveStageRequest
from app.services import ai_service, deal_service

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("")
async def list_deals(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    client_id: UUID | None = None,
    stage_id: UUID | None = None,
    owner_id: UUID | None = None,
    priority: str | None = None,
    sort_by: str = Query("created_at", pattern="^(title|amount|created_at|updated_at)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Список сделок с фильтрацией и пагинацией."""
    return await deal_service.list_deals(
        user, db, page, per_page, client_id, stage_id, owner_id, priority,
        sort_by, sort_order,
    )


@router.get("/kanban")
async def get_kanban(
    owner_id: UUID | None = None,
    client_id: UUID | None = None,
    priority: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Канбан-вид — сделки сгруппированные по стадиям."""
    return await deal_service.get_kanban(user, db, owner_id, client_id, priority)


@router.get("/{deal_id}")
async def get_deal(
    deal_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Сделка по ID."""
    return await deal_service.get_deal(deal_id, user, db)


@router.post("", status_code=201)
async def create_deal(
    data: DealCreate,
    user: User = Depends(require_role("admin", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """Создание сделки."""
    return await deal_service.create_deal(data, user, db)


@router.put("/{deal_id}")
async def update_deal(
    deal_id: UUID,
    data: DealUpdate,
    user: User = Depends(require_role("admin", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """Обновление сделки."""
    return await deal_service.update_deal(deal_id, data, user, db)


@router.delete("/{deal_id}")
async def delete_deal(
    deal_id: UUID,
    user: User = Depends(require_role("admin", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """Удаление сделки."""
    return await deal_service.delete_deal(deal_id, user, db)


@router.patch("/{deal_id}/stage")
async def move_stage(
    deal_id: UUID,
    data: MoveStageRequest,
    user: User = Depends(require_role("admin", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """Перемещение сделки на другую стадию (канбан)."""
    return await deal_service.move_stage(deal_id, data.stage_id, data.position, user, db)


@router.post("/{deal_id}/ai-summary")
async def ai_summary(
    deal_id: UUID,
    _user: User = Depends(require_role("admin", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """AI-резюме по сделке."""
    return await ai_service.generate_deal_summary(deal_id, db)
