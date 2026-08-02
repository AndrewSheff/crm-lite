"""Сервис активностей — CRUD, завершение, фильтрация с owner-based доступом."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.activity import Activity
from app.models.client import Client
from app.models.deal import Deal
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityResponse


async def list_activities(
    db: AsyncSession,
    user: User,
    page: int = 1,
    per_page: int = 20,
    client_id: UUID | None = None,
    deal_id: UUID | None = None,
    activity_type: str | None = None,
    is_completed: bool | None = None,
) -> dict:
    """Список активностей с фильтрами и owner-based доступом."""
    query = select(Activity).options(joinedload(Activity.author))

    if client_id:
        query = query.where(Activity.client_id == client_id)
    if deal_id:
        query = query.where(Activity.deal_id == deal_id)
    if activity_type:
        query = query.where(Activity.type == activity_type)
    if is_completed is not None:
        query = query.where(Activity.is_completed == is_completed)

    # owner-based: менеджер видит только активности по своим клиентам/сделкам
    if user.role != "admin":
        query = query.where(
            or_(
                Activity.client_id.in_(
                    select(Client.id).where(Client.owner_id == user.id)
                ),
                Activity.deal_id.in_(
                    select(Deal.id).where(Deal.owner_id == user.id)
                ),
                Activity.author_id == user.id,
            )
        )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    query = query.order_by(Activity.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    activities = result.unique().scalars().all()

    return {
        "items": [
            ActivityResponse.model_validate(a).model_dump() for a in activities
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


async def create_activity(
    data: ActivityCreate, user: User, db: AsyncSession
) -> dict:
    """Создание активности."""
    activity = Activity(
        type=data.type,
        title=data.title,
        description=data.description,
        author_id=user.id,
        client_id=data.client_id,
        deal_id=data.deal_id,
        scheduled_at=data.scheduled_at,
    )
    db.add(activity)
    await db.flush()
    await db.refresh(activity)
    return ActivityResponse.model_validate(activity).model_dump()


async def complete_activity(
    activity_id: UUID, user: User, db: AsyncSession
) -> dict:
    """Завершение активности — ставим is_completed и completed_at."""
    activity = await _get_activity_or_404(activity_id, db)
    _check_access(activity, user)

    activity.is_completed = True
    activity.completed_at = datetime.now(UTC)
    await db.flush()
    return ActivityResponse.model_validate(activity).model_dump()


async def delete_activity(
    activity_id: UUID, user: User, db: AsyncSession
) -> dict:
    """Удаление активности."""
    activity = await _get_activity_or_404(activity_id, db)
    _check_access(activity, user)

    await db.delete(activity)
    await db.flush()
    return {"message": "Активность удалена"}


async def _get_activity_or_404(
    activity_id: UUID, db: AsyncSession
) -> Activity:
    result = await db.execute(
        select(Activity)
        .options(joinedload(Activity.author))
        .where(Activity.id == activity_id)
    )
    activity = result.unique().scalar_one_or_none()
    if not activity:
        raise NotFoundError("Активность не найдена")
    return activity


def _check_access(activity: Activity, user: User) -> None:
    if user.role != "admin" and activity.author_id != user.id:
        raise ForbiddenError("Нет доступа к этой активности")
