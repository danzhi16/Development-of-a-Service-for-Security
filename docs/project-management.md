# 10. Project Management and Risks

Author: Andrey Rudov. Status: draft v0.1, 2026-10-20.

## Tools

| Item | Value |
|---|---|
| Git repository | GitHub, this repository (`main` is the reviewed baseline, work in `DIP-<n>-<slug>` branches) |
| YouTrack project | TODO: add the link. Create the project and import the backlog below before 24 October. |
| Review rule | Team project: another team member reviews every pull request before merge. |
| Tags | `pre-defense-1`, `pre-defense-2`, `final-pre-defense` |

## Responsibilities

| Area | Owner | Reviewer |
|---|---|---|
| Architecture, API, queue, DB | Andrey Rudov | Danial Boranbayev |
| LLM inference, generation worker | Andrey Rudov | Danial Boranbayev |
| Analysis pipeline, sandbox, normaliser | Andrey Rudov | Dias Mukhametkali |
| Task sets, prompt conditions, experiments | Danial Boranbayev | Andrey Rudov |
| Metrics definition, verification plan | Danial Boranbayev | Andrey Rudov |
| Web UI, report visualisation, UX | Dias Mukhametkali | Danial Boranbayev |
| Existing-systems comparison, usability tests | Dias Mukhametkali | Danial Boranbayev |

## Milestones

Dates follow the supervisor's plan in the justification letter.

| Period | Milestone | Result |
|---|---|---|
| By 24 Oct 2026 | Pre-defense 1 | Analysis and design documents, diagrams, prototype, verification plan, backlog in YouTrack |
| Oct - Nov 2026 | Analysis | Interviews, literature and benchmark review, requirements, architecture, choice of models and analysers (spikes) |
| Dec 2026 - Jan 2027 | MVP | Model deployment, generation, integrated analysers, first end-to-end run |
| Feb - Mar 2027 | Full service | Complete API and UI, experiments, metrics, reports |
| Apr 2027 | Testing | Testing, results analysis, thesis text |
| May 2027 | Pre-defense and defense | Fixes after comments, plagiarism check, defense preparation |

## Initial backlog (to be created in YouTrack)

Task IDs are proposed; use the real YouTrack IDs in branches and commits.
Every task needs an assignee, expected outcome, acceptance criteria and deadline.

| Proposed ID | Task | Owner | Priority | Deadline |
|---|---|---|---|---|
| DIP-1 | Repository structure, README, `.gitignore` | Andrey | High | 2026-10-24 |
| DIP-2 | Project proposal and scope | Andrey | High | 2026-10-24 |
| DIP-3 | Interviews with 3-5 potential users | Dias | High | 2026-10-24 (first two) |
| DIP-4 | Literature review and analysis table | Danial | High | 2026-10-24 |
| DIP-5 | Existing systems comparison | Dias | High | 2026-10-24 |
| DIP-6 | Technology comparison | Andrey | High | 2026-10-24 |
| DIP-7 | Requirements and acceptance criteria | Andrey | High | 2026-10-24 |
| DIP-8 | Context, use-case and component diagrams | Andrey | High | 2026-10-24 |
| DIP-9 | UX mockups and API examples | Dias | High | 2026-10-24 |
| DIP-10 | Verification and evaluation plan | Danial | High | 2026-10-24 |
| DIP-11 | Spike: vLLM vs Ollama on available hardware | Andrey | High | 2026-11-07 |
| DIP-12 | Spike: Semgrep and CodeQL on the 15 pilot files | Danial | High | 2026-11-07 |
| DIP-13 | Check licence terms of Semgrep rule packs and CodeQL | Danial | Medium | 2026-11-14 |
| DIP-14 | Database schema and ER diagram | Andrey | High | 2026-11-14 |
| DIP-15 | Docker Compose skeleton (API, DB, queue) | Andrey | High | 2026-11-21 |
| DIP-16 | Port pilot script to the generation worker | Andrey | High | 2026-12-05 |
| DIP-17 | UI skeleton with mocked API | Dias | Medium | 2026-12-05 |

## Risks

| ID | Risk | Probability | Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| R1 | Not enough GPU memory to run three target models locally | Medium | High | Quantised models through Ollama; start with smaller models; vLLM spike in DIP-11 | Andrey |
| R2 | CodeQL licence or setup blocks use in the service | Medium | Medium | Check terms in DIP-13; fall back to Bandit + Semgrep and report the limitation | Danial |
| R3 | Analysers disagree so much that the metrics are not trustworthy | High | Medium | This is a research finding, not only a risk; report agreement and use a manually labelled sample as reference | Danial |
| R4 | Untrusted generated code escapes the sandbox | Low | High | Static analysis only in MVP; hardened container; no network | Andrey |
| R5 | Team members work in parallel with a job, so the schedule slips | High | Medium | Weekly sync with supervisor, small tasks of 1-3 days, re-plan at each milestone | All |
| R6 | No real user interviews are available before the next pre-defense | Medium | Medium | Start outreach now, record assumptions explicitly (see [evidence](evidence-of-relevance.md)) | Dias |
| R7 | Pilot results change with a different model snapshot or API provider | Medium | Low | Store model id, parameters and date with each run (NFR-06) | Andrey |
| R8 | Scope creep into multi-language or repository-level evaluation | Medium | High | Keep non-goals in the proposal; add only after the Python pipeline is stable | Andrey |

## Dependencies

- Public datasets SecurityEval and LLMSecEval (available, copied unchanged in the pilot).
- Access to GPU hardware or OpenRouter-style API for generation experiments (pilot used OpenRouter; the service targets local models).
- Supervisor decision on code execution in the MVP.
- Semgrep and CodeQL availability and licence terms.

## Next steps after 24 October

1. Create YouTrack tasks and link them to branches and pull requests.
2. Run spikes DIP-11 and DIP-12, record ADRs.
3. Hold at least three interviews and update the evidence document.
4. Start the database schema and Docker Compose skeleton.
