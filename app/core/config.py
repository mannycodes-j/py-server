

from typing import List, Optional
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
   

    # ============== APPLICATION ==============
    APP_NAME: str = "Task Control Center"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # ============== SERVER ==============
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # ============== CORS ==============
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # ============== LOGGING ==============
    LOG_LEVEL: str = "INFO"

    # ============== API DOCUMENTATION ==============
    DOCS_ENABLED: bool = True
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def docs_url(self) -> Optional[str]:
        return self.DOCS_URL if self.DOCS_ENABLED else None

    @property
    def redoc_url(self) -> Optional[str]:
        return self.REDOC_URL if self.DOCS_ENABLED else None

    @property
    def openapi_url(self) -> Optional[str]:
        return self.OPENAPI_URL if self.DOCS_ENABLED else None

    class Config:
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
