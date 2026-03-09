from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional


def _normalize_redis_url(url: str) -> str:
    """Ensure Redis URL has a valid scheme (redis://, rediss://, unix://)."""
    if not url or not url.strip():
        return url
    u = url.strip()
    if u.startswith(("redis://", "rediss://", "unix://")):
        return u
    # Redis Cloud often gives default:password@host:port — assume TLS
    if "@" in u and "://" not in u:
        return "rediss://" + u
    return "redis://" + u


class Settings(BaseSettings):
    # General
    app_name: str = "LeakSight"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # MongoDB
    mongo_uri: str = "mongodb://localhost:27017/leaksight"
    mongo_db_name: str = "leaksight"

    # Redis (scheme auto-added if missing, e.g. rediss://default:pass@host:port)
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_db: int = 1
    redis_cache_ttl: int = 300

    @field_validator("redis_url", mode="before")
    @classmethod
    def normalize_redis_url(cls, v: str) -> str:
        if v is None or (isinstance(v, str) and not v.strip()):
            return "redis://localhost:6379/0"
        return _normalize_redis_url(str(v).strip())

    # HuggingFace
    hf_token: str = ""
    hf_classifier_model: str = "distilbert-base-uncased"
    hf_summarizer_model: str = "facebook/bart-large-cnn"

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"

    # Scraper (Forums + tech sites; no API keys)
    scrape_interval_minutes: int = 30
    scrape_websites_enabled: bool = True
    proxy_list_path: str = ""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    # Comma-separated list of origins, e.g. "http://localhost:3000,https://your-app.vercel.app"
    api_cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
