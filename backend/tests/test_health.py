"""Тест хелсчека — минимальная проверка что приложение стартует."""


def test_health_endpoint(client):
    """GET /api/v1/health — должен вернуть JSON со статусом и версией."""
    response = client.get("/api/v1/health")
    # без реальной БД и Redis будет degraded (503) — это ок для юнит-тестов
    assert response.status_code in (200, 503)
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert "version" in data
    assert "database" in data
    assert "redis" in data
