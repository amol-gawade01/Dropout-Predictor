from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Student Success Platform"
    app_env: str = "development"

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


@lru_cache
def get_settings() -> Settings:
    return Settings()