import asyncio
import json
import sys
import tempfile
from importlib.metadata import version
from pathlib import Path

from app.analysers.base import AnalyserError, NormalisedFinding


def normalise(report: dict) -> list[NormalisedFinding]:
    if report["errors"]:
        reasons = "; ".join(error["reason"] for error in report["errors"])
        raise AnalyserError(f"bandit could not scan the file: {reasons}")
    return [
        NormalisedFinding(
            rule_id=result["test_id"],
            cwe=f"CWE-{cwe['id']}" if (cwe := result.get("issue_cwe") or {}).get("id") else None,
            severity=result["issue_severity"].lower(),
            line=result.get("line_number"),
            message=result["issue_text"],
            raw=result,
        )
        for result in report["results"]
    ]


class BanditAnalyser:
    name = "bandit"

    def __init__(self, timeout: float = 60):
        self.timeout = timeout

    def version(self) -> str:
        return version("bandit")

    async def scan(self, code: str) -> list[NormalisedFinding]:
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "snippet.py").write_text(code, encoding="utf-8")
            # --ignore-nosec: generated code must not be able to silence findings.
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-I", "-m", "bandit", "-f", "json", "-q", "--ignore-nosec", "snippet.py",
                cwd=directory,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), self.timeout)
            except TimeoutError as error:
                process.kill()
                await process.wait()
                raise AnalyserError("bandit timed out") from error
        # Exit code 1 means "has findings"; anything above is a failure.
        if process.returncode not in (0, 1):
            raise AnalyserError(f"bandit exited {process.returncode}: {stderr.decode(errors='replace')[:300]}")
        try:
            report = json.loads(stdout)
        except ValueError as error:
            raise AnalyserError("bandit returned invalid JSON") from error
        return normalise(report)
