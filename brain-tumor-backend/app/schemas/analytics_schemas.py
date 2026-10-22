"""Pydantic schemas for analytics and model performance metrics."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AnalyticsOverviewResponse(BaseModel):
    """Aggregated usage and latency analytics."""

    total_predictions: int
    predictions_by_class: Dict[str, int]
    predictions_by_model: Dict[str, int]
    recent_predictions_24h: int
    average_inference_time_ms: float
    operational_models_count: int
    unavailable_models_count: int
    system_status: str


class EvaluationMetricDetail(BaseModel):
    """Detailed evaluation metrics for a specific model evaluation phase."""

    test_accuracy: Optional[float] = None
    test_loss: Optional[float] = None
    macro_precision: Optional[float] = None
    macro_recall: Optional[float] = None
    macro_f1_score: Optional[float] = None
    macro_roc_auc: Optional[float] = None
    evaluation_dataset: str
    evaluation_split: str
    provenance: str
    verification_status: str = Field(
        description="Indicates whether metric is mathematically verified on current artifact or project-reported"
    )
    notes: Optional[str] = None


class ModelPerformanceItem(BaseModel):
    """Performance evaluation record for a model."""

    model_id: str
    display_name: str
    total_parameters: Optional[int] = None
    trainable_parameters: Optional[int] = None
    non_trainable_parameters: Optional[int] = None
    reported_file_size_mb: Optional[float] = None
    metrics: EvaluationMetricDetail


class ModelPerformanceResponse(BaseModel):
    """Response containing known evaluation metrics and clear provenance statements."""

    disclaimer: str = Field(
        default=(
            "Model performance metrics reflect fixed evaluation benchmarks on test splits "
            "and are NEVER calculated from user uploads (ground-truth labels unavailable)."
        )
    )
    models: List[ModelPerformanceItem]
    retrieved_at: datetime
