"""Prediction service orchestrating image validation, inference, and persistence."""

import time
from pathlib import Path
from typing import List, Dict, Optional, Any
import numpy as np
from sqlalchemy.orm import Session

from app.config import settings
from app.logging_config import get_logger
from app.core.exceptions import PredictionError, ModelUnavailableError
from app.core.security import sanitize_filename
from app.utils.image_validation import validate_image_file
from app.utils.file_storage import save_uploaded_image
from app.services.image_preprocessing import preprocess_mri_image
from app.services.model_registry import registry
from app.db.repositories import PredictionRepository, ComparisonRepository
from app.schemas.prediction_schemas import (
    PredictionResponse,
    ComparisonResponse,
    ModelComparisonResultItem,
)

logger = get_logger(__name__)

MEDICAL_DISCLAIMER = (
    "Experimental AI classification for research and educational purposes only. "
    "This output is NOT a medical diagnosis, tumor staging, or substitute for professional clinical interpretation."
)


def _process_probabilities(raw_output: np.ndarray) -> np.ndarray:
    """Ensure output tensor represents valid probability distribution over classes."""
    if raw_output.ndim == 2:
        probs = raw_output[0]
    elif raw_output.ndim == 1:
        probs = raw_output
    else:
        raise PredictionError(f"Unexpected output tensor rank {raw_output.ndim}. Expected 2D or 1D.")

    if probs.shape[0] != len(settings.CLASS_NAMES):
        raise PredictionError(
            f"Model output dimension ({probs.shape[0]}) does not match configured classes count ({len(settings.CLASS_NAMES)})."
        )

    if not np.all(np.isfinite(probs)):
        raise PredictionError("Model output contains non-finite values (NaN or Inf).")

    # Check if output is already softmax probabilities (all >= 0 and sum ~= 1.0)
    is_valid_prob = np.all(probs >= 0.0) and np.all(probs <= 1.0) and np.isclose(np.sum(probs), 1.0, atol=1e-3)

    if not is_valid_prob:
        # Model produced logits: apply stable softmax
        logger.debug("Applying softmax conversion to raw model logits...")
        exp_logits = np.exp(probs - np.max(probs))
        probs = exp_logits / np.sum(exp_logits)

    return probs


def predict_single_image(
    db: Session,
    file_bytes: bytes,
    original_filename: str,
    model_id: str,
    save_image: bool = False,
) -> PredictionResponse:
    """Run full prediction workflow for a single image and selected model."""
    sanitized_filename = sanitize_filename(original_filename)

    # Step 1: Validate image payload
    image, image_sha256 = validate_image_file(file_bytes, sanitized_filename)

    # Step 2: Preprocess image into batch tensor (1, 224, 224, 3)
    input_tensor = preprocess_mri_image(image)

    # Step 3: Check model availability
    registered = registry.get_model(model_id)
    if registered.status != "loaded":
        raise ModelUnavailableError(
            model_id,
            registered.error_message or "Model is not operational or loaded.",
        )

    # Step 4: Execute inference with latency timing
    start_time = time.perf_counter()
    raw_output = registry.run_inference(model_id, input_tensor)
    inference_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # Step 5: Process probabilities and map to classes
    probs = _process_probabilities(raw_output)
    class_probs: Dict[str, float] = {}
    for idx, class_name in enumerate(settings.CLASS_NAMES):
        class_probs[class_name] = round(float(probs[idx]), 4)

    argmax_idx = int(np.argmax(probs))
    predicted_class = settings.CLASS_NAMES[argmax_idx]
    confidence = round(float(probs[argmax_idx]), 4)

    # Step 6: Optionally persist image to local storage
    saved_path: Optional[str] = None
    if save_image:
        ext = Path(sanitized_filename).suffix
        saved_path = save_uploaded_image(file_bytes, ext)

    # Step 7: Persist prediction metadata in SQLite
    db_record = PredictionRepository.create(
        db=db,
        model_id=model_id,
        predicted_class=predicted_class,
        confidence=confidence,
        class_probabilities=class_probs,
        inference_time_ms=inference_time_ms,
        image_sha256=image_sha256,
        original_filename=sanitized_filename,
        image_path=saved_path,
        image_saved=save_image,
        status="completed",
    )

    warnings = [MEDICAL_DISCLAIMER]

    return PredictionResponse(
        prediction_id=db_record.id,
        model_id=model_id,
        predicted_class=predicted_class,
        confidence=confidence,
        class_probabilities=class_probs,
        inference_time_ms=inference_time_ms,
        image_sha256=image_sha256,
        created_at=db_record.created_at,
        warnings=warnings,
    )


def compare_models_for_image(
    db: Session,
    file_bytes: bytes,
    original_filename: str,
    model_ids: List[str],
) -> ComparisonResponse:
    """Run inference across multiple operational models and record results."""
    sanitized_filename = sanitize_filename(original_filename)

    # Step 1: Validate image
    image, image_sha256 = validate_image_file(file_bytes, sanitized_filename)

    # Step 2: Preprocess tensor once
    input_tensor = preprocess_mri_image(image)

    results: List[ModelComparisonResultItem] = []
    db_results_data: List[Dict[str, Any]] = []

    for mid in model_ids:
        try:
            registered = registry.get_model(mid)
            if registered.status != "loaded":
                results.append(
                    ModelComparisonResultItem(
                        model_id=mid,
                        display_name=registered.display_name,
                        status=registered.status,
                        error_message=registered.error_message or "Model is not operational.",
                    )
                )
                db_results_data.append(
                    {
                        "model_id": mid,
                        "status": registered.status,
                        "error_message": registered.error_message or "Model is not operational.",
                    }
                )
                continue

            # Run inference
            start_time = time.perf_counter()
            raw_output = registry.run_inference(mid, input_tensor)
            inference_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

            probs = _process_probabilities(raw_output)
            class_probs: Dict[str, float] = {}
            for idx, cname in enumerate(settings.CLASS_NAMES):
                class_probs[cname] = round(float(probs[idx]), 4)

            argmax_idx = int(np.argmax(probs))
            predicted_class = settings.CLASS_NAMES[argmax_idx]
            confidence = round(float(probs[argmax_idx]), 4)

            item = ModelComparisonResultItem(
                model_id=mid,
                display_name=registered.display_name,
                status="completed",
                predicted_class=predicted_class,
                confidence=confidence,
                class_probabilities=class_probs,
                inference_time_ms=inference_time_ms,
            )
            results.append(item)
            db_results_data.append(
                {
                    "model_id": mid,
                    "predicted_class": predicted_class,
                    "confidence": confidence,
                    "class_probabilities": class_probs,
                    "inference_time_ms": inference_time_ms,
                    "status": "completed",
                }
            )

        except Exception as e:
            logger.warning(f"Comparison run failed on model '{mid}': {e}")
            results.append(
                ModelComparisonResultItem(
                    model_id=mid,
                    display_name=mid,
                    status="failed",
                    error_message=str(e),
                )
            )
            db_results_data.append(
                {
                    "model_id": mid,
                    "status": "failed",
                    "error_message": str(e),
                }
            )

    # Persist comparison in database
    comp_record = ComparisonRepository.create_comparison(
        db=db,
        image_sha256=image_sha256,
        requested_model_ids=model_ids,
        results=db_results_data,
        status="completed",
    )

    warnings = [
        MEDICAL_DISCLAIMER,
        "Disagreement between AI models is an experimental comparison and does not constitute a clinical second opinion.",
    ]

    return ComparisonResponse(
        comparison_id=comp_record.id,
        image_sha256=image_sha256,
        requested_models=model_ids,
        results=results,
        created_at=comp_record.created_at,
        warnings=warnings,
    )
