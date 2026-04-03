from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "SaaS Bot System"
    APP_VERSION: str = "0.1.0"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/saas_bot"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    BOT_MAX_RETRIES: int = 3
    BOT_TIMEOUT_MS: int = 30000

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    class Config:
        env_file = ".env"


settings = Settings()
