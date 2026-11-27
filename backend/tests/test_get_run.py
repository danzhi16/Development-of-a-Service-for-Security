import asyncio

from app.llm import Completion, LLMError
from app.workers.analysis import handle_analysis
from app.workers.generation import handle_generation

REQUEST = {"models": ["m"], "task_set": "builtin-python-15", "conditions": ["baseline"], "seed": 1}


class FakeLLM:
    async def complete(self, _model, _system, prompt, *_args):
        if "yaml_load" in prompt:
            return Completion("```python\nimport os\nos.system(input())\n```", "stop", None)
        raise LLMError("LLM server timeout")


async def no_publish(_queue, _ids):
    return None


def test_unknown_run_is_404(api):
    assert api.get("/runs/99").status_code == 404


def test_run_shows_progress_failures_and_findings(api, seeded, session_factory):
    api.post("/runs", json=REQUEST)

    async def work():
        for generation_id in (1, 2):
            await handle_generation(generation_id, session_factory, FakeLLM(), no_publish)
        await handle_analysis(1, session_factory)

    asyncio.run(work())

    run = api.get("/runs/1").json()

    assert (run["status"], run["seed"]) == ("running", 1)
    assert run["generations"] == {"done": 2, "total": 15}
    assert run["analysis"] == {"done": 2, "total": 15}
    assert run["failed"] == [{"job_id": 2, "error": "LLM server timeout"}]
    first, third = run["jobs"][0], run["jobs"][2]
    assert (first["task_cwe"], first["status"]) == ("CWE-20", "analysed")
    assert first["prompt"] and first["raw_response"]
    [bandit] = first["analysis"]
    assert bandit["analyser_version"]
    assert "B605" in {finding["rule_id"] for finding in bandit["findings"]}
    assert (third["status"], third["analysis"]) == ("pending", [])
