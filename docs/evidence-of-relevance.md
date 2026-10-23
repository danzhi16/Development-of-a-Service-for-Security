# 2. Evidence of Relevance

Author: Dias Mukhametkali. Status: draft v0.3, 2026-10-23. **3 of the required 3-5 interviews held (2026-10-23); see the log in section 3.**

The assessment requires 3-5 discussions with user representatives or an agreement with a real client. These must be real.
This file separates what is verified from what is assumed. Fill the interview log only with actual conversations.

## 1. Who to talk to

| Group | Why | How many | Candidates (fill in) |
|---|---|---|---|
| Developers using LLM code assistants | Main users of model comparison | 2 | TODO |
| DevSecOps / security engineer | Judge usefulness of findings and CWE reports | 1-2 | TODO |
| Lecturer or researcher (e.g. the supervisor) | Reproducible evaluation method | 1 | TODO |

The course supervisor, Arstan Makatov, can be one discussion if the conversation is recorded in the log below.

## 2. Interview guide (20-30 minutes)

1. Which AI coding tools or models do you use or consider? Local or hosted? Why?
2. How do you decide which model to use? Does security play a role?
3. Have you seen vulnerable code from an LLM? What happened?
4. How do you check AI-generated code today (review, scanners, nothing)? Which tools?
5. If a tool compared models by the security of their output, what would you need to see in the report?
6. Would you run it on your own machine or server? What are the constraints (GPU, privacy, time)?
7. Which result would make you trust the report, and which would not?
8. Show the mockups in [ux-prototype.md](ux-prototype.md): what is unclear or missing?

Record: date, role (no names needed), key answers, quotes with permission. Ask for consent to use anonymised notes.

## 3. Interview log (fill after each real conversation)

| # | Date | Role | Format | Key findings | Requirement impact |
|---|---|---|---|---|---|
| 1 | 2026-10-23 | Student, uses Claude and Gemini for code | Text chat (messenger), 18 min | Uses hosted tools only (no GPU for local models); has received an LLM-generated hard-coded API key and SQL built by string concatenation; checks code mostly manually, sometimes Bandit; wants ranking, explained score, CWE, severity, code fragments, corrected examples; would not trust a single percentage without code and methodology | Make local-model execution optional; support model APIs; explain score calculation; provide CWE and severity breakdowns, reproducible configurations, side-by-side code comparison, filters, and PDF/JSON export |
| 2 | 2026-10-23 | Backend developer, mid-size company | Text chat (messenger), 18 min | Uses hosted Copilot and Claude; team considers local open-weight models for sensitive code but does not use them regularly (deployment cost); has seen SQL concatenation, secrets in config, verbose errors, missing authorization checks; uses SonarQube or Semgrep, but these do not compare models; wants ranking, CWE, severity, prompts, parameters, false-positive information; prefers a company server with Docker Compose; asks for a CPU-only mode | CPU-only mode for small evaluations; separate confirmed findings from possible false positives and critical issues from minor ones; filters by CWE, severity, language and model; show model version, prompts, parameters, scanner versions and rules; repeated runs; progress with estimated time and hardware requirements; PDF/JSON export |
| 3 | 2026-10-23 | DevSecOps engineer, mid-size technology company | Voice, 22 min, recorded | Company mainly uses approved hosted services; prefers local open-weight models or private cloud for sensitive code; has seen over-privileged CI/CD configs, root containers, hardcoded secrets, weak crypto, disabled TLS verification, SQL injection; checks AI code in CI with Semgrep or SonarQube, Trivy, Gitleaks, Checkov; wants ranking plus evidence, but "one overall score is not sufficient"; GPU should be optional; would not trust single-scanner, single-generation results | In scope: separate confirmed findings from possible false positives; scanners usable without a GPU; support hosted APIs; secret redaction in logs; role-based access and audit log (extends FR-16); SARIF export. Out of scope (future work): separate results for Dockerfiles, CI/CD and infrastructure-as-code |

All participants agreed to the use of anonymised notes. The notes below are the participants' answers as recorded
by Dias; names and companies are not recorded.

### Interview 1 notes (student, 2026-10-23)

1. Tools: "I mainly use the hosted versions of Claude and Gemini. I use Claude to explain code, find mistakes, and refactor longer code fragments. I use Gemini for quick questions and because it works conveniently with Google services. I have not used local models because my laptop does not have a powerful GPU, while hosted tools are easier to use."
2. Choosing a model: "I choose based on response quality, speed, context-window size, and usage limits. For university exercises, security is not always my first criterion. However, I never upload passwords, API keys, personal information, private repositories, or confidential files. For company code, privacy and security would be much more important."
3. Vulnerable code: "Yes. An AI once generated Python code containing an API key directly in the source file. I also received an SQL example that used string concatenation instead of parameters. The code worked, but it could expose credentials or allow SQL injection. I corrected these problems after reviewing the code."
4. Checking code: "I read the code, run it with different inputs, and test error cases. For larger assignments, I use unit tests and GitHub Dependabot. Sometimes I use Bandit for Python, but I do not run security scanners for every task. Most of my checking is still manual."
5. Report needs: "I would want an overall security score and ranking, together with an explanation of how the score was calculated. The report should show CWE categories, severity levels, vulnerable code fragments, corrected examples, and successful and failed test cases. Models should be tested using identical prompts and settings."
6. Own machine: "I could run a lightweight version with Docker Compose on my laptop, but probably not several large local models. My limitations are GPU memory, disk space, execution time, and setup complexity. I would prefer using hosted model APIs together with a local security-analysis service."
7. Trust: "I would trust reproducible results that use identical prompts and show the scanner findings, test environment, and links to CWE descriptions. Repeating each test several times would also increase trust. I would not trust a report containing only one percentage or ranking without code examples, methodology, tool versions, or information about false positives."
8. Mockups: "The comparison is understandable, but the meaning of the security score should be explained more clearly. I would add tooltips for CWE and severity, filters by programming language and vulnerability type, and a side-by-side comparison of vulnerable and corrected code. The interface should show model versions, prompts, generation parameters, scanner versions, test duration, and whether the analysis was local or cloud-based. PDF and JSON export would also be useful."

Quote (with permission): "A security score is useful only when I can open it and see which code caused the score."

Assessment by Dias: E3 no information (understands the privacy benefit of local processing but does not use local models
or know how teams deploy them); E4 supports (combines manual review, testing and occasional scanners, knows no tool that
compares models under identical conditions); E5 supports; E6 partially contradicts (Docker Compose is fine for lightweight
services, but the laptop GPU is not enough for several large models).

### Interview 2 notes (backend developer, mid-size company, 2026-10-23)

1. Tools: "I mainly use GitHub Copilot and Claude for boilerplate code, explanations, test generation, and refactoring. These are hosted tools because they are convenient and produce good results. For sensitive internal code, our team considers local open-weight models, but we do not use them regularly because deployment and maintenance require additional resources."
2. Choosing a model: "We consider output quality, speed, programming-language support, IDE integration, cost, and the provider's data-retention policy. Developers must not send credentials, customer data, production logs, or proprietary code to an unapproved service. However, we currently lack a clear benchmark for comparing the security of generated code."
3. Vulnerable code: "Yes. I have seen generated code that used string concatenation for SQL queries, stored secrets in configuration files, returned detailed error messages, and created API endpoints without proper authorization checks. These problems were identified during code review and testing before release. AI-generated code should be treated as an untrusted draft."
4. Checking code: "AI-generated code goes through the same process as manually written code: developer review, pull-request review, unit and integration tests, linting, and CI checks. We use tools such as SonarQube or Semgrep, dependency scanning, and secret detection. However, these tools inspect the final repository and do not directly compare the models."
5. Report needs: "I would want an overall ranking, vulnerability counts, severity levels, CWE identifiers, affected code fragments, explanations, prompts, model parameters, and information about false positives. The report should separate critical vulnerabilities from minor code-quality issues and allow results to be filtered by language and task type. PDF and JSON export would be useful."
6. Own machine: "I would prefer running it on a company server through Docker Compose, especially for proprietary prompts or local models. Developer laptops may not have sufficient GPU memory. The main constraints are GPU availability, model size, storage, setup complexity, evaluation time, and keeping code inside the company network. A CPU-only mode would be useful for smaller evaluations."
7. Trust: "I would trust a reproducible report containing the exact model version, prompts, parameters, scanner versions, rules, raw findings, and results from several repeated runs. Manual validation of critical findings would increase trust. I would not trust a single unexplained score, a ranking based on only a few prompts, or a report that treats every scanner warning as a confirmed vulnerability."
8. Mockups: "The general comparison flow is understandable, but the interface should explain how the security score is calculated. I would add filters for CWE, severity, language, and model; side-by-side code comparison; links to affected lines; scanner and model configurations; and a distinction between confirmed findings and possible false positives. It should also show evaluation progress, estimated completion time, hardware requirements, and export options."

Assessment by Dias: E3 partially supports (the team considers local open-weight models for sensitive code but does not
use them regularly); E4 supports ("we currently lack a clear benchmark for comparing the security of generated code");
E5 supports (asks for a ranking and CWE identifiers, plus false-positive information and model parameters); E6 partially
contradicts (prefers Docker Compose on a company server, but laptops may lack GPU memory and a CPU-only mode is wanted).

### Interview 3 notes (DevSecOps engineer, mid-size technology company, 2026-10-23)

Voice call, recorded; the answers below were written up from the recording. Consent: the participant agreed that
anonymised notes and quotations could be used in the diploma without mentioning their name or company.

1. Tools: "I use GitHub Copilot and Claude for code explanations, CI/CD configuration, test generation, and reviewing infrastructure code. Our company primarily uses approved hosted services because they are easier to maintain. For sensitive source code, infrastructure configurations, or security data, we prefer local open-weight models or private cloud deployment. The choice depends on the data classification and company policy."
2. Choosing a model: "Security is one of the main selection criteria. We evaluate the provider's privacy policy, data-retention rules, enterprise controls, model quality, supported languages, cost, and integration with our development workflow. A model should not receive production secrets, customer information, internal vulnerabilities, or unfiltered logs. Even if a model produces high-quality code, we cannot use it if it does not meet our security and compliance requirements."
3. Vulnerable code: "Yes. I have seen AI-generated CI/CD configurations with excessive permissions, Dockerfiles that ran containers as the root user, and Kubernetes manifests without resource limits or security contexts. I have also seen code with hardcoded secrets, weak cryptographic algorithms, disabled TLS verification, and SQL queries vulnerable to injection. Most problems were discovered during code review or security scanning before deployment."
4. Checking code: "We treat AI-generated code like any other untrusted contribution. It must pass peer review, automated tests, and security checks in the CI/CD pipeline. Depending on the project, we use Semgrep or SonarQube for SAST, Trivy for containers and dependencies, Gitleaks for secrets, Checkov for infrastructure-as-code, and OWASP Dependency-Check or similar software-composition-analysis tools. Critical findings block the pipeline until they are reviewed or fixed."
5. Report needs: "I would want both a model ranking and detailed evidence. The report should include CWE identifiers, severity levels, vulnerability categories, affected code fragments, scanner evidence, and secure corrected examples. It should also show the exact prompt, model name and version, generation parameters, scanner versions, and number of repeated runs. Confirmed vulnerabilities and possible false positives must be clearly separated. The report should provide separate results for application code, Dockerfiles, CI/CD configurations, and infrastructure-as-code. One overall score is not sufficient because models may perform differently depending on the task."
6. Own machine: "For a company environment, I would prefer deploying the service on an internal server or private cloud using Docker Compose for a prototype and Kubernetes for a larger production deployment. The main constraints are GPU availability, GPU memory, model size, storage, processing time, maintenance, and access control. The system should also support hosted APIs because not every company can run large models locally. Security scanners should work without a GPU, while GPU use should be optional for local model inference. The system must prevent secrets and source code from being stored in logs."
7. Trust: "I would trust a reproducible report based on a documented benchmark, identical prompts, fixed model versions, repeated generations, multiple security scanners, and manual validation of critical findings. The methodology should explain how the final score is calculated and how false positives are handled. I would not trust a report with only one unexplained percentage, results from a single generation, unknown model versions, or findings produced by only one scanner without validation. I would also question a ranking if the models were tested with different prompts or parameters."
8. Mockups: "The main workflow is understandable, but the interface should provide more technical and security information. It should explain the score calculation and show which findings influenced the score. I would add filters for CWE, severity, model, programming language, scanner, and artifact type. The interface should show vulnerable and corrected code side by side, identify affected lines, and distinguish confirmed vulnerabilities from possible false positives. It should also display model versions, prompts, scanner versions, execution environment, evaluation progress, estimated completion time, and hardware requirements. I would also add role-based access control, an audit log, data-retention settings, secret redaction, and export to PDF, JSON, or SARIF. SARIF export would allow findings to be integrated with existing DevSecOps tools and CI/CD platforms."

Quote (with permission): "AI-generated code should enter the pipeline as untrusted code and earn trust through review, testing, and security scanning."

Assessment by Dias: E3 partially supports (prefers local open-weight models or private cloud for sensitive code, but the
company mainly uses hosted services and does not say it runs local models); E4 no direct information (lists the tools
used, but does not say a model-comparison tool is missing); E5 supports with a condition (wants a ranking with CWE, but
"one overall score is not sufficient"); E6 partially contradicts (Docker Compose is fine, but GPU availability is a
constraint and GPU use should be optional).

## 4. Verified findings vs assumptions

"Literature" means supported by a published study ([literature review](literature-review.md)). It is evidence for the problem,
not evidence that our users have it. "User-verified" gives the assessment per interview (#n refers to the log in section 3).

| ID | Statement | Basis | User-verified |
|---|---|---|---|
| E1 | LLM-generated code frequently contains vulnerabilities | Literature (Pearce et al., 2022; Fu et al., 2025) | n/a |
| E2 | Measured benefit of a security mitigation depends on the analyser | Literature (Alrashedy et al., 2025) | n/a |
| E3 | Teams run open-weight models locally for privacy reasons | **Assumption** (stated in the supervisor's justification letter) | #1: no information; #2: partially supports (considers local models, does not use them regularly); #3: partially supports (prefers local or private cloud for sensitive code, mainly uses hosted services) |
| E4 | Teams lack a ready tool to compare models by output security | **Assumption**; partly supported by [existing-systems comparison](existing-systems-comparison.md) | #1: supports; #2: supports; #3: no direct information |
| E5 | Users want a CWE-based report with a model ranking | **Assumption** | #1: supports; #2: supports; #3: supports with a condition (ranking alone is not sufficient) |
| E6 | Users can run a Docker Compose stack with a GPU | **Assumption** | #1: partially contradicts; #2: partially contradicts (CPU-only mode wanted); #3: partially contradicts (Docker Compose yes, GPU should be optional) |

Limits of this evidence: three interviews (one student, one backend developer, one DevSecOps engineer) are a small sample,
so "supports" means "consistent with", not proven. Question 5 of the guide assumes the participant would want such a tool,
so support for E5 is weaker than the unprompted answers behind E4. None of the three participants regularly runs local
open-weight models, and #1 and #3 asked for hosted-API support; this challenges E3 and the non-goal "Proprietary hosted
models as evaluation targets" in the [proposal](project-proposal.md), and is an open question for the team and the supervisor.

## 5. How the evidence feeds requirements

Each confirmed or rejected statement in section 4 changes a requirement or its priority in
[requirements.md](requirements.md): E5 drives FR-09..FR-13, E6 drives NFR-04 and NFR-08.
