"""Pytest fixtures and test doubles for NeuroVision AI backend."""

import io
from pathlib import Path
from typing import Generator
import numpy as np
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.config import settings, BASE_DIR
from app.db.database import Base, get_db
from app.services.model_registry import registry, RegisteredModel

# In-memory SQLite engine for isolated automated tests
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


class TestDoubleKerasModel:
    """Dynamic test double for Keras models.

    Computes deterministic probabilities directly from image tensor statistics
    rather than returning fixed hardcoded outputs.
    """

    def __init__(self, output_classes: int = 4):
        self.input_shape = (None, 224, 224, 3)
        self.output_shape = (None, output_classes)
        self.output_classes = output_classes

    def __call__(self, x: np.ndarray, training: bool = False):
        # Validate expected input tensor shape
        assert x.ndim == 4, f"Expected 4D tensor, got {x.ndim}D"
        assert x.shape[1:] == (224, 224, 3), f"Expected shape (N, 224, 224, 3), got {x.shape}"
        assert np.all(np.isfinite(x)), "Input contains non-finite values"

        # Compute dynamic scores based on tensor channel statistics
        r_mean = float(np.mean(x[..., 0]))
        g_mean = float(np.mean(x[..., 1]))
        b_mean = float(np.mean(x[..., 2]))
        total_std = float(np.std(x)) + 1e-5

        # Create unnormalized dynamic logits
        logits = np.array([
            (r_mean + 10.0) / total_std,
            (g_mean + 5.0) / total_std,
            (b_mean + 2.0) / total_std,
            (r_mean + g_mean) / (2 * total_std),
        ], dtype=np.float32)

        # Apply softmax to generate valid probability distribution
        exp_vals = np.exp(logits - np.max(logits))
        probs = exp_vals / np.sum(exp_vals)
        return np.expand_dims(probs, axis=0)

    def count_params(self):
        return 7851431


@pytest.fixture(scope="session", autouse=True)
def setup_test_registry():
    """Ensure registry has models registered and test doubles attached when needed."""
    registry.initialize_registry()

    # If local .keras files are not loaded in the test environment, attach test doubles
    for model in registry.get_all_models():
        if model.status != "loaded":
            test_double = TestDoubleKerasModel()
            model.instance = test_double
            model.status = "loaded"
            model.input_shape = [None, 224, 224, 3]
            model.output_shape = [None, 4]
            model.parameter_count = 7851431
            model.trainable_parameter_count = 804996
            model.non_trainable_parameter_count = 7046435


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Provide a fresh, isolated database session per test function."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Test client with test database dependency override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def valid_mri_image_bytes() -> bytes:
    """Generate a valid 224x224 RGB test brain MRI image in JPEG format."""
    img = Image.new("RGB", (224, 224), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    # Draw simulated brain contour and tumor-like ellipse
    draw.ellipse([30, 30, 194, 194], fill=(120, 120, 120), outline=(200, 200, 200))
    draw.ellipse([80, 80, 130, 130], fill=(240, 240, 240))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


@pytest.fixture
def valid_png_image_bytes() -> bytes:
    """Generate a valid 224x224 RGB test image in PNG format."""
    img = Image.new("RGB", (224, 224), color=(40, 40, 40))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 170, 170], fill=(160, 160, 160))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def corrupt_image_bytes() -> bytes:
    """Corrupted image payload simulating broken file transfer."""
    return b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x00\x00\x01broken_corrupt_data"
