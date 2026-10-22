"""Application custom exceptions and error models."""

from typing import Any, Optional
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.logging_config import get_logger

logger = get_logger(__name__)


class NeuroVisionException(Exception):
    """Base exception for all NeuroVision application errors."""

    def __init__(self, message: str, status_code: int = 500, error_code: str = "INTERNAL_SERVER_ERROR"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class ModelNotFoundError(NeuroVisionException):
    """Raised when a requested model ID is not registered."""

    def __init__(self, model_id: str):
        super().__init__(
            message=f"Model '{model_id}' was not found in the registry.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="MODEL_NOT_FOUND",
        )


class ModelUnavailableError(NeuroVisionException):
    """Raised when a model is registered but cannot be loaded or is offline."""

    def __init__(self, model_id: str, reason: str = "Model is currently unavailable"):
        super().__init__(
            message=f"Model '{model_id}' is unavailable: {reason}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="MODEL_UNAVAILABLE",
        )


class ImageValidationError(NeuroVisionException):
    """Raised when an uploaded image fails validation checks."""

    def __init__(self, reason: str):
        super().__init__(
            message=f"Image validation failed: {reason}",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_IMAGE",
        )


class PredictionError(NeuroVisionException):
    """Raised when inference execution fails."""

    def __init__(self, reason: str):
        super().__init__(
            message=f"Prediction failed: {reason}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="PREDICTION_FAILED",
        )


class ResourceNotFoundError(NeuroVisionException):
    """Raised when an entity is not found in database."""

    def __init__(self, resource_name: str, identifier: Any):
        super().__init__(
            message=f"{resource_name} with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Register uniform JSON error handlers with the FastAPI app."""

    @app.exception_handler(NeuroVisionException)
    async def handle_neurovision_exception(request: Request, exc: NeuroVisionException):
        logger.warning(
            f"Handled app exception on {request.method} {request.url.path}: {exc.message} [{exc.error_code}]"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "detail": exc.message,
                "path": request.url.path,
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(request: Request, exc: Exception):
        logger.error(
            f"Unhandled server error on {request.method} {request.url.path}: {str(exc)}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "detail": "An unexpected internal server error occurred.",
                "path": request.url.path,
            },
        )
