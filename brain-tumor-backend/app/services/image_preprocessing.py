"""Image preprocessing service preparing MRI images for model inference."""

import numpy as np
from PIL import Image
from app.core.exceptions import ImageValidationError
from app.logging_config import get_logger

logger = get_logger(__name__)

TARGET_SIZE = (224, 224)
EXPECTED_CHANNELS = 3


def preprocess_mri_image(image: Image.Image) -> np.ndarray:
    """Transform validated PIL Image into the exact tensor format expected by models.

    Preprocessing pipeline:
    1. Convert color mode to RGB (ensuring 3 channels).
    2. Resize to 224x224 using high-quality Bicubic resampling.
    3. Convert to float32 NumPy array.
    4. Note on rescaling: Raw pixel values in range [0.0, 255.0] are preserved
       because the trained models internally contain dedicated Rescaling
       and Normalization layers (EfficientNet scales 1/255 and MobileNet scales 1/127.5).
    5. Validate numerical integrity (no NaN or Inf values).
    6. Expand dimensions to create batch tensor: shape (1, 224, 224, 3).

    Args:
        image: Validated PIL Image.

    Returns:
        np.ndarray: Batch tensor with shape (1, 224, 224, 3), dtype float32.

    Raises:
        ImageValidationError: If processing fails or non-finite values are encountered.
    """
    try:
        # Step 1: Ensure RGB
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Step 2: Resize to expected input resolution
        resized_img = image.resize(TARGET_SIZE, resample=Image.Resampling.BICUBIC)

        # Step 3: Array conversion with float32
        arr = np.array(resized_img, dtype=np.float32)

        # Step 4: Validate shape and channels
        if arr.shape != (224, 224, 3):
            raise ImageValidationError(
                f"Unexpected preprocessed shape {arr.shape}. Expected (224, 224, 3)."
            )

        # Step 5: Check numerical finiteness
        if not np.all(np.isfinite(arr)):
            raise ImageValidationError("Non-finite values (NaN or Inf) detected in image tensor.")

        # Step 6: Expand batch dimension
        batch_tensor = np.expand_dims(arr, axis=0)  # Shape (1, 224, 224, 3)

        return batch_tensor

    except ImageValidationError:
        raise
    except Exception as e:
        logger.error(f"Image preprocessing failed: {e}", exc_info=True)
        raise ImageValidationError(f"Image preprocessing pipeline error: {str(e)}")
