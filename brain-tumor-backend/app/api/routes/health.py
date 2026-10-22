"""Health check endpoints providing real-time database and model operational status."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.services.model_registry import registry
from app.schemas.model_schemas import HealthResponse
from app.db.models import utc_now
from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Health"])


def check_system_health(db: Session) -> HealthResponse:
    """Evaluate database connectivity and operational model availability."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Health check database query failed: {e}")
        db_status = f"error: {str(e)}"

    models = registry.get_all_models()
    model_statuses = {m.model_id: m.status for m in models}
    loaded_count = sum(1 for s in model_statuses.values() if s == "loaded")
    total_count = len(models)

    if db_status == "connected" and loaded_count == total_count:
        overall_status = "healthy"
    elif db_status == "connected" and loaded_count > 0:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    return HealthResponse(
        status=overall_status,
        database=db_status,
        loaded_models_count=loaded_count,
        total_models_count=total_count,
        models=model_statuses,
        timestamp=utc_now(),
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Root Health Check",
    description="Inspect overall service readiness, database connection, and loaded models.",
)
def root_health_check(response: Response, db: Session = Depends(get_db)):
    health = check_system_health(db)
    if health.status == "unhealthy":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return health


@router.get(
    "/api/v1/health",
    response_model=HealthResponse,
    summary="API v1 Health Check",
    description="Inspect overall service readiness, database connection, and loaded models under v1 prefix.",
)
def v1_health_check(response: Response, db: Session = Depends(get_db)):
    health = check_system_health(db)
    if health.status == "unhealthy":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return health
