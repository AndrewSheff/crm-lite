"""Роутер клиентов — CRUD с owner-based доступом."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, require_role
from app.database import get_db
from app.models.user import User
from app.schemas.client import ClientCreate, ClientUpdate
from app.services import client_service

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("")
async def list_clients(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = None,
    status: str | None = None,
    owner_id: UUID | None = None,
    tag_id: UUID | None = None,
    sort_by: str = Query("created_at", pattern="^(name|created_at|updated_at)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Список клиентов с фильтрацией и пагинацией."""
    return await client_service.list_clients(
        user, db, page, per_page, search, status, owner_id, tag_id, sort_by, sort_order
    )


@router.get("/{client_id}")
async def get_client(
    client_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Клиент по ID."""
    return await client_service.get_client(client_id, user, db)


@router.post("", status_code=201)
async def create_client(
    data: ClientCreate,
    user: User = Depends(require_role("admin", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """Создание клиента."""
    return await client_service.create_client(data, user, db)


@router.put("/{client_id}")
async def update_client(
    client_id: UUID,
    data: ClientUpdate,
    user: User = Depends(require_role("admin", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """Обновление клиента."""
    return await client_service.update_client(client_id, data, user, db)


@router.delete("/{client_id}")
async def delete_client(
    client_id: UUID,
    user: User = Depends(require_role("admin", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """Удаление клиента."""
    return await client_service.delete_client(client_id, user, db)
