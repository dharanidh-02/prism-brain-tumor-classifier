"""Tests for model registry endpoints."""

from fastapi.testclient import TestClient


def test_list_models_returns_all_registered(client: TestClient):
    """Test /api/v1/models returns the registered models."""
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    model_ids = [m["model_id"] for m in data]
    assert "hybrid_v1" in model_ids
    assert "hybrid_v1_final" in model_ids
    assert "hybrid_v2_finetuned" in model_ids


def test_get_valid_model_details(client: TestClient):
    """Test /api/v1/models/{model_id} returns detailed metadata."""
    response = client.get("/api/v1/models/hybrid_v1")
    assert response.status_code == 200
    data = response.json()
    assert data["model_id"] == "hybrid_v1"
    assert "EfficientNetB0" in data["display_name"]
    assert data["input_shape"] == [None, 224, 224, 3]
    assert data["output_shape"] == [None, 4]
    assert data["parameter_count"] is not None


def test_get_invalid_model_returns_404(client: TestClient):
    """Test requesting a non-existent model ID returns 404."""
    response = client.get("/api/v1/models/non_existent_model_id")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "MODEL_NOT_FOUND"


def test_get_model_status(client: TestClient):
    """Test /api/v1/models/{model_id}/status returns operational status."""
    response = client.get("/api/v1/models/hybrid_v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["model_id"] == "hybrid_v1"
    assert "is_operational" in data
    assert "last_checked_at" in data
