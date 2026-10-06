from pydantic_settings import BaseSettings, SettingsConfigDict


class EvalSettings(BaseSettings):
    """Setting alat evaluasi yang dibaca dari `.env`, terpisah dari setting aplikasi."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    eval_old_db_url: str = ""
    eval_storage_root: str = "storage"
    eval_output_dir: str = "outputs/evaluation"
    eval_seed_db_url: str = ""
    eval_seed_storage_root: str = ""
    # URL database aplikasi; hanya dibaca untuk memastikan seed tidak menulis ke sana (003a DS1)
    database_url: str = ""


eval_settings = EvalSettings()
