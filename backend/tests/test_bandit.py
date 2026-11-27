import asyncio

import pytest

from app.analysers.bandit import BanditAnalyser, normalise
from app.analysers.base import AnalyserError


def scan(code: str):
    return asyncio.run(BanditAnalyser().scan(code))


def test_vulnerable_code_is_normalised():
    findings = scan("import os\nos.system(input())\n")

    shell = next(finding for finding in findings if finding.rule_id == "B605")
    assert (shell.cwe, shell.line) == ("CWE-78", 2)
    assert shell.severity in {"low", "medium", "high"}
    assert shell.message and shell.raw["test_id"] == "B605"


def test_clean_code_has_no_findings():
    assert scan("def add(a, b):\n    return a + b\n") == []


def test_nosec_comment_does_not_hide_findings():
    code = "import subprocess\nsubprocess.call(input(), shell=True)  # nosec\n"

    assert "B602" in {finding.rule_id for finding in scan(code)}


def test_unparsable_code_is_an_error_not_a_clean_result():
    with pytest.raises(AnalyserError, match="could not scan"):
        scan("def broken(:\n")


@pytest.mark.parametrize("issue_cwe", [{}, None])
def test_rule_without_cwe_mapping_keeps_null_cwe(issue_cwe):
    result = {"test_id": "B000", "issue_cwe": issue_cwe, "issue_severity": "LOW", "issue_text": "t"}

    [finding] = normalise({"errors": [], "results": [result]})

    assert finding.cwe is None
