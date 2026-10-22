"""Automated tests for analytics and model performance benchmarks."""

from fastapi.testclient import TestClient


def _create_prediction(client: TestClient, image_bytes: bytes, model_id="hybrid_v1"):
    res = client.post(
        "/api/v1/predictions",
        data={"model_id": model_id, "save_image": "false"},
        files={"file": ("test.jpg", image_bytes, "image/jpeg")},
    )
    assert res.status_code == 201
    return res.json()


def test_analytics_overview_calculation(client: TestClient, valid_mri_image_bytes: bytes):
    """Test analytics overview calculations aggregate predictions properly."""
    _create_prediction(client, valid_mri_image_bytes, "hybrid_v1")
    _create_prediction(client, valid_mri_image_bytes, "hybrid_v1_final")

    res = client.get("/api/v1/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["total_predictions"] >= 2
    assert "predictions_by_class" in data
    assert "predictions_by_model" in data
    assert "hybrid_v1" in data["predictions_by_model"]
    assert data["average_inference_time_ms"] > 0
    assert data["operational_models_count"] >= 1


def test_model_performance_benchmarks(client: TestClient):
    """Test that model performance exposes benchmark metrics with provenance and disclaimer."""
    res = client.get("/api/v1/analytics/model-performance")
    assert res.status_code == 200
    data = res.json()
    assert "disclaimer" in data
    assert "models" in data
    assert len(data["models"]) == 3

    model_ids = {m["model_id"]: m for m in data["models"]}

    # Verify Phase 1 metrics on hybrid_v1
    m1 = model_ids["hybrid_v1"]
    assert m1["metrics"]["test_accuracy"] == 0.9312
    assert m1["metrics"]["test_loss"] == 0.3425
    assert m1["metrics"]["provenance"] == "Project Phase 1 Test Evaluation"

    # Verify Phase 2 metrics on hybrid_v2_finetuned
    m3 = model_ids["hybrid_v2_finetuned"]
    assert m3["metrics"]["test_accuracy"] == 0.9281
    assert m3["metrics"]["macro_roc_auc"] == 0.9851
    assert m3["metrics"]["macro_f1_score"] == 0.9268
    assert m3["metrics"]["provenance"] == "Project Phase 2 Test Evaluation"
