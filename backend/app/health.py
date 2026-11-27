import asyncio
import logging
from collections.abc import Awaitable, Callable

import aio_pika
import asyncpg

from app.config import Settings

logger = logging.getLogger(__name__)


async def check_database(settings: Settings) -> None:
    connection = await asyncpg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        user=settings.postgres_user,
        password=settings.postgres_password.get_secret_value(),
        database=settings.postgres_db,
    )
    try:
        await connection.execute("SELECT 1")
    finally:
        await connection.close()


async def check_queue(settings: Settings) -> None:
    connection = await aio_pika.connect(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        login=settings.rabbitmq_default_user,
        password=settings.rabbitmq_default_pass.get_secret_value(),
    )
    await connection.close()


CHECKS: dict[str, Callable[[Settings], Awaitable[None]]] = {
    "database": check_database,
    "queue": check_queue,
}


# Failures are logged, not returned: driver messages can include hosts and user names.
async def run_checks(settings: Settings) -> dict[str, str]:
    async def run(name: str) -> str:
        try:
            await asyncio.wait_for(CHECKS[name](settings), settings.health_timeout_seconds)
        except Exception:
            logger.exception("health check failed: %s", name)
            return "error"
        return "ok"

    results = await asyncio.gather(*(run(name) for name in CHECKS))
    return dict(zip(CHECKS, results))
