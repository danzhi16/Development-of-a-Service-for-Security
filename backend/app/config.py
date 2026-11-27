from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: SecretStr
    postgres_db: str

    rabbitmq_host: str = "queue"
    rabbitmq_port: int = 5672
    rabbitmq_default_user: str
    rabbitmq_default_pass: SecretStr

    health_timeout_seconds: float = 3.0


# Cached and lazy so importing the app does not require a configured environment.
@lru_cache
def get_settings() -> Settings:
    return Settings()
