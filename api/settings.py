"""Configuration settings for Bet-That API"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_path: str = "storage/odds.db"
    api_secret_key: str = "dev-secret-key-change-in-production"
    environment: str = "development"
    rate_limit_requests: int = 60
    rate_limit_window: int = 60
    compliance_disclaimer: str = (
        "This platform provides sports analytics for entertainment purposes only. "
        "Not available to residents where prohibited. Users must be 21+. Gamble responsibly."
    )
    log_level: str = "INFO"
    enable_deep_health: bool = True
    enable_request_logging: bool = True
    
    class Config:
        env_file = ".env.api"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()

def get_database_url() -> str:
    db_path = Path(settings.db_path)
    if not db_path.is_absolute():
        project_root = Path(__file__).parent.parent
        db_path = project_root / db_path
    return f"sqlite:///{db_path}"

def validate_database_path() -> bool:
    db_path = Path(settings.db_path)
    if not db_path.is_absolute():
        project_root = Path(__file__).parent.parent
        db_path = project_root / db_path
    return db_path.exists()
