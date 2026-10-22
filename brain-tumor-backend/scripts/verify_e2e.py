"""End-to-end full verification script for NeuroVision AI backend."""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

from app.main import app

def run_verification():
    print("=" * 70)
    print("PRISM: Precision Radiology Imaging for Solid Masses")
    print("A Hybrid EfficientNet-MobileNet Attention Classifier for Brain Tumors")
    print("Full End-to-End API and Model Verification")
    print("=" * 70)

    client = TestClient(app)

    print("\n[Step 1] System Health Check (/health)...")
    h = client.get("/health")
    print(f"Status Code: {h.status_code}")
    print(f"Response: {h.json()}")
    assert h.status_code == 200
    assert h.json()["status"] in ("healthy", "degraded")

    print("\n[Step 2] Model Registry Listing (/api/v1/models)...")
    m = client.get("/api/v1/models")
    print(f"Status Code: {m.status_code}")
    models_info = m.json()
    for item in models_info:
        print(f"  - Model: {item['model_id']:<20} | Status: {item['status']:<10} | Params: {item['parameter_count']:,}")
    assert m.status_code == 200
    assert len(models_info) == 3

    print("\n[Step 3] Real Image Prediction across all 3 models...")
    crop_path = backend_root.parent / "results" / "__results___files" / "test_crop.jpg"
    with open(crop_path, "rb") as f:
        mri_bytes = f.read()

    for mid in ["hybrid_v1", "hybrid_v1_final", "hybrid_v2_finetuned"]:
        res = client.post(
            "/api/v1/predictions",
            data={"model_id": mid, "save_image": "true"},
            files={"file": ("brain_scan.jpg", mri_bytes, "image/jpeg")},
        )
        print(f"\nModel '{mid}':")
        assert res.status_code == 201
        data = res.json()
        print(f"  Prediction ID: {data['prediction_id']}")
        print(f"  Predicted Class: {data['predicted_class']}")
        print(f"  Confidence: {data['confidence']:.4f}")
        print(f"  Class Probabilities: {data['class_probabilities']}")
        print(f"  Inference Latency: {data['inference_time_ms']:.2f} ms")

    print("\n[Step 4] Multi-Model Comparison Endpoint (/api/v1/predictions/compare)...")
    comp = client.post(
        "/api/v1/predictions/compare",
        data={"model_ids": "hybrid_v1,hybrid_v1_final,hybrid_v2_finetuned"},
        files={"file": ("brain_scan.jpg", mri_bytes, "image/jpeg")},
    )
    assert comp.status_code == 200
    comp_data = comp.json()
    print(f"Comparison ID: {comp_data['comparison_id']}")
    for r in comp_data["results"]:
        print(f"  - {r['model_id']}: {r['predicted_class']} (conf={r['confidence']}, {r['inference_time_ms']}ms)")

    print("\n[Step 5] History Listing & Pagination (/api/v1/history)...")
    hist = client.get("/api/v1/history?limit=10&offset=0")
    assert hist.status_code == 200
    hist_data = hist.json()
    print(f"Total History Records: {hist_data['total']}")
    print(f"Returned Items: {len(hist_data['items'])}")

    print("\n[Step 6] CSV Export (/api/v1/history/export/csv)...")
    csv_res = client.get("/api/v1/history/export/csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    lines = csv_res.text.strip().split("\n")
    print(f"Exported CSV Rows (including header): {len(lines)}")

    print("\n[Step 7] Analytics Overview (/api/v1/analytics/overview)...")
    ana = client.get("/api/v1/analytics/overview")
    assert ana.status_code == 200
    print(f"Analytics Data: {ana.json()}")

    print("\n[Step 8] Model Benchmarks (/api/v1/analytics/model-performance)...")
    perf = client.get("/api/v1/analytics/model-performance")
    assert perf.status_code == 200
    print(f"Benchmarks count: {len(perf.json()['models'])}")

    print("\n" + "=" * 70)
    print("[SUCCESS] ALL END-TO-END VERIFICATION CHECKS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    run_verification()
