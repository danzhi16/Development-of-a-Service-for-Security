from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models import Generation, GenerationStatus, Run, RunStatus

ACTIVE_RUN = (RunStatus.QUEUED, RunStatus.RUNNING)


# Call after the job is committed: then whichever worker finishes last sees every job as terminal.
async def finalize_run(session_factory: async_sessionmaker[AsyncSession], run_id: int) -> None:
    async with session_factory() as session:
        query = (
            select(Generation.status, func.count())
            .where(Generation.run_id == run_id)
            .group_by(Generation.status)
        )
        counts = dict((await session.execute(query)).all())
        if counts.get(GenerationStatus.PENDING) or counts.get(GenerationStatus.GENERATED):
            return
        succeeded = bool(counts.get(GenerationStatus.ANALYSED))
        await session.execute(
            update(Run)
            .where(Run.id == run_id, Run.status.in_(ACTIVE_RUN))
            .values(
                status=RunStatus.DONE if succeeded else RunStatus.FAILED,
                error=None if succeeded else "all jobs failed",
                finished_at=datetime.now(UTC),
            )
        )
        await session.commit()
