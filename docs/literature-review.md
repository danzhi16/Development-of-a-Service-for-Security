# 3. Literature Review

Author: Danial Boranbayev. Status: draft v0.1, 2026-10-20.

Source of the list: the verified-source file of the course research project (Research Methods, Assignment 1),
where each venue was checked on 2026-09-18/19. All sources are from 2022-2026. Of 19 sources, 14 are
peer-reviewed (PR) and 5 are preprints (PP), so the requirement of at least 12 sources with at least 8
scientific publications is met. **Before the defense, each author must reread the papers they cite**: the
numbers below come from the verification notes, not from a fresh reading.

## 1. What is already known

**LLM-generated code is often insecure.** Pearce et al. (2022) generated 1,689 programs for 89 scenarios
covering MITRE Top-25 CWEs and found about 40% vulnerable [1]. Fu et al. (2025) analysed 733 Copilot-generated
snippets from live GitHub projects, found 43 CWEs, with 29.5% of Python snippets vulnerable [3]. Asare et al.
(2023) found that Copilot is not worse than human developers in their scenarios [2], and Kharma et al. (2026)
extend the comparison to several languages and models [4]. Human-factor studies disagree: Perry et al. (2023)
report that assistant users wrote less secure code and were more confident in it [6], while Sandoval et al. (2023)
found a small security effect in low-level C [7].

**Benchmarks exist, but most are synthetic and single-function.** SecurityEval (130 Python prompts, 75 CWE types) [8],
LLMSecEval (150 natural-language prompts over the Top-25, with secure reference implementations) [9], SALLM,
which adds an execution environment and security-aware metrics [10], and DeVAIC, a tool for assessing
AI-generated code [12]. Repository-level benchmarks are harder: SecRepoBench (318 tasks from 27 C/C++ repositories) [13] and
RealSec-bench (105 instances from Java repositories) [14].

**Mitigations by prompting and analyser feedback work for GPT models.** Tony et al. (2025) evaluate prompting techniques
on GPT models with the LLMSecEval prompts [15]. Bruni et al. (2025) report up to 56% fewer vulnerabilities from a
security-focused prefix and 41.9-68.7% from iterative self-repair [16]. Alrashedy et al. (2025) show that analyser
feedback helps, but the improvement is 33% when measured with Bandit and 12% with CodeQL [17].

## 2. Limitations the project must take into account

1. **The instrument changes the result.** The same mitigation shows 33% or 12% improvement depending on the analyser [17],
   and CASTLE reports a heavy false-positive load across 13 static analysers and 10 LLMs [11]. A service must therefore
   use more than one analyser and report their agreement. This drives FR-07 and FR-10.
2. **Open-weight models are thinly covered.** Studies [15] and [16] test GPT models only; [17] includes one older open-weight model (CodeLlama-34B).
   The users of our service run current open-weight models, which these studies did not measure.
3. **Synthetic prompts.** Benchmarks [8] and [9] use short tasks. SALLM argues that such tasks differ from code embedded in real systems [10].
   Repository-level evaluation is out of scope here (needs builds, other languages).
4. **Research code is not a product.** The evaluations above are papers with scripts and datasets. We did not find (in this review) a paper that packages
   model comparison by code security as a reusable service. The product-side comparison is in [existing-systems-comparison.md](existing-systems-comparison.md).

## 3. Structured analysis table

| # | Source | Venue / status | Contribution | Limitation for our project | Used for |
|---|---|---|---|---|---|
| 1 | Pearce et al. 2022, Asleep at the Keyboard | IEEE S&P 2022, PR | ~40% of Copilot programs vulnerable in 89 scenarios | Copilot only, 2021 model | Problem statement |
| 2 | Asare et al. 2023, Is Copilot as bad as humans | Empirical Software Eng. 28(6), PR | Copilot not worse than humans in their scenarios | Copilot only | Balance of evidence |
| 3 | Fu et al. 2025, Copilot weaknesses in GitHub projects | ACM TOSEM, PR | 733 real snippets, 29.5% of Python vulnerable, feedback fixed up to 55.5% | Copilot only | Problem statement, repair idea |
| 4 | Kharma et al. 2026, Multi-language multi-model analysis | IEEE TDSC (accepted), PR | Compares security across languages and models | Not a reusable tool | Related work |
| 5 | Morkonda et al. 2026, Security of LLM code: comparative | arXiv, PP | Comparative analysis of LLM code security | Preprint | Context only |
| 6 | Perry et al. 2023, Do users write more insecure code | ACM CCS 2023, PR | Assistant users less secure but more confident | Human study | Why verification is needed |
| 7 | Sandoval et al. 2023, Lost at C | USENIX Security 2023, PR | Small security effect in C | Low-level C | Counter-evidence |
| 8 | Siddiq, Santos 2022, SecurityEval | MSR4P&S 2022, PR | 130 Python prompts, 75 CWE types | Synthetic | Task set (8 of 15 tasks) |
| 9 | Tony et al. 2023, LLMSecEval | MSR 2023, PR | 150 NL prompts, Top-25 CWEs | Synthetic | Task set (7 of 15 tasks) |
| 10 | Siddiq et al. 2024, SALLM | ASEW 2024, PR | Framework with execution environment and security metrics | Workshop paper, research framework | Closest research system |
| 11 | Dubniczky et al. 2025, CASTLE | arXiv, PP | 250 micro-benchmarks, 13 analysers, 10 LLMs | Preprint; micro-benchmarks | Analyser trust |
| 12 | Cotroneo et al. 2024, DeVAIC | Information and Software Technology, PR | Tool for assessing security of AI-generated code | Detection tool, not model comparison | Related tool |
| 13 | Shen et al. 2026, SecRepoBench | arXiv, PP | 318 repository-level tasks in C/C++ | C/C++, builds needed | Out-of-scope justification |
| 14 | Wang et al. 2026, RealSec-bench | Findings of ACL 2026, PR | 105 Java repository instances | Java, builds needed | Out-of-scope justification |
| 15 | Tony et al. 2025, Prompting techniques for secure code | ACM TOSEM, PR | Prompting reduces vulnerabilities for GPT models | GPT only | Evaluation conditions |
| 16 | Bruni et al. 2025, Benchmarking prompt engineering | IEEE/ACM FORGE 2025, PR | Prefix up to 56% fewer vulnerabilities, self-repair 41.9-68.7% | GPT only | Evaluation conditions |
| 17 | Alrashedy et al. 2025, Feedback-driven security patching | J. Cybersecurity and Privacy 5(4), PR | Analyser feedback beats self-review; 33% (Bandit) vs 12% (CodeQL) | One older open-weight model | Repair condition, multi-analyser need |
| 18 | Basic, Giaretta 2026, SLR vulnerabilities to remediation | arXiv, PP | Systematic review of LLMs in code security | Preprint | Framing |
| 19 | SLR 2024, Security of language models for code | arXiv, PP | Systematic review | Preprint | Framing |

Numbers in brackets in the text refer to the table row, except where a citation is given by author and year.

## 4. Gap that motivates the service

The effect of security mitigations and the security of generated code are established mostly for proprietary models,
on synthetic single-function prompts, and against one analyser at a time. A team that runs open-weight models
locally cannot reproduce such an evaluation on its own models without writing scripts. The service closes this
gap by packaging the evaluation (tasks, conditions, several analysers, normalised report).

## 5. Items still to verify

- Khoury et al. (IEEE SMC 2023), SeCodePLT and LLMSecCode were noticed but not inspected. Do not cite them until checked.
- Publication status of CASTLE and SecRepoBench may have changed since the last arXiv revision.
- Add two or three papers on LLM serving or sandboxing if the thesis needs a technical-background chapter.

## References

Full BibTeX is in the course project file `Assignment1_References_AndreyRudov.bib`; copy it to `docs/references.bib` when it is verified.
