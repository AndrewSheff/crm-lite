"""Роутер дашборда — аналитика, воронка, выручка, лента."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_stats(
    period_days: int = Query(30, ge=1, le=365),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Общая статистика за период."""
    return await dashboard_service.get_stats(user, db, period_days)


@router.get("/pipeline")
async def get_pipeline(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Данные воронки продаж."""
    return await dashboard_service.get_pipeline(user, db)


@router.get("/revenue-chart")
async def get_revenue_chart(
    period_days: int = Query(90, ge=1, le=730),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """График выручки по месяцам."""
    return await dashboard_service.get_revenue_chart(user, db, period_days)


@router.get("/activity-feed")
async def get_activity_feed(
    limit: int = Query(10, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Лента последних активностей."""
    return await dashboard_service.get_activity_feed(user, db, limit)
