import asyncio

import pytest
from sqlalchemy import select

from app.models import Task
from app.tasksets import seed_task_set

BUILTIN = "builtin-python-15"


async def seed(session_factory) -> int:
    async with session_factory() as session:
        return await seed_task_set(session, BUILTIN)


def test_builtin_set_has_15_tasks_with_distinct_cwe_and_source(api, session_factory):
    asyncio.run(seed(session_factory))

    tasks = api.get("/tasks").json()

    assert len(tasks) == 15
    assert len({task["cwe"] for task in tasks}) == 15
    assert {task["source"] for task in tasks} == {"SecurityEval", "LLMSecEval"}


def test_seeding_twice_adds_nothing(session_factory):
    assert asyncio.run(seed(session_factory)) == 15
    assert asyncio.run(seed(session_factory)) == 0


def test_changed_prompt_of_a_stored_task_is_rejected(session_factory):
    async def edit_stored_prompt():
        async with session_factory() as session:
            task = (await session.scalars(select(Task).limit(1))).one()
            task.prompt = "edited"
            await session.commit()

    asyncio.run(seed(session_factory))
    asyncio.run(edit_stored_prompt())

    with pytest.raises(ValueError, match="changed"):
        asyncio.run(seed(session_factory))
