from dataclasses import dataclass
from typing import Protocol


class AnalyserError(Exception):
    """The scan did not complete, which is different from finding nothing."""


@dataclass
class NormalisedFinding:
    rule_id: str
    cwe: str | None
    severity: str
    line: int | None
    message: str
    raw: dict


class Analyser(Protocol):
    name: str

    def version(self) -> str: ...

    async def scan(self, code: str) -> list[NormalisedFinding]: ...
