"""Тесты авторизации — регистрация, логин, рефреш, смена пароля, me."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password
from app.database import get_db
from app.main import app
from app.models.user import User

# --- фикстуры ---

def _make_user(**overrides) -> MagicMock:
    """Создаем мок юзера для тестов."""
    user = MagicMock(spec=User)
    user.id = overrides.get("id", uuid.uuid4())
    user.email = overrides.get("email", "test@example.com")
    user.name = overrides.get("name", "Тестовый Юзер")
    user.hashed_password = overrides.get(
        "hashed_password", hash_password("password123")
    )
    user.role = overrides.get("role", "manager")
    user.is_active = overrides.get("is_active", True)
    user.must_change_password = overrides.get("must_change_password", False)
    user.avatar_url = overrides.get("avatar_url", None)
    user.created_at = overrides.get("created_at", datetime.now(UTC))
    user.updated_at = overrides.get("updated_at", datetime.now(UTC))
    return user


@pytest.fixture
def test_user():
    return _make_user()


@pytest.fixture
def admin_user():
    return _make_user(role="admin", email="admin@example.com", name="Админ")


@pytest.fixture
def auth_header(test_user):
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_header(admin_user):
    token = create_access_token(str(admin_user.id))
    return {"Authorization": f"Bearer {token}"}


def _mock_db_with_user(user):
    """Создаем мок сессии БД, которая возвращает нужного юзера."""
    mock_db = AsyncMock()

    # мокаем результат execute().scalar_one_or_none()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_result.scalars.return_value.all.return_value = [user] if user else []
    mock_db.execute.return_value = mock_result

    mock_db.flush = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.add = MagicMock()

    return mock_db


def _client_with_db(mock_db):
    """Создаем тест-клиент с замоканной БД."""
    async def override():
        yield mock_db

    app.dependency_overrides[get_db] = override
    client = TestClient(app)
    return client


# --- тесты регистрации ---

def test_register_success(test_user):
    """Регистрация — 201 с токенами."""
    mock_db = _mock_db_with_user(None)  # email не занят

    # после flush юзер получает id
    def side_effect(user):
        user.id = uuid.uuid4()
        user.created_at = datetime.now(UTC)
        user.updated_at = datetime.now(UTC)
        user.is_active = True
        user.must_change_password = False
        user.role = "manager"
        user.avatar_url = None

    mock_db.add.side_effect = side_effect

    client = _client_with_db(mock_db)
    response = client.post("/api/v1/auth/register", json={
        "email": "new@example.com",
        "name": "Новый Юзер",
        "password": "password123",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "new@example.com"

    app.dependency_overrides.clear()


def test_register_duplicate_email(test_user):
    """Регистрация — 409 если email занят."""
    mock_db = _mock_db_with_user(test_user)  # email уже есть

    client = _client_with_db(mock_db)
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "name": "Дубликат",
        "password": "password123",
    })
    assert response.status_code == 409

    app.dependency_overrides.clear()


# --- тесты логина ---

def test_login_success(test_user):
    """Логин — 200 с токенами и данными юзера."""
    mock_db = _mock_db_with_user(test_user)

    client = _client_with_db(mock_db)
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"

    app.dependency_overrides.clear()


def test_login_wrong_password(test_user):
    """Логин — 401 при неверном пароле."""
    mock_db = _mock_db_with_user(test_user)

    client = _client_with_db(mock_db)
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "wrong_password",
    })
    assert response.status_code == 401

    app.dependency_overrides.clear()


def test_login_nonexistent_user():
    """Логин — 401 если юзер не найден."""
    mock_db = _mock_db_with_user(None)

    client = _client_with_db(mock_db)
    response = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "password123",
    })
    assert response.status_code == 401

    app.dependency_overrides.clear()


# --- тест рефреша ---

def test_refresh_success(test_user):
    """Рефреш — 200 с новой парой токенов."""
    from app.core.security import create_refresh_token

    refresh_token = create_refresh_token(str(test_user.id))
    mock_db = _mock_db_with_user(test_user)

    client = _client_with_db(mock_db)
    response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    app.dependency_overrides.clear()


# --- тест me ---

def test_me_success(test_user, auth_header):
    """GET /me — данные текущего юзера."""
    mock_db = _mock_db_with_user(test_user)

    client = _client_with_db(mock_db)
    response = client.get("/api/v1/auth/me", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

    app.dependency_overrides.clear()


def test_me_unauthorized():
    """GET /me без токена — 403."""
    mock_db = _mock_db_with_user(None)
    client = _client_with_db(mock_db)
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403

    app.dependency_overrides.clear()


# --- тест change-password ---

def test_change_password_success(test_user, auth_header):
    """Смена пароля — 200."""
    mock_db = _mock_db_with_user(test_user)

    client = _client_with_db(mock_db)
    response = client.post("/api/v1/auth/change-password", headers=auth_header, json={
        "current_password": "password123",
        "new_password": "newpassword456",
    })
    assert response.status_code == 200

    app.dependency_overrides.clear()


def test_change_password_wrong_current(test_user, auth_header):
    """Смена пароля с неверным текущим — 401."""
    mock_db = _mock_db_with_user(test_user)

    client = _client_with_db(mock_db)
    response = client.post("/api/v1/auth/change-password", headers=auth_header, json={
        "current_password": "wrong_password",
        "new_password": "newpassword456",
    })
    assert response.status_code == 401

    app.dependency_overrides.clear()


# --- тест users (admin) ---

def test_users_list_admin(admin_user, admin_header):
    """GET /users — доступен только admin."""
    mock_db = _mock_db_with_user(admin_user)

    # мокаем count запрос
    count_result = MagicMock()
    count_result.scalar.return_value = 1

    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = [admin_user]

    # первый execute — select user by id (auth), второй — count, третий — list
    user_result = MagicMock()
    user_result.scalar_one_or_none.return_value = admin_user

    mock_db.execute = AsyncMock(
        side_effect=[user_result, count_result, list_result]
    )

    client = _client_with_db(mock_db)
    response = client.get("/api/v1/users", headers=admin_header)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

    app.dependency_overrides.clear()


def test_users_list_forbidden(test_user, auth_header):
    """GET /users — 403 для manager."""
    mock_db = _mock_db_with_user(test_user)

    client = _client_with_db(mock_db)
    response = client.get("/api/v1/users", headers=auth_header)
    assert response.status_code == 403

    app.dependency_overrides.clear()


# --- тест валидации ---

def test_register_short_password():
    """Регистрация с коротким паролем — 422."""
    mock_db = _mock_db_with_user(None)
    client = _client_with_db(mock_db)
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "name": "Тест",
        "password": "123",
    })
    assert response.status_code == 422

    app.dependency_overrides.clear()
