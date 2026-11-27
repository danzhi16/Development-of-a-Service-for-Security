import asyncio
import logging
from collections.abc import Mapping
from dataclasses import asdict
from functools import partial

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import joinedload, selectinload

from app.analysers import ANALYSERS
from app.analysers.base import Analyser, AnalyserError
from app.config import get_settings
from app.db import get_session_factory
from app.lifecycle import finalize_run
from app.models import AnalysisResult, AnalysisStatus, Finding, Generation, GenerationStatus
from app.queue import ANALYSIS_QUEUE
from app.workers.runner import consume

logger = logging.getLogger(__name__)


# Static analysis only: generated code is read by the analysers and never executed.
async def run_analyser(analyser: Analyser, code: str) -> AnalysisResult:
    result = AnalysisResult(
        analyser=analyser.name, analyser_version=analyser.version(), status=AnalysisStatus.OK, findings=[]
    )
    try:
        findings = await analyser.scan(code)
    except AnalyserError as error:
        logger.warning("%s failed: %s", analyser.name, error)
        result.status, result.error = AnalysisStatus.ERROR, str(error)
    else:
        result.findings = [Finding(**asdict(finding)) for finding in findings]
    return result


async def handle_analysis(
    generation_id: int,
    session_factory: async_sessionmaker[AsyncSession],
    analysers: Mapping[str, Analyser] = ANALYSERS,
) -> None:
    async with session_factory() as session:
        query = (
            select(Generation)
            .where(Generation.id == generation_id)
            .options(joinedload(Generation.run), selectinload(Generation.analysis_results))
        )
        generation = await session.scalar(query)
        if generation is None:
            logger.warning("generation %s does not exist", generation_id)
            return
        # Anything but "generated" is a redelivery of a finished job.
        if generation.status == GenerationStatus.GENERATED:
            for name in generation.run.analysers:
                generation.analysis_results.append(await run_analyser(analysers[name], generation.code))
            failed = [r for r in generation.analysis_results if r.status == AnalysisStatus.ERROR]
            if failed:
                generation.status = GenerationStatus.FAILED
                generation.error = "; ".join(f"{r.analyser}: {r.error}" for r in failed)
            else:
                generation.status = GenerationStatus.ANALYSED
            # Results and status are committed together, so a crash leaves no partial rows.
            await session.commit()
    await finalize_run(session_factory, generation.run_id)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    handle = partial(handle_analysis, session_factory=get_session_factory())
    await consume(get_settings(), ANALYSIS_QUEUE, handle)


if __name__ == "__main__":
    asyncio.run(main())
