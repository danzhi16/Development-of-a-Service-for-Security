import os
import time

import httpx
import pytest

BASE_URL = os.environ.get("E2E_BASE_URL")
pytestmark = pytest.mark.skipif(not BASE_URL, reason="set E2E_BASE_URL to a stack started with the stub LLM")


def test_pilot_sized_run_goes_through_the_whole_pipeline():
    with httpx.Client(base_url=BASE_URL, timeout=10) as api:
        request = {"models": ["stub"], "task_set": "builtin-python-15", "conditions": ["baseline"]}
        created = api.post("/runs", json=request).raise_for_status().json()
        assert created["total_jobs"] == 15

        deadline = time.monotonic() + 120
        while True:
            run = api.get(f"/runs/{created['id']}").raise_for_status().json()
            if run["status"] in ("done", "failed") or time.monotonic() > deadline:
                break
            time.sleep(1)

    assert run["status"] == "done"
    assert run["failed"] == []
    assert [job["status"] for job in run["jobs"]] == ["analysed"] * 15
    for job in run["jobs"]:
        rules = {finding["rule_id"] for result in job["analysis"] for finding in result["findings"]}
        assert "B605" in rules
