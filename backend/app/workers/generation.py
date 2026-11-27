import asyncio
import logging
from datetime import UTC, datetime
from functools import partial

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import joinedload

from app.config import get_settings
from app.db import get_session_factory
from app.lifecycle import finalize_run
from app.llm import LLMClient, LLMError
from app.models import Generation, GenerationStatus, Run, RunStatus
from app.prompts import extract_code
from app.queue import ANALYSIS_QUEUE, GENERATION_QUEUE, Publish, publish_jobs
from app.workers.runner import consume

logger = logging.getLogger(__name__)


async def handle_generation(
    generation_id: int,
    session_factory: async_sessionmaker[AsyncSession],
    llm: LLMClient,
    publish: Publish,
) -> None:
    async with session_factory() as session:
        query = select(Generation).where(Generation.id == generation_id).options(joinedload(Generation.run))
        generation = await session.scalar(query)
        if generation is None:
            logger.warning("generation %s does not exist", generation_id)
            return
        run = generation.run
        status = generation.status
        if status == GenerationStatus.PENDING and run.status == RunStatus.FAILED:
            generation.status = status = GenerationStatus.FAILED
            generation.error = "run aborted"
        await session.execute(
            update(Run)
            .where(Run.id == run.id, Run.status == RunStatus.QUEUED)
            .values(status=RunStatus.RUNNING)
        )
        await session.commit()

    # Redelivery: the answer is stored but the analysis job may never have been published.
    if status == GenerationStatus.GENERATED:
        await publish(ANALYSIS_QUEUE, [generation_id])
        return
    if status != GenerationStatus.PENDING:
        await finalize_run(session_factory, run.id)
        return

    # No session is held open while the model is working.
    try:
        completion = await llm.complete(
            generation.model, run.system_prompt, generation.prompt,
            run.temperature, run.max_tokens, run.seed,
        )
        failure = None
    except LLMError as error:
        completion, failure = None, str(error)

    async with session_factory() as session:
        stored = await session.get_one(Generation, generation_id)
        if completion is not None:
            stored.raw_response = completion.text
            stored.finish_reason = completion.finish_reason
            stored.usage = completion.usage
            stored.generated_at = datetime.now(UTC)
            # Cut-off and empty answers are not scanned: they would look clean.
            if completion.finish_reason == "length":
                failure = "response truncated at max_tokens"
            elif not completion.text.strip():
                failure = "empty response"
        if failure is None:
            stored.code = extract_code(completion.text)
            stored.status = GenerationStatus.GENERATED
        else:
            stored.status = GenerationStatus.FAILED
            stored.error = failure
        await session.commit()

    if failure is None:
        await publish(ANALYSIS_QUEUE, [generation_id])
    else:
        await finalize_run(session_factory, run.id)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    settings = get_settings()
    api_key = settings.llm_api_key.get_secret_value() if settings.llm_api_key else None
    llm = LLMClient(settings.llm_base_url, api_key, settings.llm_timeout_seconds)
    handle = partial(
        handle_generation,
        session_factory=get_session_factory(),
        llm=llm,
        publish=partial(publish_jobs, settings),
    )
    try:
        await consume(settings, GENERATION_QUEUE, handle)
    finally:
        await llm.close()


if __name__ == "__main__":
    asyncio.run(main())
