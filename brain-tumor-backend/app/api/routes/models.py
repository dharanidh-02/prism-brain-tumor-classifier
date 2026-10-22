"""Model registry management and status API endpoints."""

from typing import List
from fastapi import APIRouter
from app.services.model_registry import registry
from app.schemas.model_schemas import (
    ModelSummaryResponse,
    ModelDetailResponse,
    ModelStatusResponse,
)
from app.db.models import utc_now

router = APIRouter(prefix="/api/v1/models", tags=["Models"])


@router.get(
    "",
    response_model=List[ModelSummaryResponse],
    summary="List All Registered Models",
    description="Retrieve all configured Brain Tumor MRI classification models and operational status.",
)
def list_models():
    models = registry.get_all_models()
    return [
        ModelSummaryResponse(
            model_id=m.model_id,
            display_name=m.display_name,
            status=m.status,
            description=m.description,
            parameter_count=m.parameter_count,
            input_shape=m.input_shape,
            output_shape=m.output_shape,
        )
        for m in models
    ]


@router.get(
    "/{model_id}",
    response_model=ModelDetailResponse,
    summary="Get Model Details",
    description="Retrieve full metadata, architecture parameters, and verified benchmarks for a specific model.",
)
def get_model_details(model_id: str):
    m = registry.get_model(model_id)
    return ModelDetailResponse(
        model_id=m.model_id,
        display_name=m.display_name,
        model_path=m.model_path,
        model_sha256=m.sha256,
        status=m.status,
        load_duration_ms=m.load_duration_ms,
        last_loaded_at=m.last_loaded_at,
        error_message=m.error_message,
        input_shape=m.input_shape,
        output_shape=m.output_shape,
        parameter_count=m.parameter_count,
        trainable_parameter_count=m.trainable_parameter_count,
        non_trainable_parameter_count=m.non_trainable_parameter_count,
        description=m.description,
        phase=m.phase,
    )


@router.get(
    "/{model_id}/status",
    response_model=ModelStatusResponse,
    summary="Get Model Operational Status",
    description="Quick operational health check for a given model identifier.",
)
def get_model_status(model_id: str):
    m = registry.get_model(model_id)
    return ModelStatusResponse(
        model_id=m.model_id,
        display_name=m.display_name,
        status=m.status,
        is_operational=(m.status == "loaded"),
        last_checked_at=utc_now(),
        error_message=m.error_message,
    )
