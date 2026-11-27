import asyncio

import pytest
from sqlalchemy import select

from app.main import app
from app.models import Generation, Run
from app.routers.runs import get_publisher

REQUEST = {
    "models": ["model-a", "model-b"],
    "task_set": "builtin-python-15",
    "conditions": ["baseline", "security_prefix"],
}


def fetch_all(session_factory, model):
    async def scenario():
        async with session_factory() as session:
            return (await session.scalars(select(model))).all()

    return asyncio.run(scenario())


def test_run_creates_and_queues_one_job_per_model_task_condition(api, seeded, published, session_factory):
    response = api.post("/runs", json=REQUEST)

    assert response.status_code == 201
    assert response.json() == {"id": 1, "status": "queued", "total_jobs": 60}
    generations = fetch_all(session_factory, Generation)
    assert published == [("generation", [generation.id for generation in generations])]
    assert len({(g.model, g.task_pk, g.condition) for g in generations}) == 60


def test_run_stores_reproducibility_parameters(api, seeded, session_factory):
    api.post("/runs", json=REQUEST | {"seed": 42, "max_tokens": 100})

    [run] = fetch_all(session_factory, Run)

    assert (run.temperature, run.max_tokens, run.seed) == (0, 100, 42)
    assert run.analysers == ["bandit"]
    assert run.system_prompt.startswith("You are a coding assistant.")


@pytest.mark.parametrize(
    "change",
    [
        {"models": []},
        {"models": ["a", "a"]},
        {"models": ["  "]},
        {"conditions": ["analyser_repair"]},
        {"analysers": ["codeql"]},
        {"task_set": "missing"},
    ],
)
def test_invalid_run_is_rejected_and_nothing_is_stored(api, seeded, published, session_factory, change):
    response = api.post("/runs", json=REQUEST | change)

    assert response.status_code == 422
    assert published == []
    assert fetch_all(session_factory, Run) == []


def test_publish_failure_marks_the_run_failed(api, seeded, session_factory):
    async def broken(_queue, _ids):
        raise ConnectionRefusedError

    app.dependency_overrides[get_publisher] = lambda: broken

    response = api.post("/runs", json=REQUEST)

    assert response.status_code == 503
    [run] = fetch_all(session_factory, Run)
    assert (run.status, run.error) == ("failed", "could not queue the jobs")
    assert run.finished_at is not None
