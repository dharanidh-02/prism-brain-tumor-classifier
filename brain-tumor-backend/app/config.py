"""Application configuration module using Pydantic Settings."""

from pathlib import Path
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Central configuration for PRISM backend."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core Application Settings
    PROJECT_NAME: str = "PRISM"
    PROJECT_TITLE: str = "Precision Radiology Imaging for Solid Masses: A Hybrid EfficientNet-MobileNet Attention Classifier for Brain Tumors"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # CORS Settings
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Database Settings
    DATABASE_URL: str = "sqlite:///data/PRISM.db"

    # Storage Settings
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "data/uploads"

    # Model File Paths (Windows defaults pointing to results folder)
    MODEL_A_PATH: str = Field(
        default=str(
            BASE_DIR.parent
            / "results"
            / "final_hybrid_efficientnet_mobilenet_attention.keras"
        )
    )
    MODEL_B_PATH: str = Field(
        default=str(
            BASE_DIR.parent
            / "results"
            / "FINAL_Hybrid_EfficientNetB0_MobileNetV3_Attention.keras"
        )
    )
    MODEL_C_PATH: str = Field(
        default=str(
            BASE_DIR.parent
            / "results"
            / "phase2_checkpoints"
            / "best_hybrid_finetuned.keras"
        )
    )

    # Configurable Display Names
    MODEL_A_DISPLAY_NAME: str = "Hybrid EfficientNetB0 + MobileNetV3 (Attention)"
    MODEL_B_DISPLAY_NAME: str = "Hybrid EfficientNetB0 + MobileNetV3 (Final Attention)"
    MODEL_C_DISPLAY_NAME: str = "Hybrid Fine-tuned (Phase 2 Checkpoint)"

    # Class Mapping (alphabetical default from standard MRI datasets)
    CLASS_NAMES: Union[str, List[str]] = ["glioma", "meningioma", "notumor", "pituitary"]

    # Model Loading Strategy ("eager" or "lazy")
    MODEL_LOADING_STRATEGY: str = "eager"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    @field_validator("CLASS_NAMES", mode="before")
    @classmethod
    def assemble_class_names(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def resolved_database_url(self) -> str:
        """Resolve SQLite path safely relative to backend directory."""
        if self.DATABASE_URL.startswith("sqlite:///"):
            raw_path = self.DATABASE_URL.replace("sqlite:///", "")
            db_path = Path(raw_path)
            if not db_path.is_absolute():
                db_path = BASE_DIR / db_path
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{db_path.resolve()}"
        return self.DATABASE_URL

    @property
    def resolved_upload_dir(self) -> Path:
        """Resolve upload directory path and ensure existence."""
        upload_path = Path(self.UPLOAD_DIR)
        if not upload_path.is_absolute():
            upload_path = BASE_DIR / upload_path
        upload_path.mkdir(parents=True, exist_ok=True)
        return upload_path.resolve()

    def get_model_definitions(self) -> dict:
        """Return configured model definitions."""
        return {
            "hybrid_v1": {
                "display_name": self.MODEL_A_DISPLAY_NAME,
                "path": str(Path(self.MODEL_A_PATH).resolve()),
                "description": (
                    "Hybrid architecture combining EfficientNetB0 and MobileNetV3Large "
                    "backbones with dual-branch feature projection, concatenation, "
                    "and self-attention gating."
                ),
                "phase": "Phase 1 / Trained Artifact",
            },
            "hybrid_v1_final": {
                "display_name": self.MODEL_B_DISPLAY_NAME,
                "path": str(Path(self.MODEL_B_PATH).resolve()),
                "description": (
                    "Final saved variant of Hybrid EfficientNetB0 + MobileNetV3Large "
                    "with cross-feature attention gating."
                ),
                "phase": "Phase 1 Final Artifact",
            },
            "hybrid_v2_finetuned": {
                "display_name": self.MODEL_C_DISPLAY_NAME,
                "path": str(Path(self.MODEL_C_PATH).resolve()),
                "description": (
                    "Fine-tuned hybrid model checkpoint from training Phase 2 with "
                    "unfrozen backbone layers and tuned learning schedule."
                ),
                "phase": "Phase 2 Fine-tuned Checkpoint",
            },
        }


settings = Settings()
