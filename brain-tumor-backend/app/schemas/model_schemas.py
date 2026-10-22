"""Pydantic schemas for Model endpoints and registry metadata."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ModelSummaryResponse(BaseModel):
    """Concise representation of registered model."""

    model_id: str
    display_name: str
    status: str = Field(description="'loaded', 'unavailable', or 'failed_to_load'")
    description: str
    parameter_count: Optional[int] = None
    input_shape: Optional[List[Optional[int]]] = None
    output_shape: Optional[List[Optional[int]]] = None


class ModelDetailResponse(BaseModel):
    """Full detail of a registered model including architecture and verified metrics."""

    model_id: str
    display_name: str
    model_path: str
    model_sha256: Optional[str] = None
    status: str
    load_duration_ms: Optional[float] = None
    last_loaded_at: Optional[datetime] = None
    error_message: Optional[str] = None
    input_shape: Optional[List[Optional[int]]] = None
    output_shape: Optional[List[Optional[int]]] = None
    parameter_count: Optional[int] = None
    trainable_parameter_count: Optional[int] = None
    non_trainable_parameter_count: Optional[int] = None
    description: str
    phase: str
    verified_metrics: Optional[Dict[str, Any]] = None


class ModelStatusResponse(BaseModel):
    """Lightweight model health status check."""

    model_id: str
    display_name: str
    status: str
    is_operational: bool
    last_checked_at: datetime
    error_message: Optional[str] = None


class HealthResponse(BaseModel):
    """Service health response."""

    status: str = Field(description="'healthy', 'degraded', or 'unhealthy'")
    database: str
    loaded_models_count: int
    total_models_count: int
    models: Dict[str, str]
    timestamp: datetime
