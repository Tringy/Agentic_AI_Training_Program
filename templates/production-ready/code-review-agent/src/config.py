"""
Configuration Management with Pydantic Settings

Manages environment variables and configuration for the code review agent.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    github_token: str = Field(..., description="GitHub personal access token")
    anthropic_api_key: str = Field(..., description="Anthropic API key")
    github_webhook_secret: str = Field(..., description="GitHub webhook secret for signature verification")

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")

    # Review Settings
    max_files_per_pr: int = Field(default=20, description="Maximum files to review per PR")
    review_timeout: int = Field(default=300, description="Review timeout in seconds")
    auto_comment: bool = Field(default=True, description="Automatically post review comments")
    severity_threshold: str = Field(default="medium", description="Minimum severity to report (low, medium, high)")

    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(default=60, description="Rate limit per repository")
    rate_limit_tokens_per_minute: int = Field(default=100000, description="Token rate limit")

    # LLM Configuration
    model_name: str = Field(default="claude-3-5-sonnet-20241022", description="Claude model to use")
    max_tokens: int = Field(default=4096, description="Maximum tokens per request")
    temperature: float = Field(default=0.3, description="LLM temperature")

    # Cost Tracking
    enable_cost_tracking: bool = Field(default=True, description="Track API costs")
    max_cost_per_review: float = Field(default=0.50, description="Maximum cost per review in USD")

    # Caching
    enable_caching: bool = Field(default=True, description="Enable response caching")
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL in seconds")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings():
    """Reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings
