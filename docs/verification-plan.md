# 9. Verification and Evaluation Plan

Author: Danial Boranbayev. Status: draft v0.1, 2026-10-20.

Two questions are verified: (a) does the software work as specified ([requirements](requirements.md)),
(b) does the service achieve its aim, a reproducible and trustworthy comparison of open-weight models by code security.

## 1. Testing plan

| Level | What | Tools | Covers | When |
|---|---|---|---|---|
| Unit | Prompt builder, code extraction from LLM response, normaliser (analyser output to CWE record), metrics | pytest, fixtures | FR-05, FR-08, FR-09 | Every pull request (CI) |
| Component | Analyser adapters run on known vulnerable and clean files | pytest, Docker | FR-07, NFR-02 | Every pull request |
| Integration | API plus queue plus worker plus DB with a stub LLM that returns canned code | pytest, Docker Compose | FR-01, FR-04, FR-15, NFR-03 | Per milestone |
| Fault injection | Kill a worker mid-run, restart; sandbox tries network and write | scripts | NFR-02, NFR-03 | Per milestone |
| End-to-end | Real small model, 15 tasks, 3 conditions | Compose | FR-01..FR-13, NFR-04, NFR-08 | Before each pre-defense |
| Usability | 3 users do the scenario "create a run, read the ranking" | Observation, timing | NFR-07 | Once the UI exists |
| Security hygiene | Secret scan, dependency check | CI | NFR-09 | Every pull request |

Test data: a fixture set of 10 code files with hand-labelled vulnerabilities (5 vulnerable, 5 clean) and the 15 pilot tasks.

## 2. Outcome metrics

| Metric | Definition | Target |
|---|---|---|
| Insecure-output rate | Generations with at least one finding / all valid generations, per model, condition, analyser | Reported, no target (it is the object being measured) |
| CWE distribution | Findings per CWE per model | Reported |
| Analyser agreement | Share of generations flagged by both analysers of a pair; Cohen's kappa on flagged/not flagged | Reported with number of generations |
| Analyser precision on sample | Of findings in a random sample of 50, share confirmed by manual review of two team members | At least 70% for the analyser set used in rankings; below that the analyser is marked "low confidence" (threshold to agree with supervisor) |
| Reproducibility | Two runs on the same stored generations give identical metrics; a rerun with the same seed gives the same generation where the backend supports seeds | 100% identical metrics on stored generations |
| Pipeline correctness | Service counts vs the hand-computed table for the fixture run | Exact match |
| Throughput | Time per run of 3 models x 15 tasks x 3 conditions | Recorded on the reference machine; ≤ 2 hours is the working goal |
| Usability | Task completion time and success for 3 users | ≥ 3 of 3 finish in under 5 minutes |

## 3. Measurement conditions

- Reference machine: TODO (GPU model and memory, CPU, RAM), recorded in the report. Not fixed yet (risk R1).
- Model ids, quantisation, temperature, max tokens and seed are stored with each run (NFR-06).
- Analyser versions are pinned in the Docker images; Semgrep rule pack version is recorded.
- Each configuration is run at least 3 times on the final experiment; proportions are reported with a 95% confidence interval
  (Wilson interval) and paired comparisons use McNemar's test on the same tasks.
- Truncated or unparsable responses are counted separately and excluded from rates, with their number shown.

## 4. Baseline solution for comparison

| Baseline | What it is | What we compare |
|---|---|---|
| B1: manual pilot script | The course project script that generates and scans with Bandit and writes `results.jsonl` | Same 15 tasks, same models: counts must match B1 within sampling variation; effort to run is compared (steps, time) |
| B2: manual analyser run | A person runs Bandit, Semgrep and CodeQL by hand on a folder of files and merges results in a spreadsheet | Time to get a comparable table for 3 models; correctness against the service output |
| B3: related system | CyberSecEval (Meta) run on the same models, if it can run on our hardware | Whether the model ranking by insecure-output rate is consistent in direction (different tasks, so only rank order) |

B3 is optional: if CyberSecEval cannot be run, this is stated as a limitation.

## 5. How the aim will be demonstrated

1. The service reproduces the pilot (B1) through its API and UI without manual steps.
2. It produces the three-analyser table that the pilot could not (B2 needs hours by hand; the service target is one run).
3. Manual review of a sample shows how trustworthy each analyser is, so the ranking is reported with its confidence.
4. Usability test shows that a new user can obtain a ranking.

## 6. Threats to validity

- 15 tasks are a small sample; the final experiment should use more tasks (SecurityEval and LLMSecEval have 130 and 150 prompts).
- Static analysers have false positives and false negatives; this is why agreement and manual review are in the plan.
- Models served through different quantisation can behave differently from the original weights.
- Prompt wording of the security prefix is our own; results depend on it.
