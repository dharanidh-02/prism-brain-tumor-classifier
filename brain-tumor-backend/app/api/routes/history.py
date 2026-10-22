"""Prediction history retrieval, filtering, deletion, and CSV export endpoints."""

import csv
import io
import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repositories import PredictionRepository
from app.utils.file_storage import delete_stored_image
from app.core.security import sanitize_for_csv
from app.core.exceptions import ResourceNotFoundError
from app.schemas.history_schemas import (
    PaginatedHistoryResponse,
    PredictionHistoryItem,
)
from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/history", tags=["History"])


def _to_history_item(record) -> PredictionHistoryItem:
    try:
        class_probs = json.loads(record.class_probabilities_json)
    except Exception:
        class_probs = {}

    return PredictionHistoryItem(
        id=record.id,
        model_id=record.model_id,
        predicted_class=record.predicted_class,
        confidence=record.confidence,
        class_probabilities=class_probs,
        inference_time_ms=record.inference_time_ms,
        image_sha256=record.image_sha256,
        original_filename=record.original_filename,
        image_saved=record.image_saved,
        created_at=record.created_at,
        status=record.status,
        error_message=record.error_message,
    )


@router.get(
    "",
    response_model=PaginatedHistoryResponse,
    summary="List Prediction History",
    description="Query paginated historical predictions with optional class, model, and date range filters.",
)
def get_prediction_history(
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Item offset for pagination"),
    predicted_class: Optional[str] = Query(None, description="Filter by predicted class"),
    model_id: Optional[str] = Query(None, description="Filter by model ID"),
    start_date: Optional[datetime] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date filter (ISO format)"),
    db: Session = Depends(get_db),
):
    records, total = PredictionRepository.list_predictions(
        db=db,
        limit=limit,
        offset=offset,
        predicted_class=predicted_class,
        model_id=model_id,
        start_date=start_date,
        end_date=end_date,
    )
    items = [_to_history_item(r) for r in records]
    return PaginatedHistoryResponse(items=items, total=total, limit=limit, offset=offset)


@router.get(
    "/export/csv",
    summary="Export History as CSV",
    description="Export historical predictions into a downloadable CSV with spreadsheet formula injection protection.",
)
def export_history_csv(
    predicted_class: Optional[str] = Query(None, description="Filter by predicted class"),
    model_id: Optional[str] = Query(None, description="Filter by model ID"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    limit: int = Query(5000, ge=1, le=10000, description="Max export rows"),
    db: Session = Depends(get_db),
):
    records = PredictionRepository.get_for_export(
        db=db,
        predicted_class=predicted_class,
        model_id=model_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Header
    writer.writerow([
        "ID",
        "Model ID",
        "Predicted Class",
        "Confidence",
        "Glioma Probability",
        "Meningioma Probability",
        "No Tumor Probability",
        "Pituitary Probability",
        "Inference Time (ms)",
        "Image SHA256",
        "Original Filename",
        "Image Saved",
        "Status",
        "Created At (UTC)",
    ])

    for r in records:
        try:
            probs = json.loads(r.class_probabilities_json)
        except Exception:
            probs = {}

        writer.writerow([
            sanitize_for_csv(r.id),
            sanitize_for_csv(r.model_id),
            sanitize_for_csv(r.predicted_class),
            sanitize_for_csv(f"{r.confidence:.4f}"),
            sanitize_for_csv(f"{probs.get('glioma', 0.0):.4f}"),
            sanitize_for_csv(f"{probs.get('meningioma', 0.0):.4f}"),
            sanitize_for_csv(f"{probs.get('notumor', 0.0):.4f}"),
            sanitize_for_csv(f"{probs.get('pituitary', 0.0):.4f}"),
            sanitize_for_csv(f"{r.inference_time_ms:.2f}"),
            sanitize_for_csv(r.image_sha256),
            sanitize_for_csv(r.original_filename or "N/A"),
            sanitize_for_csv("Yes" if r.image_saved else "No"),
            sanitize_for_csv(r.status),
            sanitize_for_csv(r.created_at.isoformat() if r.created_at else ""),
        ])

    csv_content = output.getvalue()
    filename = f"prism_predictions_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )


@router.get(
    "/{prediction_id}",
    response_model=PredictionHistoryItem,
    summary="Get Single Prediction Record",
    description="Retrieve full record for a specific prediction ID.",
)
def get_single_prediction(prediction_id: int, db: Session = Depends(get_db)):
    record = PredictionRepository.get_by_id(db, prediction_id)
    if not record:
        raise ResourceNotFoundError("Prediction", prediction_id)
    return _to_history_item(record)


@router.delete(
    "/{prediction_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Prediction Record",
    description="Delete a prediction record and its associated persisted image file if one was saved.",
)
def delete_prediction(prediction_id: int, db: Session = Depends(get_db)):
    record = PredictionRepository.get_by_id(db, prediction_id)
    if not record:
        raise ResourceNotFoundError("Prediction", prediction_id)

    # Clean up file on disk if it was stored
    if record.image_saved and record.image_path:
        delete_stored_image(record.image_path)

    PredictionRepository.delete_by_id(db, prediction_id)
    return {"message": f"Prediction record {prediction_id} successfully deleted."}
