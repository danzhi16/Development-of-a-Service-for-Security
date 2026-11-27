import json
from pathlib import Path

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task

DATA_DIR = Path(__file__).parent / "data"
BUILTIN_TASK_SETS = ("builtin-python-15",)


class TaskRecord(BaseModel):
    task_id: str
    source: str
    source_id: str
    cwe: str
    prompt_type: str
    prompt: str


def load_task_set(name: str) -> list[TaskRecord]:
    lines = (DATA_DIR / f"{name}.jsonl").read_text(encoding="utf-8").splitlines()
    return [TaskRecord.model_validate(json.loads(line)) for line in lines if line.strip()]


# Stored tasks are never rewritten: old runs must keep pointing at the prompt they used.
async def seed_task_set(session: AsyncSession, name: str) -> int:
    query = select(Task).where(Task.task_set == name)
    existing = {task.task_id: task for task in await session.scalars(query)}
    added = 0
    for record in load_task_set(name):
        stored = existing.get(record.task_id)
        if stored is None:
            session.add(Task(task_set=name, **record.model_dump()))
            added += 1
        elif stored.prompt != record.prompt:
            raise ValueError(f"{name}/{record.task_id} changed; publish it as a new task set")
    await session.commit()
    return added
