import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./exportguard.db"
    JWT_SECRET: str = "exportguard-super-secret-jwt-key-2026-development"
    JWT_EXPIRE_MINUTES: int = 480
    TEAM_USERNAME: str = "team"
    TEAM_PASSWORD: str = "secret"
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    WATSONX_API_KEY: Optional[str] = None
    WATSONX_PROJECT_ID: Optional[str] = None
    WATSONX_URL: Optional[str] = None
    UPLOAD_DIR: str = "./uploads"
    STORAGE_BACKEND: str = "local"
    SUPABASE_URL: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    SUPABASE_STORAGE_BUCKET: str = "documents"
    OCR_LANG: str = "eng"
    NUMERIC_TOLERANCE: float = 0.01
    TASK_BACKEND: str = "local"
    CELERY_BROKER_URL: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
