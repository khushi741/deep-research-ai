import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # App Info
    APP_NAME: str = "Deep Research AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "sqlite:///./research.db"

    # LLM Settings
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Search APIs
    TAVILY_API_KEY: Optional[str] = None
    FIRECRAWL_API_KEY: Optional[str] = None

    # Pipeline Limits
    MAX_SEARCHES_PER_RUN: int = 10
    MAX_PAGES_PROCESSED: int = 15
    MAX_CONTENT_LENGTH_PER_PAGE: int = 12000
    HTTP_TIMEOUT_SECONDS: int = 15

    # Rate Limit & Safety Settings
    MAX_QUERY_LENGTH: int = 500
    ALLOWED_SCHEMES: set[str] = {"http", "https"}


settings = Settings()
