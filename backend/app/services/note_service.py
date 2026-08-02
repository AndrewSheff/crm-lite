"""Сервис заметок — CRUD с фильтрацией по клиенту/сделке и owner-based доступом."""

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.client import Client
from app.models.deal import Deal
from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate


async def list_notes(
    db: AsyncSession,
    user: User,
    page: int = 1,
    per_page: int = 20,
    client_id: UUID | None = None,
    deal_id: UUID | None = None,
) -> dict:
    """Список заметок — фильтр по client_id/deal_id с owner-based доступом."""
    query = select(Note).options(joinedload(Note.author))

    if client_id:
        query = query.where(Note.client_id == client_id)
    if deal_id:
        query = query.where(Note.deal_id == deal_id)

    # owner-based: менеджер видит только заметки по своим клиентам/сделкам
    if user.role != "admin":
        query = query.where(
            or_(
                Note.client_id.in_(
                    select(Client.id).where(Client.owner_id == user.id)
                ),
                Note.deal_id.in_(
                    select(Deal.id).where(Deal.owner_id == user.id)
                ),
                Note.author_id == user.id,
            )
        )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    query = query.order_by(Note.is_pinned.desc(), Note.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    notes = result.unique().scalars().all()

    return {
        "items": [NoteResponse.model_validate(n).model_dump() for n in notes],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


async def create_note(
    data: NoteCreate, user: User, db: AsyncSession
) -> dict:
    """Создание заметки."""
    note = Note(
        content=data.content,
        author_id=user.id,
        client_id=data.client_id,
        deal_id=data.deal_id,
        is_pinned=data.is_pinned,
    )
    db.add(note)
    await db.flush()
    await db.refresh(note)
    return NoteResponse.model_validate(note).model_dump()


async def update_note(
    note_id: UUID, data: NoteUpdate, user: User, db: AsyncSession
) -> dict:
    """Обновление заметки — только автор или admin."""
    note = await _get_note_or_404(note_id, db)
    _check_access(note, user)

    update_data = data.model_dump(exclude_unset=True)
    allowed = {"content", "is_pinned"}
    for field, value in update_data.items():
        if field in allowed:
            setattr(note, field, value)

    await db.flush()
    return NoteResponse.model_validate(note).model_dump()


async def delete_note(
    note_id: UUID, user: User, db: AsyncSession
) -> dict:
    """Удаление заметки."""
    note = await _get_note_or_404(note_id, db)
    _check_access(note, user)

    await db.delete(note)
    await db.flush()
    return {"message": "Заметка удалена"}


async def _get_note_or_404(note_id: UUID, db: AsyncSession) -> Note:
    result = await db.execute(
        select(Note).options(joinedload(Note.author)).where(Note.id == note_id)
    )
    note = result.unique().scalar_one_or_none()
    if not note:
        raise NotFoundError("Заметка не найдена")
    return note


def _check_access(note: Note, user: User) -> None:
    if user.role != "admin" and note.author_id != user.id:
        raise ForbiddenError("Нет доступа к этой заметке")
