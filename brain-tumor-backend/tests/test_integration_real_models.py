"""Integration test executing real inference against accessible .keras model files."""

import os
from pathlib import Path
import pytest
from PIL import Image
import numpy as np

from app.config import settings
from app.services.image_preprocessing import preprocess_mri_image
from app.services.model_registry import registry


def test_real_keras_models_inference_if_accessible(valid_mri_image_bytes: bytes):
    """Integration test: loads genuine .keras files and verifies real forward pass."""
    definitions = settings.get_model_definitions()

    tested_any = False
    for model_id, cfg in definitions.items():
        model_path = Path(cfg["path"])
        if not model_path.is_file():
            pytest.skip(f"Model file for {model_id} not accessible at {model_path}")
            continue

        tested_any = True
        registered = registry.get_model(model_id)
        assert registered.status == "loaded", f"Model {model_id} failed to load: {registered.error_message}"

        # Preprocess test image
        img = Image.new("RGB", (224, 224), color=(30, 30, 30))
        tensor = preprocess_mri_image(img)

        # Run real forward pass
        raw_output = registry.run_inference(model_id, tensor)
        assert raw_output.shape == (1, 4), f"Expected shape (1, 4), got {raw_output.shape}"
        assert np.all(np.isfinite(raw_output)), "Output contains NaN or Inf"

        # Check probability output
        probs = raw_output[0]
        assert np.isclose(np.sum(probs), 1.0, atol=1e-2), f"Probabilities do not sum to 1.0: {probs}"
        assert np.all(probs >= 0.0) and np.all(probs <= 1.0), f"Values out of bounds: {probs}"

    if not tested_any:
        pytest.skip("No real model files were accessible on disk for integration testing.")
