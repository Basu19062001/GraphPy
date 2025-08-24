from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings
from starlette.config import Config

config = Config("app/.env")


class Settings(BaseSettings):
    PROJECT_NAME: str = "RestAPI vs GraphQL"
    PROJECT_DESCRIPTION: str = "A comparison between REST API and GraphQL implementations."
    VERSION: str = config("VERSION", default="1.0.0")

    DEBUG: bool = config("DEBUG", cast=bool, default=False)

    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:5173",
        "http://localhost:8000",
    ]

    # Security Settings
    JWT_SECRET_KEY: str = config("JWT_SECRET_KEY", cast=str)

    API_V1_STR: str = config("API_V1_STR", cast=str, default="/api/v1")

    # API Documentation Auth
    DOC_ROOT_USERNAME: str = config("DOC_ROOT_USERNAME", cast=str)
    DOC_ROOT_PASSWORD: str = config("DOC_ROOT_PASSWORD", cast=str)


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    return settings


settings = get_settings()
