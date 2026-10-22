"""Pydantic schemas for prediction and comparison requests and responses."""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    """Schema returned after a successful MRI prediction."""

    prediction_id: int
    model_id: str
    predicted_class: str
    confidence: float
    class_probabilities: Dict[str, float]
    inference_time_ms: float
    image_sha256: str
    created_at: datetime
    warnings: List[str] = Field(default_factory=list)


class ModelComparisonResultItem(BaseModel):
    """Individual model outcome in a multi-model comparison."""

    model_id: str
    display_name: str
    status: str
    predicted_class: Optional[str] = None
    confidence: Optional[float] = None
    class_probabilities: Optional[Dict[str, float]] = None
    inference_time_ms: Optional[float] = None
    error_message: Optional[str] = None


class ComparisonResponse(BaseModel):
    """Multi-model comparison response schema."""

    comparison_id: int
    image_sha256: str
    requested_models: List[str]
    results: List[ModelComparisonResultItem]
    created_at: datetime
    warnings: List[str] = Field(default_factory=list)
