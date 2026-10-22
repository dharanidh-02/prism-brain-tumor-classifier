"""Image validation utility verifying file size, extensions, integrity, and dimensions."""

import io
import hashlib
from pathlib import Path
from typing import Tuple
from PIL import Image, ImageOps
from app.config import settings
from app.core.exceptions import ImageValidationError
from app.logging_config import get_logger

logger = get_logger(__name__)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MIN_DIMENSION = 32
MAX_DIMENSION = 4096


def validate_image_file(
    content: bytes,
    original_filename: str,
) -> Tuple[Image.Image, str]:
    """Validate raw image payload for security, format, size, and integrity.

    Args:
        content: Raw bytes from the uploaded file.
        original_filename: The client-provided file name.

    Returns:
        A tuple of (Opened PIL Image, SHA-256 hex string).

    Raises:
        ImageValidationError: If any check fails.
    """
    if not content or len(content) == 0:
        raise ImageValidationError("Uploaded image file is empty (0 bytes).")

    if len(content) > settings.max_upload_size_bytes:
        raise ImageValidationError(
            f"Image file exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    # Validate file extension
    ext = Path(original_filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ImageValidationError(
            f"Unsupported file extension '{ext}'. Only JPEG (.jpg, .jpeg) and PNG (.png) are accepted."
        )

    # Compute SHA-256 fingerprint of the original bytes
    sha256_hash = hashlib.sha256(content).hexdigest()

    # Step 1: Verify raw integrity with Pillow
    try:
        buffer = io.BytesIO(content)
        temp_img = Image.open(buffer)
        temp_img.verify()
    except Exception as e:
        logger.warning(f"Corrupt image payload rejected: {e}")
        raise ImageValidationError(f"Corrupted or invalid image data: {str(e)}")

    # Step 2: Reopen for actual pixel operations (since verify closes streams)
    try:
        buffer.seek(0)
        img = Image.open(buffer)
        img.load()  # Ensure full pixel data is decoded into memory
    except Exception as e:
        logger.warning(f"Failed to decode image pixels: {e}")
        raise ImageValidationError(f"Failed to decode image: {str(e)}")

    # Verify format
    if img.format not in ("JPEG", "PNG"):
        raise ImageValidationError(
            f"Image declared format '{img.format}' is unsupported. Only JPEG and PNG are permitted."
        )

    # Verify dimensions
    width, height = img.size
    if width < MIN_DIMENSION or height < MIN_DIMENSION:
        raise ImageValidationError(
            f"Image dimensions ({width}x{height}) are too small. Minimum dimension is {MIN_DIMENSION}px."
        )
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ImageValidationError(
            f"Image dimensions ({width}x{height}) exceed maximum allowed of {MAX_DIMENSION}px."
        )

    # Normalize orientation via EXIF if present
    try:
        img = ImageOps.exif_transpose(img)
    except Exception as e:
        logger.debug(f"Exif transpose skipped: {e}")

    return img, sha256_hash
