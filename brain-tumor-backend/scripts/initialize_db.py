"""Database initialization script.

Executes schema creation and initial artifact synchronization.
Usage:
    python scripts/initialize_db.py
"""

import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

from app.config import settings
from app.db.database import init_db, SessionLocal
from app.services.model_registry import registry
from app.db.repositories import ModelArtifactRepository
from app.logging_config import setup_logging

logger = setup_logging()


def main():
    print("=" * 70)
    print("PRISM: Precision Radiology Imaging for Solid Masses")
    print("A Hybrid EfficientNet-MobileNet Attention Classifier for Brain Tumors")
    print("SQLite Database Initialization")
    print("=" * 70)

    db_url = settings.resolved_database_url
    print(f"Database URL: {db_url}")

    print("\n[1/2] Creating tables from SQLAlchemy Base metadata...")
    init_db()
    print("[OK] Tables successfully created.")

    print("\n[2/2] Scanning model registry and populating ModelArtifact records...")
    registry.initialize_registry()
    models = registry.get_all_models()

    db = SessionLocal()
    try:
        for m in models:
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
            print(f"  - Registered {m.model_id} ({m.display_name}): Status={m.status}")
    finally:
        db.close()

    print("\n[OK] Database initialization completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
