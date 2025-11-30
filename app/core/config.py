from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application configuration settings.

    This class defines the schema for environment variables required by the 
    application. It automatically validates types and loads values from 
    the environment or a local '.env' file.

    Attributes:
        DATABASE_URL (str): The full database connection string (DSN).
        JWT_SECRET_KEY (str): The secret key used for signing and verifying 
            JWT tokens for authentication.
    """
    DATABASE_URL: str
    JWT_SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8'
    )

settings = Settings()