"""Сервис стадий воронки — CRUD, переупорядочивание."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import get_logger
from app.models.deal import Deal
from app.models.stage import Stage
from app.schemas.stage import StageCreate, StageResponse, StageUpdate

log = get_logger(__name__)


async def list_stages(db: AsyncSession) -> list[dict]:
    """Все стадии, отсортированные по позиции."""
    result = await db.execute(select(Stage).order_by(Stage.position))
    stages = result.scalars().all()
    return [StageResponse.model_validate(s).model_dump() for s in stages]


async def create_stage(data: StageCreate, db: AsyncSession) -> dict:
    """Создание стадии — автоматически ставим в конец."""
    # считаем макс позицию
    max_pos = await db.execute(select(func.max(Stage.position)))
    next_pos = (max_pos.scalar() or -1) + 1

    stage = Stage(
        name=data.name,
        position=next_pos,
        color=data.color,
        is_won=data.is_won,
        is_lost=data.is_lost,
    )
    db.add(stage)
    await db.flush()

    log.info("stage_created", stage_id=str(stage.id), name=stage.name)
    return StageResponse.model_validate(stage).model_dump()


async def update_stage(
    stage_id: UUID, data: StageUpdate, db: AsyncSession
) -> dict:
    """Обновление стадии."""
    stage = await _get_stage_or_404(stage_id, db)

    allowed = {"name", "color", "position", "is_won", "is_lost"}
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in allowed:
            setattr(stage, field, value)

    await db.flush()
    return StageResponse.model_validate(stage).model_dump()


async def delete_stage(stage_id: UUID, db: AsyncSession) -> dict:
    """Удаление стадии — нельзя если есть привязанные сделки."""
    stage = await _get_stage_or_404(stage_id, db)

    # проверяем что нет сделок на этой стадии
    count = await db.execute(
        select(func.count(Deal.id)).where(Deal.stage_id == stage_id)
    )
    if (count.scalar() or 0) > 0:
        raise ConflictError("Нельзя удалить стадию с привязанными сделками")

    await db.delete(stage)
    await db.flush()

    log.info("stage_deleted", stage_id=str(stage_id))
    return {"message": "Стадия удалена"}


async def reorder_stages(order: list[UUID], db: AsyncSession) -> dict:
    """Переупорядочивание стадий — массив ID в новом порядке."""
    for position, stage_id in enumerate(order):
        result = await db.execute(select(Stage).where(Stage.id == stage_id))
        stage = result.scalar_one_or_none()
        if stage:
            stage.position = position

    await db.flush()
    log.info("stages_reordered")
    return {"message": "Порядок обновлен"}


async def _get_stage_or_404(stage_id: UUID, db: AsyncSession) -> Stage:
    """Ищем стадию или 404."""
    result = await db.execute(select(Stage).where(Stage.id == stage_id))
    stage = result.scalar_one_or_none()
    if not stage:
        raise NotFoundError("Стадия не найдена")
    return stage
