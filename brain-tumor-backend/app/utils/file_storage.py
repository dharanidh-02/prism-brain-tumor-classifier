"""Safe file storage utilities for optional MRI image persistence."""

from pathlib import Path
from typing import Optional
from app.config import settings
from app.core.security import generate_secure_filename, validate_safe_path
from app.logging_config import get_logger

logger = get_logger(__name__)


def save_uploaded_image(content: bytes, original_extension: str) -> str:
    """Save raw image bytes into upload storage with unpredictable filename."""
    upload_dir = settings.resolved_upload_dir
    filename = generate_secure_filename(original_extension)
    destination = upload_dir / filename
    safe_path = validate_safe_path(destination, upload_dir)

    with open(safe_path, "wb") as f:
        f.write(content)

    logger.info(f"Image successfully persisted to {safe_path.name}")
    return str(safe_path)


def delete_stored_image(file_path_str: Optional[str]) -> bool:
    """Safely remove persisted image file from disk."""
    if not file_path_str:
        return False

    upload_dir = settings.resolved_upload_dir
    target = Path(file_path_str)

    try:
        safe_path = validate_safe_path(target, upload_dir)
        if safe_path.is_file():
            safe_path.unlink()
            logger.info(f"Deleted stored image {safe_path.name}")
            return True
    except Exception as e:
        logger.warning(f"Failed to delete stored image '{file_path_str}': {e}")

    return False
