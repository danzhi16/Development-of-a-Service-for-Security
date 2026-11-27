import asyncio

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import Settings
from app.models import Base


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
