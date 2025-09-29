"""Configuration settings for Bet-That API"""

import os
from pathlib import Path
from typing import Optional

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

    # JWT Authentication Settings
    jwt_secret_key: str = "dev-jwt-secret-key-change-in-production-use-256-bit-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 30
    jwt_issuer: str = "bet-that-api"
    jwt_audience: str = "bet-that-users"

    # RSA Key Pair for RS256 (optional, for production)
    jwt_private_key: Optional[str] = None
    jwt_public_key: Optional[str] = None

    # Password Security Settings
    password_bcrypt_rounds: int = 12
    password_min_length: int = 8
    password_max_length: int = 128

    # Authentication Rate Limiting
    auth_max_attempts_per_ip: int = 10
    auth_max_attempts_per_user: int = 5
    auth_rate_limit_window_minutes: int = 15
    auth_block_duration_minutes: int = 60

    # Security Features
    enable_csrf_protection: bool = True
    csrf_token_expire_hours: int = 24
    enable_email_verification: bool = True
    email_verification_expire_hours: int = 24

    # Session Management
    max_concurrent_sessions: int = 5
    session_timeout_minutes: int = 1440  # 24 hours

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
