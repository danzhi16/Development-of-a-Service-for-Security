import pytest

from app.prompts import build_prompt, extract_code

PREFIX = "You are a security-aware developer."


def test_baseline_sends_the_task_unchanged():
    assert build_prompt("baseline", "def f(x): return {x}") == "def f(x): return {x}"


def test_security_prefix_is_prepended_only_in_its_condition():
    prompt = build_prompt("security_prefix", "task")

    assert prompt.startswith(PREFIX)
    assert prompt.endswith("\n\ntask")
    assert PREFIX not in build_prompt("baseline", "task")


def test_unsupported_condition_is_rejected():
    with pytest.raises(ValueError):
        build_prompt("analyser_repair", "task")


@pytest.mark.parametrize(
    ("response", "code"),
    [
        ("text\n```python\nimport os\n```\nmore", "import os\n"),
        ("```py\na = 1\n```", "a = 1\n"),
        ("```\na\n```\n```python\nlonger = 1\n```", "longer = 1\n"),
        ("import sys\n", "import sys\n"),
    ],
)
def test_extract_code(response, code):
    assert extract_code(response) == code
