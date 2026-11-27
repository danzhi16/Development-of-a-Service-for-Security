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

    # Any OpenAI-compatible endpoint; the default is Ollama running on the Docker host.
    llm_base_url: str = "http://host.docker.internal:11434/v1"
    llm_api_key: SecretStr | None = None
    llm_timeout_seconds: float = 180


# Cached and lazy so importing the app does not require a configured environment.
@lru_cache
def get_settings() -> Settings:
    return Settings()
