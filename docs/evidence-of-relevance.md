# 2. Evidence of Relevance

Author: Dias Mukhametkali. Status: draft v0.2, 2026-10-23. **Template with a plan; no interviews have been held yet.**

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
| 1 | TODO | TODO | TODO | TODO | TODO |
| 2 | TODO | TODO | TODO | TODO | TODO |
| 3 | TODO | TODO | TODO | TODO | TODO |

## 4. Verified findings vs assumptions

"Literature" means supported by a published study ([literature review](literature-review.md)). It is evidence for the problem,
not evidence that our users have it. "User-verified" is left empty until the interviews are done.

| ID | Statement | Basis | User-verified |
|---|---|---|---|
| E1 | LLM-generated code frequently contains vulnerabilities | Literature (Pearce et al., 2022; Fu et al., 2025) | n/a |
| E2 | Measured benefit of a security mitigation depends on the analyser | Literature (Alrashedy et al., 2025) | n/a |
| E3 | Teams run open-weight models locally for privacy reasons | **Assumption** (stated in the supervisor's justification letter) | TODO |
| E4 | Teams lack a ready tool to compare models by output security | **Assumption**; partly supported by [existing-systems comparison](existing-systems-comparison.md) | TODO |
| E5 | Users want a CWE-based report with a model ranking | **Assumption** | TODO |
| E6 | Users can run a Docker Compose stack with a GPU | **Assumption** | TODO |

## 5. How the evidence feeds requirements

Each confirmed or rejected statement in section 4 changes a requirement or its priority in
[requirements.md](requirements.md): E5 drives FR-09..FR-13, E6 drives NFR-04 and NFR-08.
