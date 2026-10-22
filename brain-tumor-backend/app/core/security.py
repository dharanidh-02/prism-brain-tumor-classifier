"""Security utility functions for filename sanitization, path validation, and CSV protection."""

import re
import uuid
from pathlib import Path
from typing import Any
from app.core.exceptions import ImageValidationError


def sanitize_filename(filename: str) -> str:
    """Sanitize original client filename to prevent path injection and strange chars."""
    if not filename:
        return "unnamed_image.png"
    # Remove any directory parts
    clean_name = Path(filename).name
    # Keep only alphanumeric, dot, underscore, dash
    clean_name = re.sub(r"[^a-zA-Z0-9._-]", "_", clean_name)
    # Truncate if excessively long
    if len(clean_name) > 100:
        stem = clean_name[:80]
        ext = Path(clean_name).suffix
        clean_name = f"{stem}{ext}"
    return clean_name


def generate_secure_filename(original_extension: str) -> str:
    """Generate unpredictable unique filename for local persistence."""
    ext = original_extension.lower().strip()
    if not ext.startswith("."):
        ext = f".{ext}"
    if ext not in [".jpg", ".jpeg", ".png"]:
        ext = ".png"
    return f"{uuid.uuid4().hex}{ext}"


def validate_safe_path(target_file: Path, base_dir: Path) -> Path:
    """Verify that target_file strictly resides within base_dir to block path traversal."""
    resolved_target = target_file.resolve()
    resolved_base = base_dir.resolve()
    try:
        resolved_target.relative_to(resolved_base)
    except ValueError:
        raise ImageValidationError("Invalid file path detected (path traversal attempt).")
    return resolved_target


def sanitize_for_csv(value: Any) -> str:
    """Sanitize cell value to prevent CSV / Spreadsheet formula injection.

    Prepends a single quote if the string begins with =, +, -, @, tab, or carriage return.
    """
    if value is None:
        return ""
    val_str = str(value)
    # Check for potential spreadsheet command prefixes
    if val_str and val_str[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{val_str}"
    return val_str
