from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.

    This class defines the schema for environment variables required by the application,
    such as database connection strings and security keys. It automatically loads
    values from a '.env' file.

    Attributes:
        DATABASE_URL (str): The connection string for the database.
        JWT_SECRET_KEY (str): The secret key used for signing JWT tokens.
    """
    DATABASE_URL: str
    JWT_SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8'
    )

settings = Settings()