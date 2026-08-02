"""Фикстуры для тестов — мок БД-сессия, тестовый клиент."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app


@pytest.fixture
def mock_db():
    """Мок-сессия БД — чтобы тесты не ходили в реальную базу."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def client(mock_db):
    """Тестовый HTTP-клиент с замоканной БД."""

    async def override_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
