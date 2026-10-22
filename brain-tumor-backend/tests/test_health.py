"""Tests for system health check endpoints."""

from fastapi.testclient import TestClient
from unittest.mock import patch
from app.db.database import get_db


def test_root_health_check_healthy(client: TestClient):
    """Test /health endpoint returns 200 and healthy metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert data["database"] == "connected"
    assert data["total_models_count"] >= 3
    assert "models" in data
    assert "timestamp" in data


def test_v1_health_check(client: TestClient):
    """Test /api/v1/health returns matching healthy payload."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["database"] == "connected"


def test_health_check_db_failure(client: TestClient):
    """Test /health returns 503 when database connection raises exception."""
    class BrokenSession:
        def execute(self, *args, **kwargs):
            raise Exception("Database connection timeout")

    def broken_db_override():
        yield BrokenSession()

    from app.main import app
    app.dependency_overrides[get_db] = broken_db_override
    try:
        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "error" in data["database"]
    finally:
        app.dependency_overrides.clear()
