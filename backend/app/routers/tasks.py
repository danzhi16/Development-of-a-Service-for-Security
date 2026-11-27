from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Task
from app.tasksets import TaskRecord

router = APIRouter(tags=["tasks"])


class TaskOut(TaskRecord):
    model_config = ConfigDict(from_attributes=True)

    task_set: str


@router.get("/tasks", response_model=list[TaskOut])
async def list_tasks(task_set: str | None = None, session: AsyncSession = Depends(get_session)):
    query = select(Task).order_by(Task.task_set, Task.id)
    if task_set is not None:
        query = query.where(Task.task_set == task_set)
    return (await session.scalars(query)).all()
