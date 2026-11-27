from datetime import datetime
from enum import StrEnum

from sqlalchemy import JSON, ForeignKey, MetaData, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime

Json = JSON().with_variant(JSONB, "postgresql")


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class GenerationStatus(StrEnum):
    PENDING = "pending"
    GENERATED = "generated"
    ANALYSED = "analysed"
    FAILED = "failed"


class AnalysisStatus(StrEnum):
    OK = "ok"
    ERROR = "error"


class Base(DeclarativeBase):
    # Stable constraint names let later migrations refer to them.
    metadata = MetaData(
        naming_convention={
            "pk": "pk_%(table_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ix": "ix_%(table_name)s_%(column_0_name)s",
        }
    )


class Task(Base):
    __tablename__ = "task"
    __table_args__ = (UniqueConstraint("task_set", "task_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    task_set: Mapped[str] = mapped_column(String(100))
    task_id: Mapped[str] = mapped_column(String(100))
    source: Mapped[str] = mapped_column(String(100))
    source_id: Mapped[str] = mapped_column(String(200))
    cwe: Mapped[str] = mapped_column(String(20))
    prompt_type: Mapped[str] = mapped_column(String(50))
    prompt: Mapped[str] = mapped_column(Text)


class Run(Base):
    __tablename__ = "run"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(20), default=RunStatus.QUEUED)
    task_set: Mapped[str] = mapped_column(String(100))
    models: Mapped[list[str]] = mapped_column(Json)
    conditions: Mapped[list[str]] = mapped_column(Json)
    analysers: Mapped[list[str]] = mapped_column(Json)
    system_prompt: Mapped[str] = mapped_column(Text)
    temperature: Mapped[float]
    max_tokens: Mapped[int]
    seed: Mapped[int | None]
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    generations: Mapped[list["Generation"]] = relationship(back_populates="run", order_by="Generation.id")


class Generation(Base):
    __tablename__ = "generation"
    __table_args__ = (UniqueConstraint("run_id", "task_pk", "model", "condition", "iteration"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("run.id", ondelete="CASCADE"))
    task_pk: Mapped[int] = mapped_column(ForeignKey("task.id"))
    model: Mapped[str] = mapped_column(String(200))
    condition: Mapped[str] = mapped_column(String(50))
    # 0 for the first answer, 1..3 for repair rounds.
    iteration: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(20), default=GenerationStatus.PENDING)
    prompt: Mapped[str] = mapped_column(Text)
    raw_response: Mapped[str | None] = mapped_column(Text)
    code: Mapped[str | None] = mapped_column(Text)
    finish_reason: Mapped[str | None] = mapped_column(String(50))
    usage: Mapped[dict | None] = mapped_column(Json)
    error: Mapped[str | None] = mapped_column(Text)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    run: Mapped[Run] = relationship(back_populates="generations")
    task: Mapped[Task] = relationship()
    analysis_results: Mapped[list["AnalysisResult"]] = relationship(back_populates="generation")


class AnalysisResult(Base):
    """One row per analyser per generation, also when it found nothing (FR-07)."""

    __tablename__ = "analysis_result"
    __table_args__ = (UniqueConstraint("generation_id", "analyser"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    generation_id: Mapped[int] = mapped_column(ForeignKey("generation.id", ondelete="CASCADE"))
    analyser: Mapped[str] = mapped_column(String(50))
    analyser_version: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20))
    error: Mapped[str | None] = mapped_column(Text)

    generation: Mapped[Generation] = relationship(back_populates="analysis_results")
    findings: Mapped[list["Finding"]] = relationship(order_by="Finding.id")


class Finding(Base):
    __tablename__ = "finding"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_result_id: Mapped[int] = mapped_column(
        ForeignKey("analysis_result.id", ondelete="CASCADE"), index=True
    )
    rule_id: Mapped[str] = mapped_column(String(200))
    # Null only when the analyser rule has no CWE mapping (FR-08).
    cwe: Mapped[str | None] = mapped_column(String(20))
    severity: Mapped[str] = mapped_column(String(20))
    line: Mapped[int | None]
    message: Mapped[str] = mapped_column(Text)
    raw: Mapped[dict] = mapped_column(Json)
