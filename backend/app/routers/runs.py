import logging
from datetime import UTC, datetime
from functools import partial
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import AfterValidator, BaseModel, Field, StringConstraints
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysers import SUPPORTED_ANALYSERS
from app.config import Settings, get_settings
from app.db import get_session
from app.models import Generation, Run, RunStatus, Task
from app.prompts import SUPPORTED_CONDITIONS, SYSTEM_PROMPT, build_prompt
from app.queue import GENERATION_QUEUE, Publish, publish_jobs

logger = logging.getLogger(__name__)
router = APIRouter(tags=["runs"])


def _unique(values: list[str]) -> list[str]:
    if len(set(values)) != len(values):
        raise ValueError("values must be unique")
    return values


def _subset_of(allowed: tuple[str, ...]):
    def check(values: list[str]) -> list[str]:
        unknown = [value for value in values if value not in allowed]
        if unknown:
            raise ValueError(f"unsupported: {unknown}; allowed: {list(allowed)}")
        return _unique(values)

    return AfterValidator(check)


ModelName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class RunCreate(BaseModel):
    models: Annotated[list[ModelName], Field(min_length=1), AfterValidator(_unique)]
    task_set: str
    conditions: Annotated[list[str], Field(min_length=1), _subset_of(SUPPORTED_CONDITIONS)]
    analysers: Annotated[list[str], Field(min_length=1), _subset_of(SUPPORTED_ANALYSERS)] = list(
        SUPPORTED_ANALYSERS
    )
    temperature: float = Field(0, ge=0, le=2)
    max_tokens: int = Field(8000, ge=1, le=100_000)
    seed: int | None = Field(None, ge=0, le=2**31 - 1)


class RunCreated(BaseModel):
    id: int
    status: str
    total_jobs: int


def get_publisher(settings: Settings = Depends(get_settings)) -> Publish:
    return partial(publish_jobs, settings)


@router.post("/runs", status_code=201, response_model=RunCreated)
async def create_run(
    request: RunCreate,
    session: AsyncSession = Depends(get_session),
    publish: Publish = Depends(get_publisher),
):
    query = select(Task).where(Task.task_set == request.task_set).order_by(Task.id)
    tasks = (await session.scalars(query)).all()
    if not tasks:
        raise HTTPException(422, f"unknown task set: {request.task_set}")

    run = Run(**request.model_dump(), system_prompt=SYSTEM_PROMPT)
    run.generations = [
        Generation(task=task, model=model, condition=condition, prompt=build_prompt(condition, task.prompt))
        for model in request.models
        for task in tasks
        for condition in request.conditions
    ]
    session.add(run)
    # Commit before publishing, so a worker never receives an id it cannot read.
    await session.commit()

    try:
        await publish(GENERATION_QUEUE, [generation.id for generation in run.generations])
    except Exception as error:
        logger.exception("could not queue run %s", run.id)
        run.status = RunStatus.FAILED
        run.error = "could not queue the jobs"
        run.finished_at = datetime.now(UTC)
        await session.commit()
        raise HTTPException(503, f"queue unavailable; run {run.id} marked as failed") from error
    return RunCreated(id=run.id, status=run.status, total_jobs=len(run.generations))
