# 4. Existing Systems Comparison

Author: Dias Mukhametkali. Status: draft v0.2, 2026-10-23.

## Method

Five systems were chosen because each solves part of the problem: evaluating LLM code security, scanning code for
vulnerabilities, or controlling AI-generated code. Nine criteria were derived from the proposal
([project-proposal.md](project-proposal.md)). Cells checked against a source on 2026-10-23 cite it as [n] (list below).
Cells without [n] are first-draft judgements from the same sources and were not re-checked one by one. Where a source
gave no answer, the cell says **not verified** and names what was checked, instead of guessing.
Vendor statements are marked **(vendor claim)**. This is a focused comparison, not a full market survey.

| Code | System | Type |
|---|---|---|
| S1 | CyberSecEval (Meta, Purple Llama) | Open-source benchmark suite for LLM security |
| S2 | SALLM (Siddiq et al., 2024) | Research framework for security assessment of generated code |
| S3 | GitHub code scanning autofix (CodeQL + Copilot) | Commercial feature in GitHub Advanced Security |
| S4 | Snyk Code (DeepCode AI) | Commercial SAST with AI autofix |
| S5 | SonarQube AI Code Assurance | Commercial quality gate for projects with AI code |

## Criteria

1. **K1** Compares several LLMs by the security of their generated code.
2. **K2** Evaluates code that an LLM generated from tasks it controls (generation inside the tool).
3. **K3** Supports open-weight models run locally.
4. **K4** Uses more than one analyser and reports their agreement.
5. **K5** Maps findings to CWE.
6. **K6** Can run on the user's own infrastructure (code stays inside).
7. **K7** Has a UI or API usable by a non-researcher.
8. **K8** Open source or free to use.
9. **K9** Offers remediation of findings.

## Comparison

Legend: **Yes**, **Partial**, **No**, **not verified** (no answer in the sources checked).

| Criterion | S1 CyberSecEval | S2 SALLM | S3 GitHub autofix | S4 Snyk Code | S5 SonarQube AI Code Assurance |
|---|---|---|---|---|---|
| K1 Compare LLMs by security | Yes (benchmark across models) | Yes (framework for assessing models) | No (fixes alerts in a repository) | No | No |
| K2 Generation inside the tool | Yes (autocomplete and instruct tests) | Yes | No (code already written) | No | No (labels projects that contain AI code) |
| K3 Local open-weight models | Partial: OpenAI-compatible endpoints with a custom base URL; other self-hosted models need user-written inference code; not tried by us [3] | Partial: repo generates code from Hugging Face models with the Transformers library; the paper does not say how models were run [5][6] | No: fixes come from internal Copilot APIs [7] | No | No |
| K4 Several analysers + agreement | No: one detector ("Insecure Code Detector") | No: one static analyser (CodeQL) plus Docker-based tests; no agreement reported [5] | No: CodeQL | No: DeepCode AI engine | No: Sonar rules |
| K5 CWE mapping | Yes: about 189 patterns related to 50 CWEs [1] | Partial: each prompt is labelled with a CWE ID; CodeQL findings are not explicitly linked to CWE in the paper [5] | Yes: alerts come from CodeQL security queries, each associated with one or more CWEs [8] | Yes: each rule lists the CWE numbers it covers [10] | Yes: security rules reference CWE (e.g. CWE-89, CWE-327); CWE Top 25 2021-2024 covered (vendor claim) [13] |
| K6 Self-hosted | Yes (open source code) [3] | Yes: open-source scripts with a Docker test environment; not tried by us [5][6] | No (GitHub service) | Partial: local no-upload option requires Snyk Code Local Engine (vendor claim) [11] | Yes: SonarQube Server edition [14] |
| K7 UI/API for non-researchers | No: command-line interface only [3] | No: Python scripts and Jupyter notebooks; no UI described [6] | Yes (pull-request workflow) [7] | Yes | Yes (project pages, badges) [14] |
| K8 Open source / free | Yes: open source, MIT licence [4] | Yes: open source, Apache-2.0 licence [6] | No: governed by GitHub Advanced Security terms [7] | No: commercial | No: commercial editions |
| K9 Remediation | No | No: the repair step fixes syntax errors only, not vulnerabilities [5] | Yes: suggested fix with explanation [7]; at launch, fixes for more than two thirds of found vulnerabilities with little or no editing (vendor claim) [9] | Yes: autofix, "85%-accurate" (vendor claim, no independent benchmark found) [12] | No: gate and labelling; the docs describe no fixes [14] |

## Findings

- Systems that compare models (S1, S2) are research benchmarks: one static detector each, command-line or notebook
  use only, and the validity of S1 is debated: "Rethinking CyberSecEval" says the key drawbacks are in the insecure
  code detection part of S1's method, and that this detection process did not change in CyberSecEval 2 and 3 [2].
- Systems with a product UI (S3, S4, S5) check code that already exists in a repository; none of the three compares models.
- None of the five reports agreement between several analysers (K4). The literature shows why this matters: the same mitigation looks 33% or 12% effective depending on the analyser
  (Alrashedy et al., 2025 [15]; see [literature review](literature-review.md)).
- None of the five combines model comparison, local open-weight models and a UI for a non-researcher (K1+K3+K7) in the sources reviewed.

**Conclusion.** Among the systems reviewed, none offers a self-hostable service that compares open-weight models by the security of the
code they generate, with several analysers and CWE reports. This is the niche of the proposed service. The conclusion is limited to the reviewed
systems and to the evidence available.

## To do before the defense

- Re-check the cells without [n] against their sources.
- Consider adding one more research tool (DeVAIC) as S6.
- Try to run S1 locally; the result feeds baseline B3 of the [verification plan](verification-plan.md).

## Sources

Access date 2026-10-23 for every source below, except where noted.

1. [CyberSecEval, original paper (arXiv:2312.04724), HTML v1](https://arxiv.org/html/2312.04724v1), section 2.1: "approximately 189 patterns related to 50 different Common Weakness Enumerations (CWEs)". Also [CyberSecEval 3 (arXiv:2408.01605)](https://arxiv.org/pdf/2408.01605) (not re-opened; access date 2026-10-20).
2. [Rethinking CyberSecEval: an LLM-aided approach to evaluation critique (arXiv:2411.08813)](https://arxiv.org/html/2411.08813v1), introduction: "the nature of the insecure code detection process has not changed"; abstract: "Key drawbacks focus on the insecure code detection part of Meta's methodology."
3. [PurpleLlama CybersecurityBenchmarks README](https://github.com/facebookresearch/PurpleLlama/blob/main/CybersecurityBenchmarks/README.md), "Running the Benchmarks": "For OpenAI compatible endpoints, you can also specify a custom base URL"; "How to run benchmarks for self hosted models": "Implement your inferencing logic for at least the following required methods"; "Our command line interface uses the format".
4. [PurpleLlama CybersecurityBenchmarks LICENSE](https://github.com/facebookresearch/PurpleLlama/blob/main/CybersecurityBenchmarks/LICENSE): "MIT License".
5. Siddiq, Santos, Devareddy, Muller (2024), [SALLM: Security Assessment of Generated Code, arXiv:2311.00889 v3](https://arxiv.org/html/2311.00889v3), ASE 2024 workshops (ASYDE). Section 3.1.2: "label it with a CWE-ID"; 3.3.1: "our framework uses CodeQL", "Sallm has a Docker-based testing environment"; 3.2: the repair component is "responsible for automatically fixing syntax errors".
6. [SALLM repository (s2e-lab/SALLM)](https://github.com/s2e-lab/SALLM), README: CodeGen.ipynb generates code "from the Huggingface LLMs" using "the Huggingface Transformers library"; [LICENSE](https://github.com/s2e-lab/SALLM/blob/main/LICENSE): "Apache License, Version 2.0".
7. [GitHub Docs: Responsible use of Copilot Autofix for code scanning](https://docs.github.com/en/code-security/code-scanning/managing-code-scanning-alerts/responsible-use-autofix-code-scanning): "internal GitHub Copilot APIs interfacing with the large language models"; use "is governed by the existing terms and conditions associated with GitHub Advanced Security". Current languages: C#, C/C++, Go, Java/Kotlin, Swift, JavaScript/TypeScript, Python, Ruby, Rust (subset of queries).
8. [CodeQL CWE coverage](https://codeql.github.com/codeql-query-help/codeql-cwe-coverage/): "Every security query is associated with one or more CWEs".
9. [GitHub Blog, "Found means fixed" (20 March 2024)](https://github.blog/2024/03/20/found-means-fixed-introducing-code-scanning-autofix-powered-by-github-copilot-and-codeql/): suggestions "shown to remediate more than two-thirds of found vulnerabilities with little or no editing"; at launch it covered "more than 90% of alert types in JavaScript, Typescript, Java, and Python". Earlier secondary source: [The Hacker News, March 2024](https://thehackernews.com/2024/03/github-launches-ai-powered-autofix-tool.html) (returned HTTP 403 on 2026-10-23; access date 2026-10-20; its claims are now cited from [7] and [9]).
10. [Snyk Code security rules](https://docs.snyk.io/scan-fix-and-prevent/scan-with-snyk/snyk-code/snyk-code-security-rules): "CWEs: The CWE numbers the rule covers."
11. [Snyk Code documentation](https://docs.snyk.io/snyk-code), deployment table: "Local no-upload implementation (requires Snyk Code Local Engine)".
12. [Snyk DeepCode AI](https://snyk.io/platform/deepcode-ai/): "powers 85%-accurate security autofixes". The first draft said "over 80%"; the page now says 85%.
13. [SonarQube Server: Security-related rules](https://docs.sonarsource.com/sonarqube-server/quality-standards-administration/managing-rules/security-related-rules): examples "CWE-89: SQL Injection", "CWE-327: Use of a Broken or Risky Cryptographic Algorithm"; "CWE Top 25 (versions 2024, 2023, 2022, and 2021)".
14. [SonarQube Server: Quality gates for AI code](https://docs.sonarsource.com/sonarqube-server/quality-standards-administration/ai-code-assurance/quality-gates-for-ai-code): "Any quality gate can be marked as qualified for AI code". The page does not say which editions include it, and describes no remediation.
15. Alrashedy, Aljasser, Tambwekar, Gombolay (2025), Leveraging Static Analysis for Feedback-Driven Security Patching in LLM-Generated Code, Journal of Cybersecurity and Privacy 5(4), 110, [doi:10.3390/jcp5040110](https://doi.org/10.3390/jcp5040110). Related preprint by the same authors (not confirmed to be the same text): [Can LLMs Patch Security Issues? (arXiv:2312.00024v4)](https://arxiv.org/html/2312.00024v4): Table 2 (Bandit) and Table 3 (CodeQL).
