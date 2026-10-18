from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Setting aplikasi yang dibaca dari `.env`."""

    DATABASE_URL: str
    JWT_SECRET_KEY: str
    SECRET_KEY: str
    FLASK_ENV: str = "production"
    FLASK_DEBUG: int = 0
    # Optional, bukan `str | None`: pydantic mengevaluasi annotation saat runtime,
    # dan Python 3.8 (target Windows 7) belum mendukung operator `|` pada tipe.
    LOG_FILE_PATH: Optional[str] = None
    LOG_FORMAT: str = "text"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra="ignore"
    )


settings = Settings()
