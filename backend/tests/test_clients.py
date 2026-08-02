"""Тесты клиентов и тегов — CRUD, поиск, owner-based доступ."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password
from app.database import get_db
from app.main import app
from app.models.client import Client
from app.models.tag import Tag
from app.models.user import User


def _make_user(role="manager"):
    """Мок юзера."""
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


def _make_tag(name="VIP", color="#ef4444"):
    """Мок тега."""
    tag = MagicMock(spec=Tag)
    tag.id = uuid.uuid4()
    tag.name = name
    tag.color = color
    tag.created_at = datetime.now(UTC)
    return tag


def _make_client(owner):
    """Мок клиента."""
    client = MagicMock(spec=Client)
    client.id = uuid.uuid4()
    client.name = "ООО Тест"
    client.email = "info@test.ru"
    client.phone = "+7 999 123-45-67"
    client.company = "ООО Тест"
    client.industry = "IT"
    client.website = None
    client.address = None
    client.status = "lead"
    client.source = "Сайт"
    client.owner_id = owner.id
    client.owner = owner
    client.tags = []
    client.created_at = datetime.now(UTC)
    client.updated_at = datetime.now(UTC)
    return client


@pytest.fixture
def manager():
    return _make_user("manager")


@pytest.fixture
def admin():
    return _make_user("admin")


@pytest.fixture
def manager_header(manager):
    return {"Authorization": f"Bearer {create_access_token(str(manager.id))}"}


@pytest.fixture
def admin_header(admin):
    return {"Authorization": f"Bearer {create_access_token(str(admin.id))}"}


def _client_with_user_in_db(user):
    """Тест-клиент с БД, которая находит юзера при аутентификации."""
    mock_db = AsyncMock()

    # get_current_user делает select User by id
    user_result = MagicMock()
    user_result.scalar_one_or_none.return_value = user

    # по умолчанию все execute возвращают юзера
    mock_db.execute = AsyncMock(return_value=user_result)
    mock_db.flush = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.delete = AsyncMock()

    async def override():
        yield mock_db

    app.dependency_overrides[get_db] = override
    return TestClient(app), mock_db


# --- тесты тегов ---


def test_create_tag(admin, admin_header):
    """Создание тега — 201."""
    client, mock_db = _client_with_user_in_db(admin)

    # 1й execute = auth, 2й = check existing (None), 3й = flush
    existing_result = MagicMock()
    existing_result.scalar_one_or_none.return_value = None

    user_result = MagicMock()
    user_result.scalar_one_or_none.return_value = admin

    tag_mock = _make_tag()

    mock_db.execute = AsyncMock(side_effect=[user_result, existing_result])
    def _add_tag(t):
        t.id = tag_mock.id
        t.created_at = tag_mock.created_at

    mock_db.add = MagicMock(side_effect=_add_tag)

    response = client.post("/api/v1/tags", json={"name": "VIP", "color": "#ef4444"}, headers=admin_header)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "VIP"

    app.dependency_overrides.clear()


# --- тесты клиентов ---


def test_create_client_unauthorized():
    """Создание клиента без токена — 403."""
    mock_db = AsyncMock()
    async def override():
        yield mock_db
    app.dependency_overrides[get_db] = override

    client = TestClient(app)
    response = client.post("/api/v1/clients", json={"name": "Тест"})
    assert response.status_code == 403

    app.dependency_overrides.clear()


def test_create_client_validation():
    """Создание клиента с пустым именем — 422."""
    user = _make_user()
    client, _ = _client_with_user_in_db(user)
    header = {"Authorization": f"Bearer {create_access_token(str(user.id))}"}

    response = client.post("/api/v1/clients", json={"name": "  "}, headers=header)
    assert response.status_code == 422

    app.dependency_overrides.clear()


def test_register_short_password_validation():
    """Тест валидации клиентского статуса."""
    user = _make_user()
    client, _ = _client_with_user_in_db(user)
    header = {"Authorization": f"Bearer {create_access_token(str(user.id))}"}

    response = client.post("/api/v1/clients", json={"name": "Тест", "status": "invalid_status"}, headers=header)
    assert response.status_code == 422

    app.dependency_overrides.clear()
