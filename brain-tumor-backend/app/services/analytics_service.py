"""Analytics service generating usage overview and model evaluation benchmarks."""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.repositories import PredictionRepository
from app.services.model_registry import registry
from app.db.models import utc_now
from app.schemas.analytics_schemas import (
    AnalyticsOverviewResponse,
    ModelPerformanceResponse,
    ModelPerformanceItem,
    EvaluationMetricDetail,
)


def get_analytics_overview(db: Session) -> AnalyticsOverviewResponse:
    """Aggregate application prediction volume, class distribution, and model availability."""
    summary = PredictionRepository.get_analytics_summary(db)
    models = registry.get_all_models()

    operational_count = sum(1 for m in models if m.status == "loaded")
    unavailable_count = len(models) - operational_count

    if operational_count == len(models):
        system_status = "operational"
    elif operational_count > 0:
        system_status = "degraded"
    else:
        system_status = "offline"

    return AnalyticsOverviewResponse(
        total_predictions=summary["total_predictions"],
        predictions_by_class=summary["predictions_by_class"],
        predictions_by_model=summary["predictions_by_model"],
        recent_predictions_24h=summary["recent_predictions_24h"],
        average_inference_time_ms=summary["average_inference_time_ms"],
        operational_models_count=operational_count,
        unavailable_models_count=unavailable_count,
        system_status=system_status,
    )


def get_model_performance_benchmarks() -> ModelPerformanceResponse:
    """Return verified and project-reported benchmark metrics with strict provenance distinction."""
    items: list[ModelPerformanceItem] = []

    # Model A: Phase 1 Trained Artifact
    items.append(
        ModelPerformanceItem(
            model_id="hybrid_v1",
            display_name="Hybrid EfficientNetB0 + MobileNetV3 (Attention)",
            total_parameters=7851431,
            trainable_parameters=804996,
            non_trainable_parameters=7046435,
            reported_file_size_mb=37.56,
            metrics=EvaluationMetricDetail(
                test_accuracy=0.9312,
                test_loss=0.3425,
                evaluation_dataset="Brain Tumor MRI Kaggle Dataset (4-class)",
                evaluation_split="Test Split (Holdout)",
                provenance="Project Phase 1 Test Evaluation",
                verification_status="project_reported_unverified",
                notes="Phase 1 initial hybrid training run with frozen backbones.",
            ),
        )
    )

    # Model B: Phase 1 Final Artifact
    items.append(
        ModelPerformanceItem(
            model_id="hybrid_v1_final",
            display_name="Hybrid EfficientNetB0 + MobileNetV3 (Final Attention)",
            total_parameters=7851431,
            trainable_parameters=804996,
            non_trainable_parameters=7046435,
            reported_file_size_mb=37.56,
            metrics=EvaluationMetricDetail(
                test_accuracy=0.9312,
                test_loss=0.3425,
                evaluation_dataset="Brain Tumor MRI Kaggle Dataset (4-class)",
                evaluation_split="Test Split (Holdout)",
                provenance="Project Phase 1 Final Artifact Evaluation",
                verification_status="project_reported_unverified",
                notes="Final saved artifact from Phase 1 training run.",
            ),
        )
    )

    # Model C: Phase 2 Fine-tuned Checkpoint
    items.append(
        ModelPerformanceItem(
            model_id="hybrid_v2_finetuned",
            display_name="Hybrid Fine-tuned (Phase 2 Checkpoint)",
            total_parameters=7851431,
            trainable_parameters=804996,
            non_trainable_parameters=7046435,
            reported_file_size_mb=61.0,
            metrics=EvaluationMetricDetail(
                test_accuracy=0.9281,
                test_loss=0.3408,
                macro_precision=0.9289,
                macro_recall=0.9281,
                macro_f1_score=0.9268,
                macro_roc_auc=0.9851,
                evaluation_dataset="Brain Tumor MRI Kaggle Dataset (4-class)",
                evaluation_split="Phase 2 Fine-tuned Test Split",
                provenance="Project Phase 2 Test Evaluation",
                verification_status="project_reported_unverified",
                notes="Phase 2 checkpoint with unfrozen backbone fine-tuning.",
            ),
        )
    )

    return ModelPerformanceResponse(
        disclaimer=(
            "Model performance metrics reflect fixed evaluation benchmarks on test splits "
            "and are NEVER calculated from user uploads (ground-truth labels unavailable)."
        ),
        models=items,
        retrieved_at=utc_now(),
    )
