from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import Generation, GenerationStatus, Run


class FromModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class FindingOut(FromModel):
    rule_id: str
    cwe: str | None
    severity: str
    line: int | None
    message: str


class AnalysisOut(FromModel):
    analyser: str
    analyser_version: str
    status: str
    error: str | None
    findings: list[FindingOut]


class GenerationOut(BaseModel):
    id: int
    task_id: str
    task_cwe: str
    model: str
    condition: str
    iteration: int
    status: str
    error: str | None
    prompt: str
    raw_response: str | None
    code: str | None
    finish_reason: str | None
    usage: dict | None
    analysis: list[AnalysisOut]


class Counter(BaseModel):
    done: int
    total: int


class FailedJob(BaseModel):
    job_id: int
    error: str | None


class RunDetail(FromModel):
    id: int
    status: str
    error: str | None
    task_set: str
    models: list[str]
    conditions: list[str]
    analysers: list[str]
    system_prompt: str
    temperature: float
    max_tokens: int
    seed: int | None
    created_at: datetime
    finished_at: datetime | None
    # Filled by run_detail; the names match the progress example in docs/ux-prototype.md.
    generations: Counter
    analysis: Counter
    failed: list[FailedJob]
    jobs: list[GenerationOut]


def _generation(generation: Generation) -> GenerationOut:
    fields = {
        name: getattr(generation, name)
        for name in GenerationOut.model_fields
        if name not in ("task_id", "task_cwe", "analysis")
    }
    return GenerationOut(
        **fields,
        task_id=generation.task.task_id,
        task_cwe=generation.task.cwe,
        analysis=[AnalysisOut.model_validate(result) for result in generation.analysis_results],
    )


def run_detail(run: Run) -> RunDetail:
    jobs = run.generations
    total = len(jobs)
    generated = sum(job.status != GenerationStatus.PENDING for job in jobs)
    finished = sum(job.status in (GenerationStatus.ANALYSED, GenerationStatus.FAILED) for job in jobs)
    computed = ("generations", "analysis", "failed", "jobs")
    return RunDetail(
        **{name: getattr(run, name) for name in RunDetail.model_fields if name not in computed},
        generations=Counter(done=generated, total=total),
        analysis=Counter(done=finished, total=total),
        failed=[
            FailedJob(job_id=job.id, error=job.error)
            for job in jobs
            if job.status == GenerationStatus.FAILED
        ],
        jobs=[_generation(job) for job in jobs],
    )
