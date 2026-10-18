from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Setting aplikasi yang dibaca dari `.env`."""

    DATABASE_URL: str
    JWT_SECRET_KEY: str
    SECRET_KEY: str
    FLASK_ENV: str = "production"
    FLASK_DEBUG: int = 0
    LOG_FILE_PATH: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra="ignore"
    )


settings = Settings()
