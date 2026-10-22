# PRISM — Precision Radiology Imaging for Solid Masses
### A Hybrid EfficientNet-MobileNet Attention Classifier for Brain Tumors

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF.svg)](https://vitejs.dev/)
[![TensorFlow / Keras](https://img.shields.io/badge/Keras-3.0%2B-D00000.svg)](https://keras.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**PRISM** (Precision Radiology Imaging for Solid Masses) is a full-stack, clinical-grade deep learning solution for automated Brain Tumor MRI classification. The system combines dual-backbone convolutional neural networks (**EfficientNetB0** + **MobileNetV3Large**) integrated with feature projection, concatenation, and self-attention gating mechanisms.

---

## 🔬 Key Capabilities

- **Dual-Stream Hybrid Architecture**: Combines EfficientNetB0 for high-resolution representation and MobileNetV3Large for lightweight multi-scale context, unified via self-attention gating.
- **Multi-Class Detection**: Accurately classifies brain MRIs into 4 clinical categories:
  - `glioma`
  - `meningioma`
  - `notumor`
  - `pituitary`
- **Side-by-Side Model Benchmarking**: Perform simultaneous inference across three distinct model checkpoints to evaluate confidence distributions, agreement rates, and latency.
- **Audit & History Log**: SQLite-backed prediction history with patient metadata, filtering, full provenance auditing, and CSV export.
- **Modern Medical Dashboard**: Responsive React + Vite frontend with Tailwind/CSS styling, interactive confidence gauges, radar charts, and dark-mode healthcare UI.

---

## 🏗️ Repository Architecture

```
prism-brain-tumor-classifier/
├── brain-tumor-backend/            # FastAPI REST API & ML Inference Engine
│   ├── app/
│   │   ├── api/routes/             # Endpoints (predictions, models, history, analytics)
│   │   ├── core/                   # Security, exception handling, custom errors
│   │   ├── db/                     # SQLAlchemy models, sessions & repositories
│   │   ├── schemas/                # Pydantic v2 schemas
│   │   ├── services/               # Model registry, image preprocessing, inference
│   │   └── utils/                  # Validation & safe file handling
│   ├── tests/                      # Pytest suite with test doubles & integration tests
│   ├── requirements.txt            # Python dependencies
│   └── README.md                   # Detailed backend documentation
│
├── brain-tumor-frontend/           # React 18 + Vite SPA Frontend
│   ├── src/
│   │   ├── components/             # Reusable UI components, layout & charts
│   │   ├── pages/                  # Views (Dashboard, Predict, Models, History, Analytics)
│   │   └── services/               # API clients & state management
│   ├── package.json                # Frontend dependencies
│   └── vite.config.js              # Vite configuration
│
├── results/                        # Trained Keras 3 Model Artifacts & Evaluations
│   ├── final_hybrid_efficientnet_mobilenet_attention.keras
│   ├── FINAL_Hybrid_EfficientNetB0_MobileNetV3_Attention.keras
│   ├── checkpoints/best_hybrid_model.keras
│   └── phase2_checkpoints/best_hybrid_finetuned.keras
│
└── PRISM_Project_Appendix.docx     # Comprehensive project technical appendix
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python**: 3.10 or higher
- **Node.js**: 18+ and `npm`

---

### 2. Backend Setup

```bash
# Navigate to the backend directory
cd brain-tumor-backend

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy example environment configuration
copy .env.example .env     # Windows
# cp .env.example .env     # Linux/macOS

# Initialize database schema
python scripts/initialize_db.py

# Start the FastAPI server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend API will be available at: `http://127.0.0.1:8000`  
Interactive Swagger docs: `http://127.0.0.1:8000/docs`

---

### 3. Frontend Setup

```bash
# Navigate to the frontend directory
cd brain-tumor-frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend application will be accessible at `http://localhost:5173`.

---

## 🧪 Testing

Execute the comprehensive backend test suite:

```bash
cd brain-tumor-backend
pytest
```

---

## 📊 Models & Checkpoints

| Model ID | Architecture | Checkpoint | Focus |
|---|---|---|---|
| `hybrid_v1` | EfficientNetB0 + MobileNetV3 | `results/final_hybrid_efficientnet_mobilenet_attention.keras` | Base hybrid with attention gating |
| `hybrid_v1_final` | EfficientNetB0 + MobileNetV3 | `results/FINAL_Hybrid_EfficientNetB0_MobileNetV3_Attention.keras` | Final evaluated hybrid weights |
| `hybrid_v2_finetuned` | EfficientNetB0 + MobileNetV3 | `results/phase2_checkpoints/best_hybrid_finetuned.keras` | Two-phase fine-tuned checkpoint |

---

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
