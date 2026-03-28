from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "ResumeShield"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_per_hour: int = 5
    rate_limit_per_day: int = 15

    # File upload
    max_file_size_mb: int = 10
    allowed_file_types: list[str] = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

    # Input limits
    min_resume_length: int = 100
    max_resume_length: int = 15000
    min_jd_length: int = 50
    max_jd_length: int = 8000

    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://resumeshield.dev",
        "https://www.resumeshield.dev",
        "https://resumeshield.vercel.app",
        "https://resumeshield-gauthambinoy.vercel.app",
        "https://resumeshield-git-main-gauthambinoy.vercel.app",
    ]

    # HuggingFace API (for ML paraphrasing in humanization — optional, works without it)
    huggingface_api_key: str = ""

    # Sentry
    sentry_dsn: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
