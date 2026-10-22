"""Automated tests for prediction history and CSV export."""

import csv
import io
from fastapi.testclient import TestClient


def _create_prediction(client: TestClient, image_bytes: bytes, model_id="hybrid_v1"):
    res = client.post(
        "/api/v1/predictions",
        data={"model_id": model_id, "save_image": "false"},
        files={"file": ("test.jpg", image_bytes, "image/jpeg")},
    )
    assert res.status_code == 201
    return res.json()


def test_history_pagination_and_retrieval(client: TestClient, valid_mri_image_bytes: bytes):
    """Test history list with limit and offset pagination."""
    # Create 3 predictions
    for _ in range(3):
        _create_prediction(client, valid_mri_image_bytes)

    response = client.get("/api/v1/history?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["offset"] == 0

    # Retrieve page 2
    res_page2 = client.get("/api/v1/history?limit=2&offset=2")
    assert res_page2.status_code == 200
    assert len(res_page2.json()["items"]) >= 1


def test_history_filtering_by_model(client: TestClient, valid_mri_image_bytes: bytes):
    """Test filtering history items by model_id."""
    _create_prediction(client, valid_mri_image_bytes, model_id="hybrid_v1")
    _create_prediction(client, valid_mri_image_bytes, model_id="hybrid_v1_final")

    res = client.get("/api/v1/history?model_id=hybrid_v1_final")
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) >= 1
    assert all(i["model_id"] == "hybrid_v1_final" for i in items)


def test_get_single_prediction_history(client: TestClient, valid_mri_image_bytes: bytes):
    """Test retrieving an individual prediction by ID."""
    created = _create_prediction(client, valid_mri_image_bytes)
    pid = created["prediction_id"]

    res = client.get(f"/api/v1/history/{pid}")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == pid
    assert data["model_id"] == created["model_id"]


def test_get_missing_prediction_returns_404(client: TestClient):
    """Test retrieving non-existent prediction ID returns 404."""
    res = client.get("/api/v1/history/999999")
    assert res.status_code == 404
    assert res.json()["error"] == "RESOURCE_NOT_FOUND"


def test_delete_prediction(client: TestClient, valid_mri_image_bytes: bytes):
    """Test deleting an existing prediction record."""
    created = _create_prediction(client, valid_mri_image_bytes)
    pid = created["prediction_id"]

    del_res = client.delete(f"/api/v1/history/{pid}")
    assert del_res.status_code == 200

    # Confirm record is gone
    get_res = client.get(f"/api/v1/history/{pid}")
    assert get_res.status_code == 404


def test_export_csv_endpoint(client: TestClient, valid_mri_image_bytes: bytes):
    """Test CSV export formatting and headers."""
    _create_prediction(client, valid_mri_image_bytes)

    res = client.get("/api/v1/history/export/csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "attachment; filename=" in res.headers["content-disposition"]

    # Parse CSV content
    reader = csv.reader(io.StringIO(res.text))
    rows = list(reader)
    assert len(rows) >= 2  # Header + at least 1 record
    header = rows[0]
    assert "Predicted Class" in header
    assert "Confidence" in header
    assert "Inference Time (ms)" in header


def test_csv_injection_protection():
    """Verify security utility prevents formula injection with leading characters."""
    from app.core.security import sanitize_for_csv

    assert sanitize_for_csv("=1+1") == "'=1+1"
    assert sanitize_for_csv("+SUM(A1:A10)") == "'+SUM(A1:A10)"
    assert sanitize_for_csv("-cmd|'/C calc'!A0") == "'-cmd|'/C calc'!A0"
    assert sanitize_for_csv("@cmd") == "'@cmd"
    assert sanitize_for_csv("glioma") == "glioma"
