# Database Schema

PostgreSQL schema of the service (DIP-14). The source of truth is
[backend/app/models.py](../backend/app/models.py); changes go through Alembic migrations in
`backend/migrations/`, applied by the `migrate` service on `docker compose up`.

```mermaid
erDiagram
    task ||--o{ generation : "is solved by"
    run ||--o{ generation : contains
    generation ||--o{ analysis_result : "is scanned by"
    analysis_result ||--o{ finding : reports

    task {
        int id PK
        string task_set UK "with task_id"
        string task_id UK
        string source
        string source_id
        string cwe
        string prompt_type
        text prompt
    }
    run {
        int id PK
        string status "queued, running, done, failed"
        string task_set
        jsonb models
        jsonb conditions
        jsonb analysers
        text system_prompt
        float temperature
        int max_tokens
        int seed "nullable"
        text error "nullable"
        timestamptz created_at
        timestamptz finished_at "nullable"
    }
    generation {
        int id PK
        int run_id FK
        int task_pk FK
        string model
        string condition
        int iteration "0, or the repair round"
        string status "pending, generated, analysed, failed"
        text prompt
        text raw_response "nullable"
        text code "nullable"
        string finish_reason "nullable"
        jsonb usage "nullable"
        text error "nullable"
        timestamptz generated_at "nullable"
    }
    analysis_result {
        int id PK
        int generation_id FK
        string analyser
        string analyser_version
        string status "ok, error"
        text error "nullable"
    }
    finding {
        int id PK
        int analysis_result_id FK
        string rule_id
        string cwe "null if the rule has no mapping"
        string severity
        int line "nullable"
        text message
        jsonb raw
    }
```

## Rules

- `generation` is also the unit of work: one row per (run, task, model, condition, iteration).
- `analysis_result` has one row per analyser and generation, **including analysers that found
  nothing** (FR-07). A failed scan has status `error` and must not be counted as clean.
- The analyser of a finding is the one of its `analysis_result` (FR-08).
- Reproducibility fields (NFR-06): model id (`generation.model`), parameters and seed (`run`),
  prompt text (`run.system_prompt`, `generation.prompt`), analyser version (`analysis_result`).
