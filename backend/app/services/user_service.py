"""Сервис управления пользователями — CRUD для админа."""

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import get_logger
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

log = get_logger(__name__)


async def list_users(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    search: str | None = None,
) -> dict:
    """Список юзеров — пагинация + поиск по имени/email."""
    query = select(User)

    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(User.name.ilike(pattern), User.email.ilike(pattern))
        )

    # считаем общее кол-во
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # пагинация
    query = query.order_by(User.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    users = result.scalars().all()

    return {
        "items": [UserResponse.model_validate(u).model_dump() for u in users],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


async def get_user(user_id: UUID, db: AsyncSession) -> dict:
    """Юзер по ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("Пользователь не найден")
    return UserResponse.model_validate(user).model_dump()


async def create_user(data: UserCreate, db: AsyncSession) -> dict:
    """Создание юзера админом — с временным паролем и must_change_password."""
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise ConflictError("Пользователь с таким email уже существует")

    user = User(
        email=data.email,
        name=data.name,
        hashed_password=hash_password(data.password),
        role=data.role,
        must_change_password=True,
    )
    db.add(user)
    await db.flush()

    log.info("user_created_by_admin", user_id=str(user.id), email=user.email)
    return UserResponse.model_validate(user).model_dump()


async def block_user(user_id: UUID, db: AsyncSession) -> dict:
    """Блокировка/разблокировка юзера (toggle)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("Пользователь не найден")

    user.is_active = not user.is_active
    await db.flush()

    action = "unblocked" if user.is_active else "blocked"
    log.info(f"user_{action}", user_id=str(user.id))
    return UserResponse.model_validate(user).model_dump()
