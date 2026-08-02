"""Сервис тегов — создание, получение списка, удаление."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagResponse


async def list_tags(db: AsyncSession) -> list[dict]:
    """Все теги, отсортированные по имени."""
    result = await db.execute(select(Tag).order_by(Tag.name))
    tags = result.scalars().all()
    return [TagResponse.model_validate(t).model_dump() for t in tags]


async def create_tag(data: TagCreate, db: AsyncSession) -> dict:
    """Создание тега — проверяем уникальность имени."""
    existing = await db.execute(select(Tag).where(Tag.name == data.name))
    if existing.scalar_one_or_none():
        raise ConflictError(f"Тег '{data.name}' уже существует")

    tag = Tag(name=data.name, color=data.color)
    db.add(tag)
    await db.flush()
    return TagResponse.model_validate(tag).model_dump()


async def delete_tag(tag_id: UUID, db: AsyncSession) -> dict:
    """Удаление тега по ID."""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise NotFoundError("Тег не найден")

    await db.delete(tag)
    await db.flush()
    return {"message": "Тег удален"}
