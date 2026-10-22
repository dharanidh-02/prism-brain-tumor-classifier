"""Prediction and multi-model comparison endpoints."""

from typing import List, Union
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.prediction_service import predict_single_image, compare_models_for_image
from app.schemas.prediction_schemas import PredictionResponse, ComparisonResponse
from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/predictions", tags=["Predictions"])


@router.post(
    "",
    response_model=PredictionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Predict Brain Tumor from MRI Image",
    description=(
        "Upload a brain MRI scan image (JPEG/PNG) to classify among glioma, meningioma, "
        "notumor, and pituitary using the specified deep learning model."
    ),
)
async def predict_mri(
    file: UploadFile = File(..., description="Uploaded MRI image file (JPEG or PNG)"),
    model_id: str = Form(..., description="Model ID (e.g. 'hybrid_v1', 'hybrid_v1_final', 'hybrid_v2_finetuned')"),
    save_image: bool = Form(False, description="Whether to locally persist the uploaded image file"),
    db: Session = Depends(get_db),
):
    file_bytes = await file.read()
    filename = file.filename or "unknown.png"

    return predict_single_image(
        db=db,
        file_bytes=file_bytes,
        original_filename=filename,
        model_id=model_id,
        save_image=save_image,
    )


@router.post(
    "/compare",
    response_model=ComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare Predictions Across Multiple Models",
    description=(
        "Upload a single brain MRI image and run inference across a list of selected models. "
        "Returns individual model predictions, confidence levels, and execution durations."
    ),
)
async def compare_mri(
    file: UploadFile = File(..., description="Uploaded MRI image file (JPEG or PNG)"),
    model_ids: List[str] = Form(..., description="List of model IDs to compare (supports multiple form values or comma-separated)"),
    db: Session = Depends(get_db),
):
    file_bytes = await file.read()
    filename = file.filename or "unknown.png"

    # Flatten if client submitted comma-separated string in single form field
    parsed_model_ids: List[str] = []
    for item in model_ids:
        for mid in item.split(","):
            clean = mid.strip()
            if clean and clean not in parsed_model_ids:
                parsed_model_ids.append(clean)

    return compare_models_for_image(
        db=db,
        file_bytes=file_bytes,
        original_filename=filename,
        model_ids=parsed_model_ids,
    )
