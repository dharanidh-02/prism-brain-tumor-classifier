"""Central Model Registry Service for managing and serving Keras models."""

import os
import time
import hashlib
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np

# Suppress TensorFlow verbose logging
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

try:
    import keras
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False

from app.config import settings
from app.logging_config import get_logger
from app.core.exceptions import ModelNotFoundError, ModelUnavailableError, PredictionError
from app.db.models import utc_now

logger = get_logger(__name__)


class RegisteredModel:
    """Encapsulates a single model's runtime instance and metadata."""

    def __init__(
        self,
        model_id: str,
        display_name: str,
        model_path: str,
        description: str,
        phase: str,
    ):
        self.model_id = model_id
        self.display_name = display_name
        self.model_path = model_path
        self.description = description
        self.phase = phase

        self.instance: Any = None
        self.status: str = "unloaded"  # "loaded", "unavailable", "failed_to_load"
        self.sha256: Optional[str] = None
        self.input_shape: Optional[List[Optional[int]]] = None
        self.output_shape: Optional[List[Optional[int]]] = None
        self.parameter_count: Optional[int] = None
        self.trainable_parameter_count: Optional[int] = None
        self.non_trainable_parameter_count: Optional[int] = None
        self.load_duration_ms: Optional[float] = None
        self.last_loaded_at: Optional[Any] = None
        self.error_message: Optional[str] = None

    def compute_sha256(self) -> Optional[str]:
        """Compute SHA256 checksum of the model file if it exists."""
        p = Path(self.model_path)
        if not p.is_file():
            return None
        sha = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                sha.update(chunk)
        self.sha256 = sha.hexdigest()
        return self.sha256


class ModelRegistry:
    """Thread-safe Central Model Registry."""

    def __init__(self):
        self._models: Dict[str, RegisteredModel] = {}
        self._load_lock = threading.Lock()
        self._inference_locks: Dict[str, threading.Lock] = {}
        self._initialized = False

    def initialize_registry(self) -> None:
        """Register all configured model definitions and optionally eager-load."""
        with self._load_lock:
            if self._initialized:
                return

            definitions = settings.get_model_definitions()
            for model_id, cfg in definitions.items():
                registered = RegisteredModel(
                    model_id=model_id,
                    display_name=cfg["display_name"],
                    model_path=cfg["path"],
                    description=cfg["description"],
                    phase=cfg["phase"],
                )
                registered.compute_sha256()
                self._models[model_id] = registered
                self._inference_locks[model_id] = threading.Lock()

            self._initialized = True
            logger.info(f"Model registry registered {len(self._models)} models.")

            if settings.MODEL_LOADING_STRATEGY == "eager":
                logger.info("Eager loading all configured models...")
                for model_id in self._models:
                    self._load_single_model(model_id)

    def _load_single_model(self, model_id: str) -> bool:
        """Load a specific model file into memory."""
        registered = self._models.get(model_id)
        if not registered:
            return False

        p = Path(registered.model_path)
        if not p.is_file():
            registered.status = "unavailable"
            registered.error_message = f"Model file not found at path: {registered.model_path}"
            logger.warning(registered.error_message)
            return False

        if not KERAS_AVAILABLE:
            registered.status = "failed_to_load"
            registered.error_message = "Keras library is not installed in the environment."
            logger.error(registered.error_message)
            return False

        logger.info(f"Loading model '{model_id}' from {registered.model_path}...")
        start_time = time.perf_counter()
        try:
            # Load with compile=False for optimal inference startup
            model = keras.models.load_model(str(p), compile=False)
            registered.instance = model
            registered.status = "loaded"
            registered.last_loaded_at = utc_now()
            registered.load_duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            registered.error_message = None

            # Inspect input/output shapes safely
            try:
                registered.input_shape = list(model.input_shape)
            except Exception:
                registered.input_shape = [None, 224, 224, 3]

            try:
                registered.output_shape = list(model.output_shape)
            except Exception:
                registered.output_shape = [None, 4]

            # Inspect parameter counts
            try:
                trainable = sum(int(np.prod(w.shape)) for w in model.trainable_weights)
                non_trainable = sum(int(np.prod(w.shape)) for w in model.non_trainable_weights)
                registered.trainable_parameter_count = trainable
                registered.non_trainable_parameter_count = non_trainable
                registered.parameter_count = trainable + non_trainable
            except Exception:
                try:
                    registered.parameter_count = model.count_params()
                except Exception:
                    pass

            logger.info(
                f"Model '{model_id}' successfully loaded in {registered.load_duration_ms} ms. "
                f"Input shape: {registered.input_shape}, Output shape: {registered.output_shape}, "
                f"Total params: {registered.parameter_count}"
            )
            return True

        except Exception as e:
            registered.status = "failed_to_load"
            registered.error_message = f"Failed to load model: {str(e)}"
            registered.load_duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                f"Error loading model '{model_id}' from {registered.model_path}: {e}",
                exc_info=True,
            )
            return False

    def get_model(self, model_id: str) -> RegisteredModel:
        """Retrieve model metadata or load on demand if lazy strategy."""
        if not self._initialized:
            self.initialize_registry()

        if model_id not in self._models:
            raise ModelNotFoundError(model_id)

        model = self._models[model_id]
        if model.status == "unloaded":
            with self._load_lock:
                if model.status == "unloaded":
                    self._load_single_model(model_id)

        return model

    def get_all_models(self) -> List[RegisteredModel]:
        """Return list of all registered models."""
        if not self._initialized:
            self.initialize_registry()
        return list(self._models.values())

    def run_inference(self, model_id: str, input_tensor: np.ndarray) -> np.ndarray:
        """Execute thread-safe model inference on input tensor.

        Args:
            model_id: Target model identifier.
            input_tensor: NumPy array with shape (1, 224, 224, 3), float32.

        Returns:
            NumPy array of predictions with shape (1, 4).
        """
        registered = self.get_model(model_id)
        if registered.status != "loaded" or registered.instance is None:
            raise ModelUnavailableError(
                model_id,
                registered.error_message or "Model is not loaded or operational.",
            )

        lock = self._inference_locks.get(model_id)
        if not lock:
            raise PredictionError(f"Inference lock missing for model '{model_id}'")

        with lock:
            try:
                # Forward pass in inference mode
                output = registered.instance(input_tensor, training=False)
                if hasattr(output, "numpy"):
                    output_arr = output.numpy()
                else:
                    output_arr = np.array(output)
                return output_arr
            except Exception as e:
                logger.error(f"Inference error on model '{model_id}': {e}", exc_info=True)
                raise PredictionError(f"Execution failed on model '{model_id}': {str(e)}")


# Global singleton instance
registry = ModelRegistry()
