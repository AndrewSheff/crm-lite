"""Роутер заметок — CRUD с фильтрацией по клиенту/сделке."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, require_role
from app.database import get_db
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate
from app.services import note_service

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("")
async def list_notes(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    client_id: UUID | None = None,
    deal_id: UUID | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Список заметок."""
    return await note_service.list_notes(db, user, page, per_page, client_id, deal_id)


@router.post("", status_code=201)
async def create_note(
    data: NoteCreate,
    user: User = Depends(require_role("admin", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """Создание заметки."""
    return await note_service.create_note(data, user, db)


@router.put("/{note_id}")
async def update_note(
    note_id: UUID,
    data: NoteUpdate,
    user: User = Depends(require_role("admin", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """Обновление заметки."""
    return await note_service.update_note(note_id, data, user, db)


@router.delete("/{note_id}")
async def delete_note(
    note_id: UUID,
    user: User = Depends(require_role("admin", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """Удаление заметки."""
    return await note_service.delete_note(note_id, user, db)
