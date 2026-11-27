import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import get_settings
from app.db import database_url
from app.models import Base

if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)


def run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()


# Only online mode is supported: the URL comes from the same settings as the app.
async def main() -> None:
    engine = create_async_engine(database_url(get_settings()))
    async with engine.connect() as connection:
        await connection.run_sync(run_migrations)
    await engine.dispose()


asyncio.run(main())
