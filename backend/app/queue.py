import json
from collections.abc import Awaitable, Callable

import aio_pika
from aio_pika.abc import AbstractRobustConnection

from app.config import Settings

GENERATION_QUEUE = "generation"
ANALYSIS_QUEUE = "analysis"

Publish = Callable[[str, list[int]], Awaitable[None]]


async def connect(settings: Settings) -> AbstractRobustConnection:
    return await aio_pika.connect_robust(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        login=settings.rabbitmq_default_user,
        password=settings.rabbitmq_default_pass.get_secret_value(),
    )


# Durable queue, persistent messages and publisher confirms: jobs survive a broker restart.
async def publish_jobs(settings: Settings, queue_name: str, generation_ids: list[int]) -> None:
    async with await connect(settings) as connection:
        channel = await connection.channel(publisher_confirms=True)
        await channel.declare_queue(queue_name, durable=True)
        for generation_id in generation_ids:
            message = aio_pika.Message(
                json.dumps({"generation_id": generation_id}).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )
            await channel.default_exchange.publish(message, routing_key=queue_name)
