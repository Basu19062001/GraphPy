from functools import lru_cache

from pydantic_settings import BaseSettings
from starlette.config import Config

config = Config("app/.env")


class Settings(BaseSettings):
    VERSION: str = config("VERSION", default="1.0.0")


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    return settings


settings = get_settings()
