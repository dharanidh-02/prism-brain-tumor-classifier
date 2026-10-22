# PRISM — Precision Radiology Imaging for Solid Masses
### A Hybrid EfficientNet-MobileNet Attention Classifier for Brain Tumors

A production-grade, locally executable deep learning platform for Brain Tumor MRI classification. Integrates three trained hybrid deep learning models combining **EfficientNetB0** and **MobileNetV3Large** backbones with feature projection, concatenation, and self-attention gating.

---

## 1. Project Architecture Overview

**PRISM** (Precision Radiology Imaging for Solid Masses) delivers automated inference, multi-model comparison, prediction auditing, and benchmark tracking across four distinct brain MRI categories:
1. `glioma`
2. `meningioma`
3. `notumor`
4. `pituitary`

```
brain-tumor-backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── health.py           # Health checks with model and DB monitoring
│   │       ├── models.py           # Model registry and metadata endpoints
│   │       ├── predictions.py      # MRI prediction and multi-model comparison
│   │       ├── history.py          # Paginated history, search, delete, and CSV export
│   │       └── analytics.py        # Usage analytics and benchmark tracking
│   ├── core/
│   │   ├── exceptions.py       # Custom domain exceptions and JSON error handlers
│   │   └── security.py         # Path traversal defense and CSV formula injection protection
│   ├── db/
│   │   ├── database.py         # SQLAlchemy engine with SQLite foreign key enforcement
│   │   ├── models.py           # ORM schemas (Prediction, ModelArtifact, Comparison)
│   │   └── repositories.py     # Clean CRUD operations with transaction rollback
│   ├── schemas/                # Pydantic v2 schemas for all requests/responses
│   ├── services/
│   │   ├── model_registry.py   # Thread-safe central model loader and execution
│   │   ├── image_preprocessing.py # Resizing (224x224), RGB decoding, float32 validation
│   │   ├── prediction_service.py  # Inference execution, softmax verification, persistence
│   │   └── analytics_service.py   # Usage aggregation and evaluation provenance
│   ├── utils/
│   │   ├── image_validation.py # Integrity check, format whitelist, dimension bounds
│   │   └── file_storage.py     # Safe image persistence outside static roots
│   ├── config.py               # Pydantic BaseSettings with environment variable loading
│   ├── logging_config.py       # Rotating file logger and structured stdout logging
│   └── main.py                 # FastAPI application assembly and lifecycle events
├── data/                       # Local SQLite database (PRISM.db) and uploads
├── logs/                       # Application logs (app.log)
├── scripts/
│   ├── check_models.py         # Standalone model inspector and latency tester
│   └── initialize_db.py        # Database schema creation and artifact synchronization
├── tests/                      # Comprehensive automated test suite
├── .env.example                # Example environment configuration
├── requirements.txt            # Pinned dependency manifest
└── pytest.ini                  # Pytest configuration
```

---

## 2. Integrated Trained Models

The backend integrates three genuine trained Keras 3 model artifacts:

| Model ID | Display Name | Architecture | File Size | Benchmark Accuracy |
| :--- | :--- | :--- | :--- | :--- |
| `hybrid_v1` | Hybrid EfficientNetB0 + MobileNetV3 (Attention) | Dual-backbone + Self-Attention Gating | 37.56 MB | 93.12% (Phase 1 Test) |
| `hybrid_v1_final` | Hybrid EfficientNetB0 + MobileNetV3 (Final Attention) | Dual-backbone + Cross-Attention | 37.56 MB | 93.12% (Phase 1 Test) |
| `hybrid_v2_finetuned`| Hybrid Fine-tuned (Phase 2 Checkpoint) | Dual-backbone (Unfrozen backbones) | 61.00 MB | 92.81% (Phase 2 Test) |

> **Critical Preprocessing Note**: The deep learning models embed native Keras `Rescaling` layers internally (`scale=1/255.0` for EfficientNet and `scale=1/127.5, offset=-1.0` for MobileNet). Raw pixel values in `[0.0, 255.0]` (float32) must be preserved during image preprocessing.

---

## 3. Windows Setup and Execution Guide

Follow these commands in **PowerShell**:

### Step 1: Verify Python 3.11
```powershell
py --version
# Expected: Python 3.11.x
```

### Step 2: Navigate to Backend Directory
```powershell
cd "c:\Users\Dharanidharan\OneDrive - sece.ac.in\Documents\CSBS 3RD YEAR\SEMESTER 5\Artificial Intelligence and Machine Learning\Project\Brain Tumor Using MRI\brain-tumor-backend"
```

### Step 3: Create and Activate Virtual Environment
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

*(Note: If execution policy blocks script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### Step 4: Upgrade Pip and Install Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Configure Environment
Copy `.env.example` to `.env` (already created with verified Windows model paths):
```powershell
Copy-Item .env.example .env
```

### Step 6: Verify Model Files and Run Forward Pass Test
```powershell
python scripts/check_models.py
```
This utility calculates SHA-256 digests, confirms layer counts, and runs a dummy tensor forward pass.

### Step 7: Initialize SQLite Database
```powershell
python scripts/initialize_db.py
```
This script creates `data/PRISM.db` and populates the `model_artifacts` table.

### Step 8: Start the Uvicorn Server
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Step 9: Access Interactive API Documentation
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Step 10: Run the Automated Test Suite
```powershell
python -m pytest -v
```

---

## 4. API Endpoints Reference

### Health
- `GET /health`: Overall system readiness and model loading status.
- `GET /api/v1/health`: API v1 health check.

### Models
- `GET /api/v1/models`: List all registered models with architecture summaries.
- `GET /api/v1/models/{model_id}`: Detailed specifications, parameter breakdown, and shapes.
- `GET /api/v1/models/{model_id}/status`: Quick operational status check.

### Predictions
- `POST /api/v1/predictions`: Classify uploaded MRI scan (`file`, `model_id`, optional `save_image`).
- `POST /api/v1/predictions/compare`: Run scan across multiple models simultaneously.

### History
- `GET /api/v1/history`: Paginated predictions with filters (`predicted_class`, `model_id`, `start_date`, `end_date`).
- `GET /api/v1/history/{prediction_id}`: Fetch single prediction record.
- `DELETE /api/v1/history/{prediction_id}`: Remove prediction and associated stored image.
- `GET /api/v1/history/export/csv`: Export prediction logs to CSV with formula injection defense.

### Analytics
- `GET /api/v1/analytics/overview`: Aggregated volumes, class distribution, and average latency.
- `GET /api/v1/analytics/model-performance`: Verified model benchmark metrics and evaluation provenance.

---

## 5. Security & Reliability Highlights

1. **Path Traversal Protection**: Enforced strict root validation for image storage and database paths.
2. **Spreadsheet Formula Injection Defense**: All exported CSV text cells beginning with `=`, `+`, `-`, `@`, `\t`, or `\r` are escaped with a prepended single quote `'`.
3. **Pillow Verification**: Every uploaded image undergoes two-phase validation (`verify()` and decoding check) to reject malformed or maliciously crafted payloads.
4. **Thread-Safe CPU Inference**: Model inference is protected by per-model execution locks preventing concurrency conflicts during simultaneous user requests.
5. **Medical Compliance Disclaimer**: All prediction outputs include a mandatory disclaimer emphasizing that results are for experimental and research use and never constitute a medical diagnosis.

---

## 6. Troubleshooting

- **OneDrive Path with Spaces**: All paths use Windows raw strings and resolve paths via `pathlib.Path`.
- **TensorFlow oneDNN Warning**: Suppressed cleanly via environment variables (`TF_ENABLE_ONEDNN_OPTS=0`).
- **Port 8000 Already in Use**: Start on a different port using: `python -m uvicorn app.main:app --port 8080`.
- **Database Locked**: SQLite in-memory and write locks are managed using scoped transactions with immediate rollback upon error.
