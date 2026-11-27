import pytest

from app.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        postgres_user="test",
        postgres_password="test",
        postgres_db="test",
        rabbitmq_default_user="test",
        rabbitmq_default_pass="test",
        health_timeout_seconds=0.2,
    )
