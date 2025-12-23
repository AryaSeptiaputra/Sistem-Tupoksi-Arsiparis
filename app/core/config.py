from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Konfigurasi aplikasi yang disesuaikan untuk mode Production.
    """
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    
    # Tambahkan variabel baru yang ada di .env Anda di sini:
    SECRET_KEY: Optional[str] = None
    FLASK_ENV: str = "production"
    FLASK_DEBUG: int = 0
    LOG_FILE_PATH: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra="ignore" 
    )

settings = Settings()