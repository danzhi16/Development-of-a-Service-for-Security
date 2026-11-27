from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings, get_settings


# URL.create escapes the password, unlike string formatting.
def database_url(settings: Settings) -> URL:
    return URL.create(
        "postgresql+asyncpg",
        username=settings.postgres_user,
        password=settings.postgres_password.get_secret_value(),
        host=settings.postgres_host,
        port=settings.postgres_port,
        database=settings.postgres_db,
    )


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(database_url(get_settings()), pool_pre_ping=True)
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with get_session_factory()() as session:
        yield session
