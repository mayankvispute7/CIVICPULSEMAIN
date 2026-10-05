"""Core configuration and settings for Civic Pulse backend."""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    PROJECT_NAME: str = "Civic Pulse API"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/civicpulse"
    USE_SQLITE: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    LOG_LEVEL: str = "info"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # File uploads
    MAX_CSV_SIZE_MB: int = 50
    MAX_CSV_ROWS: int = 10000
    UPLOAD_DIR: str = "./uploads"

    # LLM Provider
    LLM_PROVIDER: Optional[str] = None
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: Optional[str] = None

    # Earth Observation
    EO_PROVIDER: Optional[str] = None
    EO_API_KEY: Optional[str] = None

    # Weather
    WEATHER_PROVIDER: Optional[str] = None
    WEATHER_API_KEY: Optional[str] = None

    # Geocoding
    GEOCODING_PROVIDER: Optional[str] = None
    GEOCODING_API_KEY: Optional[str] = None

    # Clustering
    CLUSTERING_MIN_SAMPLES: int = 2
    CLUSTERING_SPATIAL_EPS_METERS: float = 500.0
    CLUSTERING_TEMPORAL_DAYS: int = 90

    # Demo
    DEMO_SEED: int = 42

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def db_url(self) -> str:
        if self.USE_SQLITE:
            db_path = Path(__file__).parent.parent / "civicpulse.db"
            return f"sqlite:///{db_path}"
        return self.DATABASE_URL

    @property
    def max_csv_bytes(self) -> int:
        return self.MAX_CSV_SIZE_MB * 1024 * 1024

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
