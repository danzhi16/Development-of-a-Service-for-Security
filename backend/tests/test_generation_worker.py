import asyncio

import pytest
from sqlalchemy.orm import joinedload

from app.llm import Completion, LLMError
from app.models import Generation
from app.workers.generation import handle_generation


class FakeLLM:
    def __init__(self, reply):
        self.reply = reply
        self.calls = []

    async def complete(self, *args):
        self.calls.append(args)
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply


def answer(text="```python\nimport os\n```", finish_reason="stop"):
    return Completion(text, finish_reason, {"total_tokens": 5})


@pytest.fixture
def job(api, seeded) -> int:
    request = {"models": ["m"], "task_set": "builtin-python-15", "conditions": ["baseline"]}
    api.post("/runs", json=request)
    return 1


def work(session_factory, job, llm, published):
    async def publish(queue_name, ids):
        published.append((queue_name, ids))

    asyncio.run(handle_generation(job, session_factory, llm, publish))


def load(session_factory, job) -> Generation:
    async def scenario():
        async with session_factory() as session:
            return await session.get_one(Generation, job, options=[joinedload(Generation.run)])

    return asyncio.run(scenario())


def test_answer_is_stored_and_sent_to_analysis(session_factory, job, published):
    llm = FakeLLM(answer())

    work(session_factory, job, llm, published)

    generation = load(session_factory, job)
    assert (generation.status, generation.code) == ("generated", "import os\n")
    assert generation.raw_response.startswith("```python")
    assert generation.usage == {"total_tokens": 5}
    assert generation.run.status == "running"
    assert published[-1] == ("analysis", [job])
    assert llm.calls[0][0] == "m"


@pytest.mark.parametrize(
    ("reply", "error"),
    [
        (LLMError("LLM server timeout"), "LLM server timeout"),
        (answer(finish_reason="length"), "response truncated at max_tokens"),
        (answer(text="  "), "empty response"),
    ],
)
def test_unusable_answer_fails_the_job_without_analysis(session_factory, job, published, reply, error):
    published.clear()

    work(session_factory, job, FakeLLM(reply), published)

    generation = load(session_factory, job)
    assert (generation.status, generation.error, generation.code) == ("failed", error, None)
    assert published == []


def test_redelivered_job_is_republished_without_a_second_model_call(session_factory, job, published):
    llm = FakeLLM(answer())

    async def broken(_queue, _ids):
        raise ConnectionError

    with pytest.raises(ConnectionError):
        asyncio.run(handle_generation(job, session_factory, llm, broken))
    work(session_factory, job, llm, published)

    assert len(llm.calls) == 1
    assert published[-1] == ("analysis", [job])


def test_run_fails_when_every_job_fails(session_factory, job, published):
    for generation_id in range(1, 16):
        work(session_factory, generation_id, FakeLLM(LLMError("down")), published)

    run = load(session_factory, job).run
    assert (run.status, run.error) == ("failed", "all jobs failed")
    assert run.finished_at is not None
