"""Конфигурация приложения — все из переменных окружения через Pydantic Settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # БД
    DATABASE_URL: str = "postgresql+asyncpg://crm_user:secret@localhost:5432/crm_lite"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "change-this-to-random-64-char-string"  # noqa: S105
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Дефолтный админ
    ADMIN_EMAIL: str = "admin@crm-lite.local"
    ADMIN_PASSWORD: str = "change_me_immediately"  # noqa: S105

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
