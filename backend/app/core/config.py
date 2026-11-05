"""
Application Configuration Module using Pydantic Settings.
Loads environment variables from .env with fallback defaults.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "The Churn Poacher"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    DEMO_MODE: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./churn_poacher.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # OpenAI / LLM
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Social & Status integrations
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USER_AGENT: str = "ChurnPoacherBot/1.0.0"

    HACKER_NEWS_API_BASE: str = "https://hn.algolia.com/api/v1"
    DATADOG_STATUS_PAGE_URL: str = "https://status.datadoghq.com/api/v2/summary.json"
    TWITTER_BEARER_TOKEN: Optional[str] = None

    # Enrichment integrations
    CLEARBIT_API_KEY: Optional[str] = None
    APOLLO_API_KEY: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
