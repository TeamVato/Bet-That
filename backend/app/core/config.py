from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, BaseSettings, Field


class Settings(BaseSettings):
    odds_api_keys: List[str] = Field(default_factory=list, env="ODDS_API_KEYS")
    odds_api_key_1: Optional[str] = Field(default=None, env="ODDS_API_KEY_1")
    odds_api_key_2: Optional[str] = Field(default=None, env="ODDS_API_KEY_2")
    odds_api_key_3: Optional[str] = Field(default=None, env="ODDS_API_KEY_3")
    odds_api_key_4: Optional[str] = Field(default=None, env="ODDS_API_KEY_4")
    odds_api_key_5: Optional[str] = Field(default=None, env="ODDS_API_KEY_5")
    odds_api_key_6: Optional[str] = Field(default=None, env="ODDS_API_KEY_6")
    odds_api_base_url: AnyHttpUrl = Field(
        default="https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"
    )
    cache_ttl_seconds: int = Field(default=1800, env="CACHE_TTL_SECONDS")
    daily_request_limit: int = Field(default=20, env="DAILY_REQUEST_LIMIT")
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_cache_prefix: str = Field(default="bet_that_odds", env="REDIS_CACHE_PREFIX")
    environment: str = Field(default="development", env="ENVIRONMENT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def all_odds_keys(self) -> List[str]:
        keys = [
            key
            for key in (
                *(self.odds_api_keys or []),
                self.odds_api_key_1,
                self.odds_api_key_2,
                self.odds_api_key_3,
                self.odds_api_key_4,
                self.odds_api_key_5,
                self.odds_api_key_6,
            )
            if key
        ]
        seen: set[str] = set()
        ordered: list[str] = []
        for key in keys:
            if key not in seen:
                seen.add(key)
                ordered.append(key)
        return ordered


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def get_cache_prefix(*suffixes: str) -> str:
    settings = get_settings()
    parts = [settings.redis_cache_prefix, *suffixes]
    return ":".join(parts)


# Cached settings instance used across the app
settings = get_settings()
