from functools import lru_cache
from typing import List, Optional, Dict, Any

from pydantic import field_validator
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

    MONGO_USERNAME: str = config("MONGO_USERNAME", cast=str)
    MONGO_PASSWORD: str = config("MONGO_PASSWORD", cast=str)
    MONGO_HOST: str = config("MONGO_HOST", cast=str, default="localhost")
    MONGO_PORT: int = config("MONGO_PORT", cast=int, default=27017)
    MONGO_DB: str = config("MONGO_DB", cast=str, default="restapi_vs_graphql")
    MONGO_DSN: Optional[str] = config("MONGO_DSN", cast=str, default=None)

    @field_validator("MONGO_DSN", mode="before")
    @classmethod
    def assemble_mongo_dsn(cls, v: Optional[str], info: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v

        values = info.data

        if values.get("MONGO_USERNAME") and values.get("MONGO_PASSWORD"):
            return f"mongodb://{values.get('MONGO_USERNAME')}:{values.get('MONGO_PASSWORD')}@{values.get('MONGO_HOST')}:{values.get('MONGO_PORT')}/{values.get('MONGO_DB')}"

        return f"mongodb://{values.get('MONGO_HOST')}:{values.get('MONGO_PORT')}/{values.get('MONGO_DB')}"


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    return settings


settings = get_settings()
