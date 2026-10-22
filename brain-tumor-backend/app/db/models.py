"""SQLAlchemy ORM models for database persistence."""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from app.db.database import Base


def utc_now() -> datetime:
    """Helper returning UTC timezone-aware datetime."""
    return datetime.now(timezone.utc)


class Prediction(Base):
    """Stores individual MRI prediction outcomes and metadata."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model_id = Column(String(64), nullable=False, index=True)
    predicted_class = Column(String(64), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    class_probabilities_json = Column(Text, nullable=False)
    inference_time_ms = Column(Float, nullable=False)
    image_sha256 = Column(String(64), nullable=False, index=True)
    original_filename = Column(String(255), nullable=True)
    image_path = Column(String(512), nullable=True)
    image_saved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    status = Column(String(32), default="completed", nullable=False)
    error_message = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_predictions_class_created", "predicted_class", "created_at"),
        Index("ix_predictions_model_created", "model_id", "created_at"),
    )


class ModelArtifact(Base):
    """Tracks registered Keras model artifacts and inspected properties."""

    __tablename__ = "model_artifacts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model_id = Column(String(64), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    model_path = Column(String(512), nullable=False)
    model_sha256 = Column(String(64), nullable=True)
    input_shape_json = Column(Text, nullable=True)
    output_shape_json = Column(Text, nullable=True)
    parameter_count = Column(Integer, nullable=True)
    status = Column(String(32), default="unloaded", nullable=False)
    last_loaded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class ModelComparison(Base):
    """Parent record for multi-model image comparison runs."""

    __tablename__ = "model_comparisons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_sha256 = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    requested_model_ids_json = Column(Text, nullable=False)
    status = Column(String(32), default="completed", nullable=False)

    results = relationship(
        "ModelComparisonResult",
        back_populates="comparison",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ModelComparisonResult(Base):
    """Individual model outcome within a comparison run."""

    __tablename__ = "model_comparison_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    comparison_id = Column(
        Integer,
        ForeignKey("model_comparisons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    model_id = Column(String(64), nullable=False)
    predicted_class = Column(String(64), nullable=True)
    confidence = Column(Float, nullable=True)
    class_probabilities_json = Column(Text, nullable=True)
    inference_time_ms = Column(Float, nullable=True)
    status = Column(String(32), nullable=False)  # "completed" or "failed"
    error_message = Column(Text, nullable=True)

    comparison = relationship("ModelComparison", back_populates="results")
