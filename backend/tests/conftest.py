import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import Settings
from app.db import get_session
from app.main import app
from app.models import Base
from app.routers.runs import get_publisher
from app.tasksets import seed_task_set


@pytest.fixture
def session_factory(tmp_path):
    # NullPool: every asyncio.run() has its own loop, so connections must not be reused.
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'test.db'}", poolclass=NullPool)
    event.listen(engine.sync_engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))

    async def create_schema():
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    asyncio.run(create_schema())
    return async_sessionmaker(engine, expire_on_commit=False)


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


@pytest.fixture
def seeded(session_factory):
    async def seed():
        async with session_factory() as session:
            await seed_task_set(session, "builtin-python-15")

    asyncio.run(seed())


@pytest.fixture
def published() -> list[tuple[str, list[int]]]:
    return []


@pytest.fixture
def api(session_factory, published):
    async def override_session():
        async with session_factory() as session:
            yield session

    async def publish(queue_name, generation_ids):
        published.append((queue_name, generation_ids))

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_publisher] = lambda: publish
    yield TestClient(app)
    app.dependency_overrides.clear()
