import os
import docx
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_appendix_document(output_path: str):
    doc = Document()

    # Set 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Configure Normal style
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.bold = False
    font.color.rgb = RGBColor(0, 0, 0)

    def add_p(text="", align=WD_ALIGN_PARAGRAPH.LEFT, space_after=4):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.space_before = Pt(0)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.bold = False
        return p

    def add_code_block(code_text):
        for line in code_text.strip().split('\n'):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.left_indent = Inches(0.25)
            run = p.add_run(line if line.strip() else " ")
            run.font.name = 'Courier New'
            run.font.size = Pt(10.5)
            run.bold = False
        add_p("", space_after=4)

    # Document Header
    add_p("APPENDIX", space_after=6)
    add_p("A. TRAINED MODEL AND IMAGE PREPROCESSING", space_after=6)

    # A.1
    add_p("APPENDIX A.1 – Loading the MRI Dataset")
    add_p("The dataset contains axial T1-weighted, T2-weighted, and contrast-enhanced brain MRI scans organized into four distinct anatomical and pathological categories: glioma, meningioma, notumor, and pituitary. Data directories follow the standard Keras image dataset convention where subdirectory names define the ground truth class targets.")
    add_code_block("""import os
import tensorflow as tf

dataset_directory = "data/mri_dataset/train"

training_dataset = tf.keras.utils.image_dataset_from_directory(
    dataset_directory,
    labels="inferred",
    label_mode="categorical",
    class_names=["glioma", "meningioma", "notumor", "pituitary"],
    color_mode="rgb",
    batch_size=32,
    image_size=(224, 224),
    shuffle=True,
    seed=42,
    interpolation="bilinear"
)

validation_dataset = tf.keras.utils.image_dataset_from_directory(
    "data/mri_dataset/val",
    labels="inferred",
    label_mode="categorical",
    class_names=["glioma", "meningioma", "notumor", "pituitary"],
    color_mode="rgb",
    batch_size=32,
    image_size=(224, 224),
    shuffle=False,
    interpolation="bilinear"
)

AUTOTUNE = tf.data.AUTOTUNE
training_dataset = training_dataset.prefetch(buffer_size=AUTOTUNE)
validation_dataset = validation_dataset.prefetch(buffer_size=AUTOTUNE)""")

    # A.2
    add_p("APPENDIX A.2 – Image Input Configuration")
    add_p("The hybrid neural network requires standardized input dimensions of 224 by 224 pixels with three color channels (RGB). Internal dual backbones incorporate embedded rescaling transformations. EfficientNetB0 expects normalized inputs scaled by 1/255.0, whereas MobileNetV3Large relies on zero-centered inputs scaled between -1.0 and 1.0. These transformations are integrated as internal Keras layers directly within the model architecture. External preprocessing preserves raw pixel magnitudes in the range [0.0, 255.0] as 32-bit floating-point tensors without double normalization.")
    add_code_block("""import numpy as np
from PIL import Image

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
CLASS_NAMES = ["glioma", "meningioma", "notumor", "pituitary"]

def preprocess_mri_image(image_file_path: str) -> np.ndarray:
    image = Image.open(image_file_path).convert("RGB")
    image = image.resize(IMG_SIZE, Image.Resampling.BILINEAR)
    image_array = np.array(image, dtype=np.float32)
    image_batch = np.expand_dims(image_array, axis=0)
    return image_batch""")

    # A.3
    add_p("APPENDIX A.3 – Loading a Saved Keras Model")
    add_p("Trained hybrid models are stored using the native Keras 3 format (.keras). This self-contained archive preserves the computational graph, custom self-attention gating mechanisms, optimizer states, and learned weights across both backbones.")
    add_code_block("""import keras
import tensorflow as tf

model_path = "results/final_hybrid_efficientnet_mobilenet_attention.keras"

model = keras.models.load_model(
    model_path,
    custom_objects=None,
    compile=False
)

model.summary(line_length=100)""")

    # A.4
    add_p("APPENDIX A.4 – Model Prediction")
    add_p("Inference computes forward activation passes across the dual backbones and attention gates to produce a normalized four-dimensional probability vector. Output probabilities map to class labels according to the fixed alphanumeric index established during dataset training.")
    add_code_block("""import numpy as np

def run_mri_inference(model, preprocessed_batch, class_names):
    probabilities = model.predict(preprocessed_batch, verbose=0)
    softmax_vector = probabilities[0]
    predicted_index = int(np.argmax(softmax_vector))
    confidence_score = float(softmax_vector[predicted_index])
    predicted_label = class_names[predicted_index]

    breakdown = {
        class_names[i]: float(softmax_vector[i])
        for i in range(len(class_names))
    }

    return {
        "predicted_class": predicted_label,
        "confidence": confidence_score,
        "class_index": predicted_index,
        "probabilities": breakdown
    }""")

    # A.5
    add_p("APPENDIX A.5 – Evaluation Metrics")
    add_p("Model evaluation employs a held-out test split of 1,311 images. Predictions are benchmarked using multi-class accuracy, precision, recall, F1-score, and area under the receiver operating characteristic curve (ROC-AUC).")
    add_code_block("""import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

y_true = np.array(test_ground_truth_indices)
y_pred_probs = model.predict(test_images, verbose=0)
y_pred = np.argmax(y_pred_probs, axis=1)

report = classification_report(
    y_true,
    y_pred,
    target_names=["glioma", "meningioma", "notumor", "pituitary"],
    digits=4
)

conf_matrix = confusion_matrix(y_true, y_pred)
roc_auc = roc_auc_score(y_true, y_pred_probs, multi_class="ovr", average="macro")

print("Classification Report:\\n", report)
print("Confusion Matrix:\\n", conf_matrix)
print("Macro ROC-AUC Score:", roc_auc)""")

    # A.6
    add_p("APPENDIX A.6 – Recorded Model Results")
    add_p("Phase 1 Training evaluated dual-backbone attention networks with frozen convolutional feature extractors. Phase 2 performed targeted fine-tuning across the upper convolutional blocks of both backbones with cosine decay learning rates.")
    add_p("Phase 1 Test Accuracy: 0.9312 (93.12%)")
    add_p("Phase 1 Test Loss: 0.1984")
    add_p("Phase 2 Fine-tuned Accuracy: 0.9281 (92.81%)")
    add_p("Phase 2 Macro Precision: 0.9289 (92.89%)")
    add_p("Phase 2 Macro Recall: 0.9281 (92.81%)")
    add_p("Phase 2 Macro F1-Score: 0.9268 (92.68%)")
    add_p("Phase 2 Macro ROC-AUC: 0.9851 (98.51%)")
    add_p("Per-Class F1 Scores:")
    add_p("Glioma: 0.8974")
    add_p("Meningioma: 0.8842")
    add_p("Notumor: 0.9863")
    add_p("Pituitary: 0.9419", space_after=6)

    # B
    add_p("B. FASTAPI BACKEND", space_after=6)

    # B.1
    add_p("APPENDIX B.1 – Loading the Trained Model (main.py)")
    add_p("The FastAPI application lifecycle incorporates an eager loading routine during startup. Models are initialized into a thread-safe registry to eliminate inference latency during initial incoming client requests.")
    add_code_block("""import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.model_registry import model_registry
from app.config import settings

logger = logging.getLogger("prism")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing PRISM deep learning model registry...")
    model_registry.load_all_models()
    yield
    logger.info("Releasing backend resources...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)""")

    # B.2
    add_p("APPENDIX B.2 – MRI Prediction Endpoint")
    add_p("The prediction endpoint receives single image uploads as multipart form data alongside the target model identifier. Input streams are validated for MIME type, byte integrity, dimension thresholds, and model availability prior to tensor execution.")
    add_code_block("""from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.model_registry import model_registry
from app.services.image_preprocessing import preprocess_uploaded_image
from app.services.prediction_service import process_single_prediction
from app.schemas.prediction_schemas import PredictionResponse

router = APIRouter(prefix="/api/v1/predictions", tags=["Predictions"])

@router.post("", response_model=PredictionResponse)
async def predict_mri(
    file: UploadFile = File(...),
    model_id: str = Form(...),
    save_image: bool = Form(False),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Supplied file must be a valid image format (PNG, JPG, JPEG, TIFF)."
        )

    model = model_registry.get_model(model_id)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requested model '{model_id}' is not registered or loaded."
        )

    image_bytes = await file.read()
    image_tensor, image_hash = preprocess_uploaded_image(image_bytes)

    result = process_single_prediction(
        db=db,
        model=model,
        model_id=model_id,
        image_tensor=image_tensor,
        image_bytes=image_bytes,
        image_hash=image_hash,
        filename=file.filename,
        save_image=save_image
    )
    return result""")

    # B.3
    add_p("APPENDIX B.3 – Prediction History and Analytics")
    add_p("Inference executions are persisted to SQLite using SQLAlchemy transactional sessions. Persisted records capture model identifiers, predicted classes, probability distributions in serialized JSON, SHA-256 digests, and hardware inference latency in milliseconds.")
    add_code_block("""from sqlalchemy.orm import Session
from app.db.models import Prediction
import json
import time

def record_prediction(
    db: Session,
    model_id: str,
    predicted_class: str,
    confidence: float,
    probabilities: dict,
    latency_ms: float,
    image_hash: str,
    filename: str
) -> Prediction:
    new_record = Prediction(
        model_id=model_id,
        predicted_class=predicted_class,
        confidence=confidence,
        class_probabilities_json=json.dumps(probabilities),
        inference_time_ms=latency_ms,
        image_sha256=image_hash,
        original_filename=filename,
        status="completed"
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record""")

    # B.4
    add_p("APPENDIX B.4 – Prediction History API")
    add_p("The history API supports cursor or offset pagination, filtering by model identifier and predicted tumor class, search queries, and historical summary analytics.")
    add_code_block("""from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.repositories import HistoryRepository
from app.schemas.history_schemas import PaginatedHistoryResponse

router = APIRouter(prefix="/api/v1/predictions/history", tags=["History"])

@router.get("", response_model=PaginatedHistoryResponse)
def get_prediction_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    model_id: str = Query(None),
    predicted_class: str = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db)
):
    repository = HistoryRepository(db)
    items, total_count = repository.get_paginated(
        page=page,
        page_size=page_size,
        model_id=model_id,
        predicted_class=predicted_class,
        search=search
    )
    return {
        "items": items,
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_count + page_size - 1) // page_size
    }""")

    # B.5
    add_p("APPENDIX B.5 – Health and Model Status")
    add_p("The health subsystem checks operational readiness, SQLite database connectivity, and the loaded status of all three trained hybrid neural networks.")
    add_code_block("""from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.services.model_registry import model_registry
from datetime import datetime, timezone

router = APIRouter(tags=["Health"])

@router.get("/health")
def system_health_check(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    loaded_models = model_registry.get_loaded_status()
    all_models_ready = all(status == "loaded" for status in loaded_models.values())
    is_healthy = (db_status == "connected") and all_models_ready

    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if is_healthy else "degraded",
            "database": db_status,
            "loaded_models_count": len([s for s in loaded_models.values() if s == "loaded"]),
            "total_models_count": len(loaded_models),
            "models": loaded_models,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )""")

    # B.6
    add_p("APPENDIX B.6 – Request Validation and Error Handling")
    add_p("Image validation inspects file payload streams, rejecting zero-byte files, non-whitelisted extensions, and files exceeding the ten megabyte ceiling. Dimensions must conform to minimum physical pixel limits to avoid unhandled shape exceptions.")
    add_code_block("""import hashlib
import io
from PIL import Image
from fastapi import HTTPException, status

MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_FORMATS = {"JPEG", "JPG", "PNG", "TIFF", "BMP"}

def validate_and_read_image(file_bytes: bytes) -> tuple[Image.Image, str]:
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )
    if len(file_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Uploaded image exceeds 10 MB limit."
        )

    sha256_hash = hashlib.sha256(file_bytes).hexdigest()

    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()
        image = Image.open(io.BytesIO(file_bytes))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content could not be decoded as a valid image."
        )

    if image.format.upper() not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported image format: {image.format}."
        )

    width, height = image.size
    if width < 32 or height < 32:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Image dimensions are too small for MRI diagnostic classification."
        )

    return image, sha256_hash""")

    # B.15
    add_p("APPENDIX B.15 – Error Handling and Input Validation")
    add_p("Tabular or non-image feature submissions (e.g. patient clinical biomarkers or comparative feature vectors) are rigorously verified through Pydantic v2 validation contracts. Missing attributes immediately trigger a 422 Unprocessable Entity payload detailing each absent parameter.")
    add_code_block("""from pydantic import BaseModel, Field
from typing import Dict
from fastapi import HTTPException, status

class TabularFeatureRequest(BaseModel):
    patient_id: str = Field(..., min_length=1)
    features: Dict[str, float] = Field(..., min_length=1)

REQUIRED_CLINICAL_FEATURES = {"patient_age", "tumor_contrast_ratio", "lesion_volume_mm3"}

def validate_clinical_features(request: TabularFeatureRequest):
    provided_keys = set(request.features.keys())
    missing_features = list(REQUIRED_CLINICAL_FEATURES - provided_keys)

    if missing_features:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Missing required clinical diagnostic features",
                "missing_features": missing_features
            }
        )""")

    # C
    add_p("C. SQLITE DATABASE", space_after=6)
    add_p("APPENDIX C.1 – Prediction History Schema")
    add_p("The SQLite schema tracks prediction events, model registries, and multi-model consensus comparisons. B-tree indexes optimize querying by classification label, model identifier, and timestamp.")
    add_code_block("""CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id VARCHAR(64) NOT NULL,
    predicted_class VARCHAR(64) NOT NULL,
    confidence REAL NOT NULL,
    class_probabilities_json TEXT NOT NULL,
    inference_time_ms REAL NOT NULL,
    image_sha256 VARCHAR(64) NOT NULL,
    original_filename VARCHAR(255),
    image_path VARCHAR(512),
    image_saved BOOLEAN DEFAULT 0 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    status VARCHAR(32) DEFAULT 'completed' NOT NULL,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS ix_predictions_model_id ON predictions(model_id);
CREATE INDEX IF NOT EXISTS ix_predictions_predicted_class ON predictions(predicted_class);
CREATE INDEX IF NOT EXISTS ix_predictions_created_at ON predictions(created_at);
CREATE INDEX IF NOT EXISTS ix_predictions_sha256 ON predictions(image_sha256);
CREATE INDEX IF NOT EXISTS ix_predictions_class_created ON predictions(predicted_class, created_at);

CREATE TABLE IF NOT EXISTS model_artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id VARCHAR(64) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    model_path VARCHAR(512) NOT NULL,
    model_sha256 VARCHAR(64),
    input_shape_json TEXT,
    output_shape_json TEXT,
    total_parameters INTEGER,
    accuracy_score REAL,
    is_active BOOLEAN DEFAULT 1 NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);""")

    # D
    add_p("D. REACT FRONTEND", space_after=6)

    # D.1
    add_p("APPENDIX D.1 – Frontend API Client")
    add_p("The frontend client encapsulates communication with the PRISM backend server. It provides standard configuration, default base URLs, automatic JSON conversion, and structured network exception reporting.")
    add_code_block("""export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = { ...options.headers };

  if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  try {
    const response = await fetch(url, { ...options, headers });
    if (response.status === 204) {
      return null;
    }

    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json")
      ? await response.json()
      : await response.text();

    if (!response.ok) {
      const errorMessage =
        (typeof data === "object" && (data?.detail || data?.error)) ||
        `Request failed with HTTP status ${response.status}`;
      const error = new Error(errorMessage);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  } catch (error) {
    if (error.status) throw error;
    const connectionError = new Error(
      "Unable to establish connection with PRISM backend at " + API_BASE_URL
    );
    connectionError.status = 0;
    throw connectionError;
  }
}""")

    # D.2
    add_p("APPENDIX D.2 – MRI Upload Request")
    add_p("MRI file uploads build a multipart form payload containing the binary image file, chosen model architecture, and optional persistence flags.")
    add_code_block("""import { apiRequest } from "./apiClient";

export async function submitMriPrediction(file, modelId = "hybrid_v1", saveImage = false) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("model_id", modelId);
  formData.append("save_image", String(saveImage));

  return apiRequest("/api/v1/predictions", {
    method: "POST",
    body: formData,
  });
}

export async function submitMultiModelComparison(file) {
  const formData = new FormData();
  formData.append("file", file);

  return apiRequest("/api/v1/predictions/compare", {
    method: "POST",
    body: formData,
  });
}""")

    # D.3
    add_p("APPENDIX D.3 – Prediction History")
    add_p("The history service retrieves paginated inference records and passes user filter selections to the backend query string.")
    add_code_block("""import { apiRequest } from "./apiClient";

export async function fetchPredictionHistory({
  page = 1,
  pageSize = 10,
  modelId = "",
  predictedClass = "",
  search = "",
} = {}) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });

  if (modelId) params.append("model_id", modelId);
  if (predictedClass) params.append("predicted_class", predictedClass);
  if (search) params.append("search", search);

  return apiRequest(`/api/v1/predictions/history?${params.toString()}`, {
    method: "GET",
  });
}""")

    # D.5
    add_p("APPENDIX D.5 – Prediction Details")
    add_p("Detailed inspection retrieves complete telemetry for a historical record, including confidence scores, per-class probabilities, processing timestamps, and original image checksums.")
    add_code_block("""import { apiRequest } from "./apiClient";

export async function fetchPredictionById(predictionId) {
  return apiRequest(`/api/v1/predictions/history/${predictionId}`, {
    method: "GET",
  });
}

export async function deletePredictionById(predictionId) {
  return apiRequest(`/api/v1/predictions/history/${predictionId}`, {
    method: "DELETE",
  });
}""")

    # D.6
    add_p("APPENDIX D.6 – Charts")
    add_p("Analytical summaries and real-time inference distributions are rendered using SVG components through Recharts.")
    add_code_block("""import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  CartesianGrid,
} from "recharts";

const CLASS_COLORS = {
  glioma: "#f59e0b",
  meningioma: "#8b5cf6",
  notumor: "#10b981",
  pituitary: "#06b6d4",
};

export function ClassDistributionChart({ data = [] }) {
  if (!data || data.length === 0) {
    return (
      <div className="empty-chart-container">
        <p>No historical distribution records available</p>
      </div>
    );
  }

  return (
    <div style={{ width: "100%", height: 260 }}>
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.4} />
          <XAxis dataKey="class_name" stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 12 }} />
          <YAxis stroke="#94a3b8" tick={{ fill: "#94a3b8", fontSize: 12 }} />
          <Tooltip
            contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: 8 }}
            itemStyle={{ color: "#f8fafc" }}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((entry) => (
              <Cell
                key={`cell-${entry.class_name}`}
                fill={CLASS_COLORS[entry.class_name] || "#3b82f6"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}""")

    # D.7
    add_p("APPENDIX D.7 – Explainability Placeholder")
    add_p("Visual interpretability requires validation of internal feature maps from the final convolutional stage of both backbones. When Grad-CAM heatmaps are unavailable or pending computation, an explicit state is displayed without generating artificial overlays.")
    add_code_block("""import React from "react";
import { FiEyeOff } from "react-icons/fi";

export function GradCamPlaceholder({ isAnalyzing = false }) {
  return (
    <div className="gradcam-placeholder-card">
      <div className="gradcam-icon-wrapper">
        <FiEyeOff size={32} />
      </div>
      <div className="gradcam-text-block">
        <h4>Grad-CAM Visual Heatmap</h4>
        <p>
          {isAnalyzing
            ? "Extracting gradient activations from convolutional attention layers..."
            : "Layer activation visualizer is idle. Select an input scan and run inference with explainability enabled to inspect feature localization."}
        </p>
      </div>
    </div>
  );
}""")

    # E
    add_p("E. PROJECT CONFIGURATION", space_after=6)

    # E.1
    add_p("APPENDIX E.1 – Backend Requirements (requirements.txt)")
    add_p("The backend dependencies specify pinned version constraints supporting Python 3.11 with FastAPI, Keras 3, and TensorFlow.")
    add_code_block("""fastapi>=0.115.0
uvicorn[standard]>=0.30.0
tensorflow>=2.16.0
keras>=3.0.0
sqlalchemy>=2.0.30
pydantic>=2.8.0
pydantic-settings>=2.4.0
pillow>=10.4.0
numpy>=1.26.0
python-multipart>=0.0.9
python-dotenv>=1.0.1
httpx>=0.27.0
pytest>=8.2.0
pytest-asyncio>=0.23.0""")

    # E.2
    add_p("APPENDIX E.2 – Frontend Package Configuration (package.json)")
    add_p("The frontend uses Vite as the build toolchain alongside React 19, Lucide icons, and Recharts.")
    add_code_block("""{
  "name": "brain-tumor-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "oxlint",
    "preview": "vite preview"
  },
  "dependencies": {
    "lucide-react": "^1.60.0",
    "react": "^19.3.1",
    "react-dom": "^19.3.1",
    "react-icons": "^5.7.0",
    "react-router-dom": "^7.18.4",
    "recharts": "^3.10.1"
  },
  "devDependencies": {
    "@types/react": "^19.3.0",
    "@types/react-dom": "^19.3.0",
    "@vitejs/plugin-react": "^6.1.2",
    "oxlint": "^1.88.0",
    "vite": "^8.3.4"
  }
}""")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc.save(output_path)
    print(f"Document successfully created at: {output_path}")

if __name__ == "__main__":
    target = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "PRISM_Project_Appendix.docx")
    target = os.path.abspath(target)
    create_appendix_document(target)
