import asyncio

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.models import AnalysisResult, AnalysisStatus, Generation, Run, Task


def make_generation() -> Generation:
    task = Task(
        task_set="set", task_id="t1", source="s", source_id="1", cwe="CWE-78",
        prompt_type="nl", prompt="p",
    )
    run = Run(
        task_set="set", models=["m"], conditions=["baseline"], analysers=["bandit"],
        system_prompt="sys", temperature=0, max_tokens=10,
    )
    return Generation(run=run, task=task, model="m", condition="baseline", prompt="p")


def bandit_result() -> AnalysisResult:
    return AnalysisResult(analyser="bandit", analyser_version="1", status=AnalysisStatus.OK)


def test_clean_analysis_is_stored_without_findings(session_factory):
    async def scenario():
        async with session_factory() as session:
            generation = make_generation()
            generation.analysis_results.append(bandit_result())
            session.add(generation)
            await session.commit()

        async with session_factory() as session:
            query = select(AnalysisResult).options(selectinload(AnalysisResult.findings))
            return (await session.scalars(query)).one()

    stored = asyncio.run(scenario())

    assert stored.status == "ok"
    assert stored.findings == []


def test_second_result_of_the_same_analyser_is_rejected(session_factory):
    async def scenario():
        async with session_factory() as session:
            generation = make_generation()
            generation.analysis_results.extend([bandit_result(), bandit_result()])
            session.add(generation)
            await session.commit()

    with pytest.raises(IntegrityError):
        asyncio.run(scenario())
