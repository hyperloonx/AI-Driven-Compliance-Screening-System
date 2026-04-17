"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI-Driven Compliance Screening System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./compliance.db",
        description="Database connection URL",
    )

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", description="Redis URL")

    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")

    # Agent mode: "AI_MODE" or "RULE_BASED"
    AGENT_MODE: str = Field(
        default="RULE_BASED",
        description="Agent operating mode: AI_MODE or RULE_BASED",
    )

    # Security
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", description="JWT secret key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000", "*"]

    # Reports directory
    REPORTS_DIR: str = Field(default="reports", description="Directory to store PDF reports")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()

# Ensure reports directory exists
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
