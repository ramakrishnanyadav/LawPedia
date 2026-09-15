"""
Lawpedia Backend Configuration Settings
"""

import os
from pydantic import BaseModel, Field


def _get_secret_key() -> str:
    secret_env = os.getenv("LAWPEDIA_SECRET_KEY")
    if not secret_env:
        # In non-DEBUG mode, fail startup with a clear error if LAWPEDIA_SECRET_KEY is omitted
        if not os.getenv("DEBUG", "True").lower() in ("true", "1", "t"):
            raise RuntimeError(
                "CRITICAL SECURITY CONFIGURATION ERROR: LAWPEDIA_SECRET_KEY environment variable is not set. "
                "Set LAWPEDIA_SECRET_KEY in environment before starting production server."
            )
        return "lawpedia_dev_secret_key_change_in_production"
    return secret_env


class Settings(BaseModel):
    APP_NAME: str = "Lawpedia Legal Intelligence Platform"
    VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    # Security & Storage
    SECRET_KEY: str = _get_secret_key()
    MAX_UPLOAD_SIZE_MB: int = 25

    ALLOWED_MIME_TYPES: list[str] = ["application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    
    # Retrieval & RAG
    VECTOR_DIMENSION: int = 384
    TOP_K_RETRIEVAL: int = 5
    RRF_K: int = 60
    
    # Evidence & Verification (Recalibrated for Real Dense Semantic Vectors)
    MIN_CONFIDENCE_THRESHOLD: float = 0.30
    STRICT_ABSTENTION: bool = True

    
    # Default Tenant
    DEFAULT_TENANT_ID: str = "tenant_lawpedia_demo"


settings = Settings()
