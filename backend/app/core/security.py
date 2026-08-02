"""JWT-токены, bcrypt, зависимости авторизации для FastAPI."""

import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.database import get_db
from app.models.user import User

ALGORITHM = "HS256"
security_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    """Хешируем пароль через bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Проверяем пароль — совпадает ли с хешем."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: str) -> str:
    """Генерируем access JWT."""
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": user_id, "exp": expire, "type": "access"},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


def create_refresh_token(user_id: str) -> str:
    """Генерируем refresh JWT."""
    expire = datetime.now(UTC) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    return jwt.encode(
        {"sub": user_id, "exp": expire, "type": "refresh"},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_token(token: str, expected_type: str = "access") -> str:
    """Декодируем JWT, возвращаем user_id. Кидает UnauthorizedError если что-то не так."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if user_id is None or token_type != expected_type:
            raise UnauthorizedError("Невалидный токен")
        return user_id
    except JWTError:
        raise UnauthorizedError("Невалидный или просроченный токен") from None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Зависимость — достаем текущего юзера из JWT."""
    user_id = decode_token(credentials.credentials)
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise UnauthorizedError("Невалидный токен") from None

    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if user is None:
        raise UnauthorizedError("Пользователь не найден")
    if not user.is_active:
        raise ForbiddenError("Аккаунт заблокирован")
    return user


def require_role(*roles: str):
    """Фабрика зависимостей — проверяет роль юзера."""

    async def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise ForbiddenError("Недостаточно прав")
        return user

    return checker
