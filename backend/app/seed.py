import asyncio

from app.db import get_session_factory
from app.tasksets import BUILTIN_TASK_SETS, seed_task_set


async def main() -> None:
    async with get_session_factory()() as session:
        for name in BUILTIN_TASK_SETS:
            added = await seed_task_set(session, name)
            print(f"task set {name}: {added} tasks added")


if __name__ == "__main__":
    asyncio.run(main())
