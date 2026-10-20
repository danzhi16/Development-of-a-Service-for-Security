# 5. Technology Comparison

Author: Andrey Rudov. Status: draft v0.1, 2026-10-20.

Scores are qualitative (++ strong, + adequate, - weak) against the project requirements in
[requirements.md](requirements.md). They are a design judgement, not measurements. Items
marked **spike** must be confirmed on our hardware before the decision is final (see ADR plan at the end).

## D1. Backend framework

Requirement drivers: async I/O (long LLM calls), OpenAPI contract for the UI, team skills (Python), NFR-05 maintainability.

| Criterion | FastAPI | Django REST Framework | Go (net/http or Gin) |
|---|---|---|---|
| Async request handling | ++ native | + via ASGI, ORM mostly sync | ++ |
| Auto-generated OpenAPI | ++ built in | + via extra package | - manual or codegen |
| Python ecosystem for analysers and LLM clients | ++ same language | ++ | - needs subprocess/HTTP glue |
| Admin/ORM batteries | + (with SQLAlchemy) | ++ | - |
| Team experience | ++ | + | + |

**Decision: FastAPI.** Same language as the analysis pipeline, OpenAPI for free. Django adds weight we do not need.

## D2. Job queue (message exchange between API and workers)

Requirement drivers: jobs last minutes, must survive worker restarts, retry on failure (NFR-03).

| Criterion | RabbitMQ | Kafka | Redis-based queue (RQ/arq) |
|---|---|---|---|
| Acknowledgement and redelivery | ++ | + (offset commits, more manual) | - weaker durability by default |
| Dead-letter / retry | ++ | - build yourself | - |
| Operational weight for 1 host | + | - heavy (broker plus coordination) | ++ already needed for cache |
| Fit for task queue semantics | ++ | - designed for event log | + |

**Decision: RabbitMQ.** Task-queue semantics with acknowledgements fit the job model. Kafka solves a log-streaming
problem we do not have. Kafka and RabbitMQ were the initial candidates; this comparison selects RabbitMQ.

## D3. LLM inference server

Requirement drivers: serve several open-weight models locally, batch many short requests, fit limited VRAM (NFR-04).

| Criterion | vLLM | Ollama | llama.cpp server |
|---|---|---|---|
| Throughput under batched load | ++ continuous batching (**spike**) | + | + |
| Setup effort on a laptop or single GPU | + | ++ | ++ |
| Quantised models on small VRAM | + | ++ | ++ |
| OpenAI-compatible HTTP API | ++ | + | + |
| Model catalogue convenience | + (Hugging Face) | ++ own registry | + (GGUF files) |

**Decision: vLLM as the primary server, Ollama as fallback for machines without a suitable GPU.**
The service talks to an OpenAI-compatible endpoint through one adapter, so both are interchangeable.
**Spike:** measure tokens/s and memory for the three target models on the available hardware.

## D4. Persistent storage

Requirement drivers: runs, tasks, generated files, findings with variable structure per analyser (FR-08, FR-10).

| Criterion | PostgreSQL | SQLite | MongoDB |
|---|---|---|---|
| Relational integrity (run, task, model, condition) | ++ | + | - |
| Semi-structured findings (JSON) | ++ JSONB | + JSON1 | ++ |
| Concurrent writers (several workers) | ++ | - single writer | ++ |
| Aggregation queries for reports | ++ SQL | + | + |

**Decision: PostgreSQL.** Findings go to a JSONB column next to normalised CWE columns. SQLite stays for unit tests.

## D5. Isolation for untrusted generated code

Requirement drivers: generated code is untrusted, must never reach network or host files (NFR-02).

| Criterion | Docker with hardening | gVisor (runsc) | Firecracker microVM |
|---|---|---|---|
| Isolation strength | + shared kernel | ++ user-space kernel | ++ separate kernel |
| Setup effort | ++ | + | - needs KVM, orchestration |
| Start-up cost | ++ | + | + |
| Works in CI on a laptop | ++ | + | - |

**Decision: Docker** with no network, read-only root filesystem, dropped capabilities, CPU/memory/time limits,
as an MVP baseline. gVisor is the planned upgrade if the supervisor requires code execution.

## D6. Static analysers

Requirement drivers: more than one independent analyser (the key finding of the literature review:
the measured effect of a mitigation depends on the analyser), CWE mapping, free to use.

| Criterion | Bandit | Semgrep | CodeQL |
|---|---|---|---|
| Analysis depth | - pattern based on AST | + pattern and limited dataflow | ++ dataflow queries on a code database |
| Speed per snippet | ++ | ++ | - database build per run |
| CWE tags in output | + | ++ rule metadata | ++ |
| Effort to integrate | ++ | ++ | + |
| Licence for our use | open source | open-source engine, check rule-pack terms | **check**: CodeQL terms restrict use outside open-source and research |

**Decision: all three**, behind one `Analyser` interface. Licence terms for Semgrep rule packs and CodeQL
must be checked and recorded before the final defense (task in backlog).

## Summary of decisions

| Area | Choice | Rejected | Needs spike |
|---|---|---|---|
| Framework | FastAPI | Django REST, Go | no |
| Queue | RabbitMQ | Kafka, Redis queue | no |
| Inference | vLLM (+ Ollama fallback) | llama.cpp | yes |
| Storage | PostgreSQL | SQLite (tests only), MongoDB | no |
| Isolation | Docker hardened | gVisor, Firecracker | no |
| Analysers | Bandit + Semgrep + CodeQL | none | licence check |

Frontend technology is compared in [ux-prototype.md](ux-prototype.md).

## ADR plan

Each decision above becomes a short ADR in `docs/adr/` when the corresponding spike or check is done.
