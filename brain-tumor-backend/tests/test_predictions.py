"""Automated tests for prediction and model comparison endpoints."""

import io
from fastapi.testclient import TestClient


def test_predict_valid_jpeg(client: TestClient, valid_mri_image_bytes: bytes):
    """Test standard prediction on valid JPEG brain MRI image."""
    response = client.post(
        "/api/v1/predictions",
        data={"model_id": "hybrid_v1", "save_image": "false"},
        files={"file": ("brain_mri.jpg", valid_mri_image_bytes, "image/jpeg")},
    )
    assert response.status_code == 201
    data = response.json()
    assert "prediction_id" in data
    assert data["model_id"] == "hybrid_v1"
    assert data["predicted_class"] in ["glioma", "meningioma", "notumor", "pituitary"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert len(data["class_probabilities"]) == 4
    assert sum(data["class_probabilities"].values()) > 0.99
    assert data["inference_time_ms"] > 0
    assert len(data["warnings"]) >= 1


def test_predict_valid_png(client: TestClient, valid_png_image_bytes: bytes):
    """Test prediction on valid PNG brain MRI scan."""
    response = client.post(
        "/api/v1/predictions",
        data={"model_id": "hybrid_v1_final", "save_image": "false"},
        files={"file": ("brain_scan.png", valid_png_image_bytes, "image/png")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["model_id"] == "hybrid_v1_final"
    assert data["confidence"] > 0.0


def test_predict_invalid_model_id(client: TestClient, valid_mri_image_bytes: bytes):
    """Test prediction with non-existent model ID returns 404."""
    response = client.post(
        "/api/v1/predictions",
        data={"model_id": "unknown_model_xyz", "save_image": "false"},
        files={"file": ("brain_mri.jpg", valid_mri_image_bytes, "image/jpeg")},
    )
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "MODEL_NOT_FOUND"


def test_predict_corrupt_image(client: TestClient, corrupt_image_bytes: bytes):
    """Test uploading corrupt image bytes returns 400 Bad Request."""
    response = client.post(
        "/api/v1/predictions",
        data={"model_id": "hybrid_v1", "save_image": "false"},
        files={"file": ("corrupt.jpg", corrupt_image_bytes, "image/jpeg")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "INVALID_IMAGE"


def test_predict_unsupported_file_extension(client: TestClient):
    """Test uploading an unsupported file type (.pdf or .txt) returns 400."""
    response = client.post(
        "/api/v1/predictions",
        data={"model_id": "hybrid_v1", "save_image": "false"},
        files={"file": ("document.pdf", b"%PDF-1.4 sample content", "application/pdf")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "INVALID_IMAGE"


def test_predict_empty_file(client: TestClient):
    """Test uploading empty (0 byte) file returns 400."""
    response = client.post(
        "/api/v1/predictions",
        data={"model_id": "hybrid_v1", "save_image": "false"},
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "INVALID_IMAGE"


def test_predict_oversized_file(client: TestClient, monkeypatch):
    """Test uploading file exceeding configured size threshold returns 400."""
    # Temporarily set max size to 100 bytes for testing
    from app.config import settings
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 1 / (1024 * 1024 * 10))  # ~0.1 bytes

    response = client.post(
        "/api/v1/predictions",
        data={"model_id": "hybrid_v1", "save_image": "false"},
        files={"file": ("toolarge.jpg", b"A" * 500, "image/jpeg")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "INVALID_IMAGE"


def test_compare_models_endpoint(client: TestClient, valid_mri_image_bytes: bytes):
    """Test /api/v1/predictions/compare across multiple models."""
    response = client.post(
        "/api/v1/predictions/compare",
        data={"model_ids": "hybrid_v1,hybrid_v1_final,hybrid_v2_finetuned"},
        files={"file": ("brain_mri.jpg", valid_mri_image_bytes, "image/jpeg")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "comparison_id" in data
    assert len(data["results"]) == 3
    for res in data["results"]:
        assert res["status"] in ("completed", "loaded")
        assert res["predicted_class"] in ["glioma", "meningioma", "notumor", "pituitary"]
        assert 0.0 <= res["confidence"] <= 1.0
