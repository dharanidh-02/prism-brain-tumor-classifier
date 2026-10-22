"""Pydantic schemas for prediction history retrieval and filtering."""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel


class PredictionHistoryItem(BaseModel):
    """Detailed prediction record from database."""

    id: int
    model_id: str
    predicted_class: str
    confidence: float
    class_probabilities: Dict[str, float]
    inference_time_ms: float
    image_sha256: str
    original_filename: Optional[str] = None
    image_saved: bool
    created_at: datetime
    status: str
    error_message: Optional[str] = None


class PaginatedHistoryResponse(BaseModel):
    """Paginated list of prediction records."""

    items: List[PredictionHistoryItem]
    total: int
    limit: int
    offset: int
