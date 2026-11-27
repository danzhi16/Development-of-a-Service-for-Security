import asyncio
import json
import logging
from collections.abc import Awaitable, Callable

from aio_pika.abc import AbstractIncomingMessage

from app.config import Settings
from app.queue import connect

logger = logging.getLogger(__name__)

RETRY_DELAY_SECONDS = 5


# Ack only after the handler returns, so a killed worker gets its job redelivered.
async def process(message: AbstractIncomingMessage, handle: Callable[[int], Awaitable[None]]) -> None:
    try:
        generation_id = int(json.loads(message.body)["generation_id"])
    except (ValueError, KeyError, TypeError):
        logger.exception("dropping malformed message: %r", message.body[:200])
        await message.reject(requeue=False)
        return
    try:
        await handle(generation_id)
    except Exception:
        # Infrastructure failure (database, broker): expected LLM and analyser errors are stored.
        logger.exception("job %s failed, requeueing", generation_id)
        await asyncio.sleep(RETRY_DELAY_SECONDS)
        await message.nack(requeue=True)
        return
    await message.ack()


async def consume(settings: Settings, queue_name: str, handle: Callable[[int], Awaitable[None]]) -> None:
    async with await connect(settings) as connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        queue = await channel.declare_queue(queue_name, durable=True)
        logger.info("consuming queue %s", queue_name)
        async with queue.iterator() as messages:
            async for message in messages:
                await process(message, handle)
