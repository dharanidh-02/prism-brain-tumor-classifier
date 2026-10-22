"""FastAPI Application Main Entrypoint for NeuroVision AI (PRISM)."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.logging_config import setup_logging, get_logger
from app.db.database import init_db, SessionLocal
from app.db.repositories import ModelArtifactRepository
from app.core.exceptions import register_exception_handlers
from app.services.model_registry import registry
from app.api.routes import health, models, predictions, history, analytics

# Configure structured logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management for startup and graceful shutdown."""
    logger.info("Initializing NeuroVision AI backend service...")

    # 1. Initialize SQLite Database Schema
    try:
        init_db()
        logger.info("Database schema initialized.")
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}", exc_info=True)

    # 2. Initialize Model Registry
    try:
        registry.initialize_registry()
        logger.info("Model registry initialized.")

        # Sync model state into ModelArtifact table
        db = SessionLocal()
        try:
            for m in registry.get_all_models():
                ModelArtifactRepository.upsert_artifact(
                    db=db,
                    model_id=m.model_id,
                    display_name=m.display_name,
                    model_path=m.model_path,
                    model_sha256=m.sha256,
                    input_shape=m.input_shape,
                    output_shape=m.output_shape,
                    parameter_count=m.parameter_count,
                    status=m.status,
                    last_loaded_at=m.last_loaded_at,
                )
            logger.info("Synchronized model artifacts to database table.")
        except Exception as e:
            logger.warning(f"Could not synchronize model artifacts to DB: {e}")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error during model registry startup: {e}", exc_info=True)

    logger.info("NeuroVision AI backend startup complete and ready to serve requests.")

    yield

    logger.info("Gracefully shutting down NeuroVision AI backend service...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "PRISM: Precision Radiology Imaging for Solid Masses: "
        "A Hybrid EfficientNet-MobileNet Attention Classifier for Brain Tumors."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Custom Exception Handlers
register_exception_handlers(app)

# Include API Routers
app.include_router(health.router)
app.include_router(models.router)
app.include_router(predictions.router)
app.include_router(history.router)
app.include_router(analytics.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
