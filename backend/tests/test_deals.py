"""Тесты сделок и стадий — CRUD, канбан, перемещение."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password
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
    mock_db.add = MagicMock()
    mock_db.delete = AsyncMock()
    mock_db.refresh = AsyncMock()

    async def override():
        yield mock_db

    app.dependency_overrides[get_db] = override
    return TestClient(app), mock_db


def test_create_deal_unauthorized():
    """Создание сделки без токена — 403."""
    mock_db = AsyncMock()

    async def override():
        yield mock_db

    app.dependency_overrides[get_db] = override
    client = TestClient(app)
    response = client.post("/api/v1/deals", json={"title": "Тест"})
    assert response.status_code == 403
    app.dependency_overrides.clear()


def test_create_deal_validation():
    """Создание сделки с пустым заголовком — 422."""
    user = _make_user()
    client, _ = _client_with_user(user)
    header = {"Authorization": f"Bearer {create_access_token(str(user.id))}"}

    response = client.post(
        "/api/v1/deals",
        json={
            "title": "  ",
            "client_id": str(uuid.uuid4()),
            "stage_id": str(uuid.uuid4()),
        },
        headers=header,
    )
    assert response.status_code == 422
    app.dependency_overrides.clear()


def test_stages_forbidden_for_manager():
    """Создание стадии manager-ом — 403."""
    user = _make_user("manager")
    client, _ = _client_with_user(user)
    header = {"Authorization": f"Bearer {create_access_token(str(user.id))}"}

    response = client.post(
        "/api/v1/stages",
        json={"name": "Тестовая стадия"},
        headers=header,
    )
    assert response.status_code == 403
    app.dependency_overrides.clear()


def test_move_stage_validation():
    """Перемещение сделки — невалидный UUID — 422."""
    user = _make_user()
    client, _ = _client_with_user(user)
    header = {"Authorization": f"Bearer {create_access_token(str(user.id))}"}

    response = client.patch(
        f"/api/v1/deals/{uuid.uuid4()}/stage",
        json={"stage_id": "not-a-uuid", "position": 0},
        headers=header,
    )
    assert response.status_code == 422
    app.dependency_overrides.clear()


def test_deal_priority_validation():
    """Создание сделки с невалидным приоритетом — 422."""
    user = _make_user()
    client, _ = _client_with_user(user)
    header = {"Authorization": f"Bearer {create_access_token(str(user.id))}"}

    response = client.post(
        "/api/v1/deals",
        json={
            "title": "Тест",
            "client_id": str(uuid.uuid4()),
            "stage_id": str(uuid.uuid4()),
            "priority": "super_urgent",
        },
        headers=header,
    )
    assert response.status_code == 422
    app.dependency_overrides.clear()
