# Pilot Results (feasibility check)

Author: Danial Boranbayev. Status: draft v0.1, 2026-10-20.

The pilot comes from the course research project (Research Methods). It checks that the planned pipeline
(generate, scan, repair) works end to end on a small sample. It is **not** the final experiment.

## Setup

- 15 Python tasks, one per CWE: 8 from SecurityEval, 7 from LLMSecEval, prompt text unchanged.
- Models (through OpenRouter): `google/gemma-4-31b-it`, `deepseek/deepseek-v4-flash`, `moonshotai/kimi-k2.6`.
- Conditions: `baseline`, `security_prefix`, `analyser_repair` (up to 3 rounds, applied to tasks that had findings in the baseline).
- Analyser: Bandit only. One generation per task.

## Result: tasks with at least one Bandit finding

| Model | Baseline | Security prefix | After repair (tasks repaired / still with findings) |
|---|---|---|---|
| gemma-4-31b-it | 13 of 15 | 5 of 15 | 13 repaired, 1 still with findings |
| deepseek-v4-flash | 10 of 15 | 8 of 15 | 10 repaired, 0 still with findings |
| kimi-k2.6 | 12 of 15 | 4 of 15 (2 responses truncated, not scanned) | 12 repaired, 0 still with findings |

Counts were recomputed on 2026-10-20 from `results.jsonl` of each model (last iteration per task and condition).

## What this does and does not show

- The pipeline works: generation, extraction, Bandit scan and the repair loop ran for all three models.
- The direction (prefix lowers, repair lowers further) is consistent with the literature (Bruni et al., 2025; Alrashedy et al., 2025),
  but with 15 tasks, one generation and one analyser no hypothesis is tested.
- Two Kimi responses in the prefix condition (`SE_CWE-611_author_1`, `LSE_CWE-306_MAC-1a`) were cut by the 8000-token limit.
- Bandit is the weakest of the three planned analysers in depth. Repair "success" against the same analyser that triggered the repair
  is optimistic; Semgrep and CodeQL are needed to see whether the effect holds.

## Use in the service

The pilot script is the baseline for the verification plan ([verification-plan.md](verification-plan.md)):
the service must reproduce these counts on the same inputs, within model sampling variation.
