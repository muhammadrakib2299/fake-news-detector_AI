"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "VerifyAI"
    app_env: str = "development"
    debug: bool = True

    # Database (SQLite for dev, PostgreSQL for production)
    database_url: str = "sqlite:///./verifyai.db"

    # CORS
    cors_origins: str = "http://localhost:3000"

    # API Keys
    google_fact_check_api_key: str = ""
    anthropic_api_key: str = ""

    # Model
    model_path: str = "ml/models"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
