import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.llm import Completion
from app.models import AnalysisResult, Generation, Run
from app.workers.analysis import handle_analysis
from app.workers.generation import handle_generation

TASKS = 15


class FakeLLM:
    def __init__(self, code: str):
        self.code = code

    async def complete(self, *_args):
        return Completion(f"```python\n{self.code}```", "stop", None)


async def no_publish(_queue, _ids):
    return None


def run_jobs(api, session_factory, codes: list[str]):
    api.post("/runs", json={"models": ["m"], "task_set": "builtin-python-15", "conditions": ["baseline"]})

    async def scenario():
        for generation_id, code in enumerate(codes, start=1):
            await handle_generation(generation_id, session_factory, FakeLLM(code), no_publish)
            await handle_analysis(generation_id, session_factory)
            # A redelivered message must not add a second result.
            await handle_analysis(generation_id, session_factory)

    asyncio.run(scenario())


def query(session_factory, statement):
    async def scenario():
        async with session_factory() as session:
            return (await session.scalars(statement)).all()

    return asyncio.run(scenario())


def results(session_factory):
    statement = select(AnalysisResult).options(selectinload(AnalysisResult.findings))
    return query(session_factory, statement.order_by(AnalysisResult.generation_id))


def test_findings_and_clean_results_are_stored_once(api, seeded, session_factory):
    run_jobs(api, session_factory, ["import os\nos.system(input())\n", "x = 1\n"])

    vulnerable, clean = results(session_factory)

    assert (vulnerable.analyser, vulnerable.status) == ("bandit", "ok")
    assert vulnerable.analyser_version
    assert "B605" in {finding.rule_id for finding in vulnerable.findings}
    assert (clean.status, clean.findings) == ("ok", [])
    assert query(session_factory, select(Run))[0].status == "running"


def test_analyser_error_fails_the_job(api, seeded, session_factory):
    run_jobs(api, session_factory, ["def broken(:\n"])

    [result] = results(session_factory)
    generation = query(session_factory, select(Generation).where(Generation.id == 1))[0]

    assert result.status == "error"
    assert generation.status == "failed"
    assert generation.error.startswith("bandit: ")


def test_run_is_done_after_the_last_job(api, seeded, session_factory):
    run_jobs(api, session_factory, ["x = 1\n"] * TASKS)

    [run] = query(session_factory, select(Run))

    assert (run.status, run.error) == ("done", None)
    assert run.finished_at is not None
