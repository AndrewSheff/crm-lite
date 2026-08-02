"""Сервис аналитики — статистика, воронка, график выручки, лента активности."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import extract, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.client import Client
from app.models.deal import Deal
from app.models.stage import Stage
from app.models.user import User
from app.schemas.dashboard import (
    ActivityFeedItem,
    ActivityFeedResponse,
    DashboardStats,
    PipelineResponse,
    PipelineStage,
    RevenueChartPoint,
    RevenueChartResponse,
)


def _add_filters(query, *filters):
    """Добавляем фильтры к запросу, пропуская None (admin видит все)."""
    for f in filters:
        if f is not None:
            query = query.where(f)
    return query


async def get_stats(
    user: User, db: AsyncSession, period_days: int = 30
) -> dict:
    """Общая статистика — клиенты, сделки, выручка, конверсия."""
    since = datetime.now(UTC) - timedelta(days=period_days)

    # owner-based фильтр — None для admin (без ограничений)
    owner_filter = None if user.role == "admin" else (Client.owner_id == user.id)
    deal_owner_filter = None if user.role == "admin" else (Deal.owner_id == user.id)

    # клиенты
    q = select(func.count(Client.id))
    q = _add_filters(q, owner_filter)
    total_clients = (await db.execute(q)).scalar() or 0

    q = select(func.count(Client.id))
    q = _add_filters(q, owner_filter, Client.created_at >= since)
    new_clients = (await db.execute(q)).scalar() or 0

    # активные сделки
    q = select(func.count(Deal.id))
    q = _add_filters(q, deal_owner_filter, Deal.closed_at.is_(None))
    active_deals = (await db.execute(q)).scalar() or 0

    # выигранные/проигранные за период
    won_q = (
        select(func.count(Deal.id))
        .join(Stage, Deal.stage_id == Stage.id)
    )
    won_q = _add_filters(won_q, deal_owner_filter, Stage.is_won.is_(True), Deal.closed_at >= since)
    won_deals = (await db.execute(won_q)).scalar() or 0

    lost_q = (
        select(func.count(Deal.id))
        .join(Stage, Deal.stage_id == Stage.id)
    )
    lost_q = _add_filters(lost_q, deal_owner_filter, Stage.is_lost.is_(True), Deal.closed_at >= since)
    lost_deals = (await db.execute(lost_q)).scalar() or 0

    # выручка (сумма won сделок)
    revenue_q = (
        select(func.coalesce(func.sum(Deal.amount), 0))
        .join(Stage, Deal.stage_id == Stage.id)
    )
    revenue_q = _add_filters(revenue_q, deal_owner_filter, Stage.is_won.is_(True), Deal.closed_at >= since)
    total_revenue = float((await db.execute(revenue_q)).scalar() or 0)

    # средний чек
    avg_deal_size = total_revenue / won_deals if won_deals > 0 else 0.0

    # конверсия
    closed_total = won_deals + lost_deals
    conversion_rate = (won_deals / closed_total * 100) if closed_total > 0 else 0.0

    # средний цикл сделки (дни от created_at до closed_at для won)
    cycle_q = (
        select(
            func.avg(
                extract("epoch", Deal.closed_at - Deal.created_at) / 86400
            )
        )
        .join(Stage, Deal.stage_id == Stage.id)
    )
    cycle_q = _add_filters(cycle_q, deal_owner_filter, Stage.is_won.is_(True), Deal.closed_at.is_not(None))
    avg_cycle = (await db.execute(cycle_q)).scalar() or 0

    return DashboardStats(
        total_clients=total_clients,
        new_clients=new_clients,
        active_deals=active_deals,
        won_deals=won_deals,
        lost_deals=lost_deals,
        total_revenue=total_revenue,
        avg_deal_size=round(avg_deal_size, 2),
        conversion_rate=round(conversion_rate, 1),
        avg_deal_cycle_days=int(avg_cycle),
    ).model_dump()


async def get_pipeline(user: User, db: AsyncSession) -> dict:
    """Данные воронки — стадии с кол-вом и суммой сделок."""
    # для pipeline используем outerjoin с условием
    if user.role == "admin":
        join_cond = Deal.stage_id == Stage.id
    else:
        join_cond = (Deal.stage_id == Stage.id) & (Deal.owner_id == user.id)

    query = (
        select(
            Stage.name,
            Stage.color,
            func.count(Deal.id).label("count"),
            func.coalesce(func.sum(Deal.amount), 0).label("amount"),
        )
        .outerjoin(Deal, join_cond)
        .group_by(Stage.id, Stage.name, Stage.color, Stage.position)
        .order_by(Stage.position)
    )

    result = await db.execute(query)
    rows = result.all()

    stages = [
        PipelineStage(
            name=row.name,
            count=row.count,
            amount=float(row.amount),
            color=row.color,
        )
        for row in rows
    ]

    return PipelineResponse(stages=stages).model_dump()


async def get_revenue_chart(
    user: User, db: AsyncSession, period_days: int = 90
) -> dict:
    """График выручки — помесячно за период."""
    since = datetime.now(UTC) - timedelta(days=period_days)
    deal_owner_filter = None if user.role == "admin" else (Deal.owner_id == user.id)

    query = (
        select(
            func.to_char(Deal.closed_at, "YYYY-MM").label("month"),
            func.coalesce(func.sum(Deal.amount), 0).label("revenue"),
            func.count(Deal.id).label("deals_count"),
        )
        .join(Stage, Deal.stage_id == Stage.id)
    )
    query = _add_filters(
        query, deal_owner_filter, Stage.is_won.is_(True), Deal.closed_at >= since
    )
    query = (
        query
        .group_by(func.to_char(Deal.closed_at, "YYYY-MM"))
        .order_by(func.to_char(Deal.closed_at, "YYYY-MM"))
    )

    result = await db.execute(query)
    rows = result.all()

    data = [
        RevenueChartPoint(
            date=row.month, revenue=float(row.revenue), deals_count=row.deals_count
        )
        for row in rows
    ]

    return RevenueChartResponse(data=data).model_dump()


async def get_activity_feed(
    user: User, db: AsyncSession, limit: int = 10
) -> dict:
    """Лента последних активностей — JOIN вместо subquery, owner-based доступ."""
    query = (
        select(
            Activity.id,
            Activity.type,
            Activity.title,
            Activity.created_at,
            func.coalesce(User.name, "Неизвестный").label("author_name"),
        )
        .outerjoin(User, Activity.author_id == User.id)
        .order_by(Activity.created_at.desc())
    )

    # owner-based: менеджер видит только свои активности
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

    query = query.limit(limit)
    result = await db.execute(query)
    rows = result.all()

    items = [
        ActivityFeedItem(
            id=str(row.id),
            type=row.type,
            title=row.title,
            author_name=row.author_name,
            created_at=row.created_at.isoformat(),
        )
        for row in rows
    ]

    return ActivityFeedResponse(items=items).model_dump()
