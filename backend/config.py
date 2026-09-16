"""
Lawpedia Backend Configuration Settings
"""

import os
from pydantic import BaseModel, Field, model_validator


def _get_secret_key() -> str:
    secret_env = os.getenv("LAWPEDIA_SECRET_KEY")
    if not secret_env:
        if os.getenv("DEBUG", "True").lower() not in ("true", "1", "t") or os.getenv("ENV", "development").lower() == "production":
            raise RuntimeError(
                "CRITICAL SECURITY CONFIGURATION ERROR: LAWPEDIA_SECRET_KEY environment variable is not set. "
                "Set LAWPEDIA_SECRET_KEY in environment before starting production server."
            )
        return "lawpedia_dev_secret_key_change_in_production"
    return secret_env


class Settings(BaseModel):
    APP_NAME: str = "Lawpedia Legal Intelligence Platform"
    VERSION: str = "2.0.0"
    ENV: str = Field(default_factory=lambda: os.getenv("ENV", "development").lower())
    DEBUG: bool = Field(default_factory=lambda: os.getenv("DEBUG", "True").lower() in ("true", "1", "t"))
    
    # Security & Storage
    SECRET_KEY: str = Field(default_factory=_get_secret_key)
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_MIME_TYPES: list[str] = ["application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    
    # Demo Mode Configuration (Controlled via Environment Variables)
    # IMPORTANT: Default is FALSE — demo mode must be explicitly opted-in per environment.
    # Never rely on default in production. Use render-demo.yaml for public demo deployments.
    LAWPEDIA_DEMO_MODE: bool = os.getenv("LAWPEDIA_DEMO_MODE", "false").lower() in ("true", "1", "t")
    LAWPEDIA_DEMO_TOKEN: str = os.getenv("LAWPEDIA_DEMO_TOKEN", "")
    DEFAULT_TENANT_ID: str = os.getenv("DEFAULT_TENANT_ID", "tenant_lawpedia_demo")

    # Retrieval & RAG
    VECTOR_DIMENSION: int = 384
    TOP_K_RETRIEVAL: int = 5
    RRF_K: int = 60
    MIN_CONFIDENCE_THRESHOLD: float = 0.30
    STRICT_ABSTENTION: bool = True

    # Parameterized Model Configurations
    OPENAI_MODEL_NAME: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    ANTHROPIC_MODEL_NAME: str = os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-5-haiku-20241022")
    MAX_LLM_REQUESTS_PER_MINUTE_PER_TENANT: int = int(os.getenv("MAX_LLM_REQUESTS_PER_MINUTE_PER_TENANT", "60"))

    @model_validator(mode="after")
    def validate_production_guards(self):
        if self.ENV == "production" and self.DEBUG:
            raise RuntimeError("CRITICAL SECURITY ERROR: Refusing to start production server with DEBUG=True.")
        return self


settings = Settings()
