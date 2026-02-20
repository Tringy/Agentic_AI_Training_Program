"""Application settings and configuration."""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Environment
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # API Keys
    anthropic_api_key: str
    openai_api_key: Optional[str] = None

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Rate Limiting
    rate_limit_rpm: int = 60
    rate_limit_tpm: int = 100000
    rate_limit_burst_multiplier: float = 1.5

    # Caching
    cache_ttl_seconds: int = 3600
    semantic_cache_threshold: float = 0.95
    enable_semantic_cache: bool = True

    # Responsible AI
    enable_bias_detection: bool = True
    enable_audit_trail: bool = True
    human_approval_threshold: float = 0.7
    auto_approve_threshold: float = 0.9
    auto_reject_threshold: float = 0.3

    # Database
    database_url: Optional[str] = None

    # Monitoring
    sentry_dsn: Optional[str] = None
    enable_metrics: bool = True

    # Security
    cors_origins: str = "*"
    api_key_header: str = "X-API-Key"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def get_settings() -> Settings:
    """Get settings instance."""
    return Settings()
