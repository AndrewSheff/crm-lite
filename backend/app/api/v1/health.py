"""Хелсчек — статус приложения, БД и Redis."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.database import async_session

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Проверка здоровья системы — БД и Redis."""
    db_status = "connected"
    redis_status = "connected"

    # Проверяем БД
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    # Проверяем Redis
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.aclose()
    except Exception:
        redis_status = "disconnected"

    status = "healthy" if db_status == "connected" and redis_status == "connected" else "degraded"

    body = {
        "status": status,
        "database": db_status,
        "redis": redis_status,
        "version": settings.APP_VERSION,
    }
    status_code = 200 if status == "healthy" else 503
    return JSONResponse(content=body, status_code=status_code)
