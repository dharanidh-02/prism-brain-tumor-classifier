"""Analytics and model evaluation performance endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.analytics_service import (
    get_analytics_overview,
    get_model_performance_benchmarks,
)
from app.schemas.analytics_schemas import (
    AnalyticsOverviewResponse,
    ModelPerformanceResponse,
)

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    summary="Get System Analytics Overview",
    description=(
        "Retrieve aggregated usage metrics including total predictions, predictions per tumor class, "
        "model utilization, average inference latency, and operational model counts."
    ),
)
def analytics_overview(db: Session = Depends(get_db)):
    return get_analytics_overview(db)


@router.get(
    "/model-performance",
    response_model=ModelPerformanceResponse,
    summary="Get Verified Model Performance Metrics",
    description=(
        "Retrieve verified benchmark evaluation metrics (accuracy, precision, recall, F1, ROC-AUC) "
        "and provenance statements for each trained model artifact. Metrics are strictly benchmark-based."
    ),
)
def model_performance():
    return get_model_performance_benchmarks()
