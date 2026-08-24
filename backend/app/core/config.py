from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Student Success Platform"
    app_env: str = "development"
    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:4173,http://127.0.0.1:4173,http://localhost:3000"
    )

    database_url: str = (
        "postgresql+psycopg://sih_user:sih_password"
        "@localhost:5432/student_success"
    )

    dataset_path: Path = Path(
        "data/raw/SIH_Indian_Student_Dropout_Synthetic_Dataset_v1.xlsx"
    )

    model_dir: Path = Path("ml/artifacts")

    model_risk_low_threshold: float = 0.40
    model_risk_critical_threshold: float = 0.70

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    google_api_key: str = ""

    gemini_model: str = (
    "gemini-3.6-flash"
    )
    jwt_secret_key: str = ""

    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 120

    whatsapp_graph_version: str | None = None

    whatsapp_phone_number_id: str | None = None

    whatsapp_access_token: str | None = None

    whatsapp_template_name: str | None = None

    whatsapp_template_language: str = "en_US"


@lru_cache
def get_settings() -> Settings:
    return Settings()