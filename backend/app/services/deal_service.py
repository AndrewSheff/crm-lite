"""Сервис сделок — CRUD, канбан, перемещение по стадиям."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.logging import get_logger
from app.models.deal import Deal
from app.models.stage import Stage
from app.models.tag import Tag
from app.models.user import User
from app.schemas.deal import (
    DealCreate,
    DealResponse,
    DealUpdate,
    KanbanCard,
    KanbanColumn,
    KanbanResponse,
)

log = get_logger(__name__)


async def create_deal(
    data: DealCreate, user: User, db: AsyncSession
) -> dict:
    """Создание сделки — привязка к клиенту, стадии, тегам."""
    # определяем позицию в стадии — with_for_update для защиты от race condition
    max_pos = await db.execute(
        select(func.max(Deal.position))
        .where(Deal.stage_id == data.stage_id)
        .with_for_update()
    )
    next_pos = (max_pos.scalar() or -1) + 1

    deal = Deal(
        title=data.title,
        client_id=data.client_id,
        stage_id=data.stage_id,
        owner_id=user.id,
        amount=data.amount,
        currency=data.currency,
        probability=data.probability,
        expected_close_date=data.expected_close_date,
        priority=data.priority,
        description=data.description,
        position=next_pos,
    )

    if data.tag_ids:
        result = await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))
        deal.tags = list(result.scalars().all())

    db.add(deal)
    await db.flush()
    await db.refresh(deal)

    log.info("deal_created", deal_id=str(deal.id))
    return DealResponse.model_validate(deal).model_dump()


async def get_deal(deal_id: UUID, user: User, db: AsyncSession) -> dict:
    """Получение сделки с проверкой доступа."""
    deal = await _get_deal_or_404(deal_id, db)
    _check_access(deal, user)
    return DealResponse.model_validate(deal).model_dump()


async def list_deals(
    user: User,
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    client_id: UUID | None = None,
    stage_id: UUID | None = None,
    owner_id: UUID | None = None,
    priority: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> dict:
    """Список сделок — пагинация, фильтры, owner-based доступ."""
    query = select(Deal).options(
        joinedload(Deal.client),
        joinedload(Deal.stage),
        joinedload(Deal.owner),
        joinedload(Deal.tags),
    )

    # owner-based
    if user.role != "admin":
        query = query.where(Deal.owner_id == user.id)
    elif owner_id:
        query = query.where(Deal.owner_id == owner_id)

    if client_id:
        query = query.where(Deal.client_id == client_id)
    if stage_id:
        query = query.where(Deal.stage_id == stage_id)
    if priority:
        query = query.where(Deal.priority == priority)

    count_q = select(func.count(func.distinct(Deal.id))).select_from(
        query.subquery()
    )
    total = (await db.execute(count_q)).scalar() or 0

    sortable = {"title", "amount", "priority", "probability", "created_at"}
    if sort_by not in sortable:
        sort_by = "created_at"
    sort_col = getattr(Deal, sort_by)
    order = sort_col.desc() if sort_order == "desc" else sort_col.asc()
    query = query.order_by(order).offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    deals = result.unique().scalars().all()

    return {
        "items": [DealResponse.model_validate(d).model_dump() for d in deals],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


async def get_kanban(
    user: User,
    db: AsyncSession,
    owner_id: UUID | None = None,
    client_id: UUID | None = None,
    priority: str | None = None,
) -> dict:
    """Канбан-вид — сделки сгруппированные по стадиям. Один запрос вместо N+1."""
    # все стадии по порядку
    stages_result = await db.execute(select(Stage).order_by(Stage.position))
    stages = stages_result.scalars().all()

    # один запрос на все сделки с фильтрами
    deals_query = (
        select(Deal)
        .options(
            joinedload(Deal.client),
            joinedload(Deal.owner),
            joinedload(Deal.tags),
        )
        .order_by(Deal.position)
    )

    # owner-based
    if user.role != "admin":
        deals_query = deals_query.where(Deal.owner_id == user.id)
    elif owner_id:
        deals_query = deals_query.where(Deal.owner_id == owner_id)

    if client_id:
        deals_query = deals_query.where(Deal.client_id == client_id)
    if priority:
        deals_query = deals_query.where(Deal.priority == priority)

    deals_result = await db.execute(deals_query)
    all_deals = deals_result.unique().scalars().all()

    # группируем в Python по stage_id
    deals_by_stage: dict[UUID, list] = {}
    for d in all_deals:
        deals_by_stage.setdefault(d.stage_id, []).append(d)

    columns = []
    for stage in stages:
        stage_deals = deals_by_stage.get(stage.id, [])
        cards = [KanbanCard.model_validate(d).model_dump() for d in stage_deals]
        total_amount = sum(d.amount or 0 for d in stage_deals)

        columns.append(
            KanbanColumn(
                id=stage.id,
                name=stage.name,
                color=stage.color,
                position=stage.position,
                is_won=stage.is_won,
                is_lost=stage.is_lost,
                deals=cards,
                total_amount=float(total_amount),
                deals_count=len(stage_deals),
            ).model_dump()
        )

    return KanbanResponse(stages=columns).model_dump()


async def update_deal(
    deal_id: UUID, data: DealUpdate, user: User, db: AsyncSession
) -> dict:
    """Обновление сделки."""
    deal = await _get_deal_or_404(deal_id, db)
    _check_access(deal, user)

    update_data = data.model_dump(exclude_unset=True)

    tag_ids = update_data.pop("tag_ids", None)
    if tag_ids is not None:
        result = await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
        deal.tags = list(result.scalars().all())

    # обновляем только допустимые поля — без id, owner_id, created_at, closed_at
    allowed = {"title", "client_id", "stage_id", "amount", "currency", "probability",
               "expected_close_date", "priority", "description"}
    for field, value in update_data.items():
        if field in allowed:
            setattr(deal, field, value)

    await db.flush()
    await db.refresh(deal)
    log.info("deal_updated", deal_id=str(deal_id))
    return DealResponse.model_validate(deal).model_dump()


async def delete_deal(
    deal_id: UUID, user: User, db: AsyncSession
) -> dict:
    """Удаление сделки."""
    deal = await _get_deal_or_404(deal_id, db)
    _check_access(deal, user)

    await db.delete(deal)
    await db.flush()
    log.info("deal_deleted", deal_id=str(deal_id))
    return {"message": "Сделка удалена"}


async def move_stage(
    deal_id: UUID, stage_id: UUID, position: int, user: User, db: AsyncSession
) -> dict:
    """Перемещение сделки на другую стадию (канбан drag & drop)."""
    deal = await _get_deal_or_404(deal_id, db)
    _check_access(deal, user)

    # проверяем что стадия существует
    stage_result = await db.execute(select(Stage).where(Stage.id == stage_id))
    stage = stage_result.scalar_one_or_none()
    if not stage:
        raise NotFoundError("Стадия не найдена")

    # обновляем стадию и позицию
    deal.stage_id = stage_id
    deal.position = position

    # логика closed_at — если стадия финальная
    if stage.is_won or stage.is_lost:
        deal.closed_at = datetime.now(UTC)
    else:
        deal.closed_at = None

    await db.flush()
    await db.refresh(deal)

    log.info(
        "deal_moved",
        deal_id=str(deal_id),
        stage=stage.name,
        is_won=stage.is_won,
        is_lost=stage.is_lost,
    )
    return DealResponse.model_validate(deal).model_dump()


# --- хелперы ---


async def _get_deal_or_404(deal_id: UUID, db: AsyncSession) -> Deal:
    """Ищем сделку или 404."""
    result = await db.execute(
        select(Deal)
        .options(
            joinedload(Deal.client),
            joinedload(Deal.stage),
            joinedload(Deal.owner),
            joinedload(Deal.tags),
        )
        .where(Deal.id == deal_id)
    )
    deal = result.unique().scalar_one_or_none()
    if not deal:
        raise NotFoundError("Сделка не найдена")
    return deal


def _check_access(deal: Deal, user: User) -> None:
    """Проверяем доступ — manager видит только свои сделки."""
    if user.role != "admin" and deal.owner_id != user.id:
        raise ForbiddenError("Нет доступа к этой сделке")
