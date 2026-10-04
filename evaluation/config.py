from pydantic_settings import BaseSettings, SettingsConfigDict


class EvalSettings(BaseSettings):
    """Setting alat evaluasi yang dibaca dari `.env`, terpisah dari setting aplikasi."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    eval_old_db_url: str = ""
    eval_storage_root: str = "storage"
    eval_output_dir: str = "outputs/evaluation"


eval_settings = EvalSettings()
