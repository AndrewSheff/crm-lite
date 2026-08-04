"""Конфигурация приложения — все из переменных окружения через Pydantic Settings."""

import warnings

from pydantic_settings import BaseSettings

# Дефолтные значения для сравнения — ругнемся если не поменяли
_DEV_SECRET = "change-this-to-random-64-char-string"  # noqa: S105
_DEV_ADMIN_PASSWORD = "change_me_immediately"  # noqa: S105


class Settings(BaseSettings):
    # БД
    DATABASE_URL: str = "postgresql+asyncpg://crm_user:secret@localhost:5432/crm_lite"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = _DEV_SECRET
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Дефолтный админ
    ADMIN_EMAIL: str = "admin@crm-lite.local"
    ADMIN_PASSWORD: str = _DEV_ADMIN_PASSWORD  # noqa: S105

    # AI
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    AI_PROVIDER: str = "anthropic"
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    OPENAI_MODEL: str = "gpt-4o-mini"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # Приложение
    DEBUG: bool = False
    APP_VERSION: str = "1.0.0"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

# Ворнинги при дефолтных секретах — не забудь поменять перед деплоем
if settings.SECRET_KEY == _DEV_SECRET:
    warnings.warn(
        "SECRET_KEY не задан — используется дефолтное значение. "
        "Обязательно задайте уникальный ключ в .env перед деплоем!",
        UserWarning,
        stacklevel=1,
    )

if settings.ADMIN_PASSWORD == _DEV_ADMIN_PASSWORD:
    warnings.warn(
        "ADMIN_PASSWORD не изменен — используется дефолтный пароль. "
        "Задайте надежный пароль в .env!",
        UserWarning,
        stacklevel=1,
    )
