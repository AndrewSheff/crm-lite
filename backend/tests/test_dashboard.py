"""Тесты дашборда и экспорта — базовые проверки эндпоинтов."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.database import get_db
from app.main import app
from app.models.user import User


def _make_user(role="manager"):
    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.email = f"{role}@example.com"
    user.name = f"Тест {role}"
    user.hashed_password = hash_password("password123")
    user.role = role
    user.is_active = True
    user.must_change_password = False
    user.avatar_url = None
    user.created_at = datetime.now(UTC)
    user.updated_at = datetime.now(UTC)
    return user


def _client_with_user(user):
    mock_db = AsyncMock()
    user_result = MagicMock()
    user_result.scalar_one_or_none.return_value = user
    mock_db.execute = AsyncMock(return_value=user_result)
    mock_db.flush = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()

    async def override():
        yield mock_db

    app.dependency_overrides[get_db] = override
    return TestClient(app), mock_db


def test_dashboard_stats_unauthorized():
    """Дашборд без токена — 403."""
    mock_db = AsyncMock()

    async def override():
        yield mock_db

    app.dependency_overrides[get_db] = override
    client = TestClient(app)
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 403
    app.dependency_overrides.clear()


def test_export_clients_unauthorized():
    """Экспорт без токена — 403."""
    mock_db = AsyncMock()

    async def override():
        yield mock_db

    app.dependency_overrides[get_db] = override
    client = TestClient(app)
    response = client.get("/api/v1/export/clients")
    assert response.status_code == 403
    app.dependency_overrides.clear()


def test_export_deals_unauthorized():
    """Экспорт сделок без токена — 403."""
    mock_db = AsyncMock()

    async def override():
        yield mock_db

    app.dependency_overrides[get_db] = override
    client = TestClient(app)
    response = client.get("/api/v1/export/deals")
    assert response.status_code == 403
    app.dependency_overrides.clear()


def test_ai_summary_unauthorized():
    """AI-резюме без токена — 403."""
    mock_db = AsyncMock()

    async def override():
        yield mock_db

    app.dependency_overrides[get_db] = override
    client = TestClient(app)
    response = client.post(f"/api/v1/deals/{uuid.uuid4()}/ai-summary")
    assert response.status_code == 403
    app.dependency_overrides.clear()
