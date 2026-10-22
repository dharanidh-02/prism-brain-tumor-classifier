"""Database repositories handling CRUD operations and queries."""

import json
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from app.db.models import (
    Prediction,
    ModelArtifact,
    ModelComparison,
    ModelComparisonResult,
    utc_now,
)
from app.logging_config import get_logger

logger = get_logger(__name__)


class PredictionRepository:
    """Repository for managing Prediction database records."""

    @staticmethod
    def create(
        db: Session,
        model_id: str,
        predicted_class: str,
        confidence: float,
        class_probabilities: Dict[str, float],
        inference_time_ms: float,
        image_sha256: str,
        original_filename: Optional[str] = None,
        image_path: Optional[str] = None,
        image_saved: bool = False,
        status: str = "completed",
        error_message: Optional[str] = None,
    ) -> Prediction:
        try:
            record = Prediction(
                model_id=model_id,
                predicted_class=predicted_class,
                confidence=confidence,
                class_probabilities_json=json.dumps(class_probabilities),
                inference_time_ms=inference_time_ms,
                image_sha256=image_sha256,
                original_filename=original_filename,
                image_path=image_path,
                image_saved=image_saved,
                status=status,
                error_message=error_message,
                created_at=utc_now(),
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create prediction record: {e}", exc_info=True)
            raise

    @staticmethod
    def get_by_id(db: Session, prediction_id: int) -> Optional[Prediction]:
        return db.query(Prediction).filter(Prediction.id == prediction_id).first()

    @staticmethod
    def list_predictions(
        db: Session,
        limit: int = 20,
        offset: int = 0,
        predicted_class: Optional[str] = None,
        model_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Tuple[List[Prediction], int]:
        query = db.query(Prediction)

        if predicted_class:
            query = query.filter(Prediction.predicted_class == predicted_class)
        if model_id:
            query = query.filter(Prediction.model_id == model_id)
        if start_date:
            query = query.filter(Prediction.created_at >= start_date)
        if end_date:
            query = query.filter(Prediction.created_at <= end_date)

        total_count = query.count()
        records = (
            query.order_by(desc(Prediction.created_at), desc(Prediction.id))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return records, total_count

    @staticmethod
    def delete_by_id(db: Session, prediction_id: int) -> Optional[Prediction]:
        record = db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if not record:
            return None
        try:
            db.delete(record)
            db.commit()
            return record
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete prediction {prediction_id}: {e}", exc_info=True)
            raise

    @staticmethod
    def get_for_export(
        db: Session,
        predicted_class: Optional[str] = None,
        model_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 5000,
    ) -> List[Prediction]:
        query = db.query(Prediction)
        if predicted_class:
            query = query.filter(Prediction.predicted_class == predicted_class)
        if model_id:
            query = query.filter(Prediction.model_id == model_id)
        if start_date:
            query = query.filter(Prediction.created_at >= start_date)
        if end_date:
            query = query.filter(Prediction.created_at <= end_date)

        return (
            query.order_by(desc(Prediction.created_at), desc(Prediction.id))
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_analytics_summary(db: Session) -> Dict[str, Any]:
        total_predictions = db.query(func.count(Prediction.id)).scalar() or 0

        # Predictions by class
        class_counts = (
            db.query(Prediction.predicted_class, func.count(Prediction.id))
            .group_by(Prediction.predicted_class)
            .all()
        )
        by_class = {cls_name: count for cls_name, count in class_counts}

        # Predictions by model
        model_counts = (
            db.query(Prediction.model_id, func.count(Prediction.id))
            .group_by(Prediction.model_id)
            .all()
        )
        by_model = {mid: count for mid, count in model_counts}

        # Average inference duration
        avg_duration = (
            db.query(func.avg(Prediction.inference_time_ms))
            .filter(Prediction.status == "completed")
            .scalar()
        )
        avg_time = round(float(avg_duration), 2) if avg_duration is not None else 0.0

        # Recent 24h count
        cutoff_24h = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_count = (
            db.query(func.count(Prediction.id))
            .filter(Prediction.created_at >= cutoff_24h)
            .scalar()
            or 0
        )

        return {
            "total_predictions": total_predictions,
            "predictions_by_class": by_class,
            "predictions_by_model": by_model,
            "average_inference_time_ms": avg_time,
            "recent_predictions_24h": recent_count,
        }


class ModelArtifactRepository:
    """Repository for managing ModelArtifact metadata records."""

    @staticmethod
    def upsert_artifact(
        db: Session,
        model_id: str,
        display_name: str,
        model_path: str,
        model_sha256: Optional[str] = None,
        input_shape: Optional[Any] = None,
        output_shape: Optional[Any] = None,
        parameter_count: Optional[int] = None,
        status: str = "unloaded",
        last_loaded_at: Optional[datetime] = None,
    ) -> ModelArtifact:
        try:
            artifact = db.query(ModelArtifact).filter(ModelArtifact.model_id == model_id).first()
            if not artifact:
                artifact = ModelArtifact(
                    model_id=model_id,
                    display_name=display_name,
                    model_path=model_path,
                    model_sha256=model_sha256,
                    input_shape_json=json.dumps(input_shape) if input_shape else None,
                    output_shape_json=json.dumps(output_shape) if output_shape else None,
                    parameter_count=parameter_count,
                    status=status,
                    last_loaded_at=last_loaded_at,
                )
                db.add(artifact)
            else:
                artifact.display_name = display_name
                artifact.model_path = model_path
                if model_sha256:
                    artifact.model_sha256 = model_sha256
                if input_shape:
                    artifact.input_shape_json = json.dumps(input_shape)
                if output_shape:
                    artifact.output_shape_json = json.dumps(output_shape)
                if parameter_count is not None:
                    artifact.parameter_count = parameter_count
                artifact.status = status
                if last_loaded_at:
                    artifact.last_loaded_at = last_loaded_at
                artifact.updated_at = utc_now()

            db.commit()
            db.refresh(artifact)
            return artifact
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to upsert model artifact {model_id}: {e}", exc_info=True)
            raise

    @staticmethod
    def get_by_model_id(db: Session, model_id: str) -> Optional[ModelArtifact]:
        return db.query(ModelArtifact).filter(ModelArtifact.model_id == model_id).first()

    @staticmethod
    def list_all(db: Session) -> List[ModelArtifact]:
        return db.query(ModelArtifact).order_by(ModelArtifact.id.asc()).all()


class ComparisonRepository:
    """Repository for managing ModelComparison and ModelComparisonResult records."""

    @staticmethod
    def create_comparison(
        db: Session,
        image_sha256: str,
        requested_model_ids: List[str],
        results: List[Dict[str, Any]],
        status: str = "completed",
    ) -> ModelComparison:
        try:
            comparison = ModelComparison(
                image_sha256=image_sha256,
                requested_model_ids_json=json.dumps(requested_model_ids),
                status=status,
                created_at=utc_now(),
            )
            db.add(comparison)
            db.flush()

            for res in results:
                child = ModelComparisonResult(
                    comparison_id=comparison.id,
                    model_id=res["model_id"],
                    predicted_class=res.get("predicted_class"),
                    confidence=res.get("confidence"),
                    class_probabilities_json=(
                        json.dumps(res.get("class_probabilities"))
                        if res.get("class_probabilities")
                        else None
                    ),
                    inference_time_ms=res.get("inference_time_ms"),
                    status=res.get("status", "completed"),
                    error_message=res.get("error_message"),
                )
                db.add(child)

            db.commit()
            db.refresh(comparison)
            return comparison
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save comparison run: {e}", exc_info=True)
            raise
