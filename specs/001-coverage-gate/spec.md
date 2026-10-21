---
title: "SPEC-001 — CI coverage gate (TDD + SDD pilot)"
status: in review
tags: [spec, sdd, tdd, ci, coverage]
created: 2026-10-21
updated: 2026-10-21
description: "Turn on the platform-ci-workflows v1.1.0 coverage gate for this service as the first adopter of the TDD + SDD standard."
---

# SPEC-001 — CI coverage gate (TDD + SDD pilot)

Standard: [ADR-0004 — TDD + SDD](https://github.com/bookchaowalit/architecture-docs/blob/main/docs/architecture/decisions/ADR-0004-tdd-sdd-standard.md).
Template: [feature-spec.md](https://github.com/bookchaowalit/architecture-docs/blob/main/templates/sdlc/feature-spec.md).

## Document control

| Field | Value |
|---|---|
| Spec ID / version | SPEC-001 / 0.1 |
| Status | in review |
| Repository / path | bookchaowalit/platform-ai-usage-api / `specs/001-coverage-gate/spec.md` |
| Owner (maker) | Claude Code |
| Reviewer (checker) | Fresh Claude reviewer session |
| Approver | Owner (bookchaowalit) |
| Requirement links | Owner request 2026-10-21 ("Pilot it on one repo first"); ADR-0004 rule 4 |
| Related docs | [platform-ci-workflows v1.1.0](https://github.com/bookchaowalit/platform-ci-workflows/releases/tag/v1.1.0) |
| Created / approved | 2026-10-21 / pending |

## 1. Problem and intent

- **Problem:** CI ran 68 tests but measured no coverage, so a change could delete tests or add untested code and still pass.
- **Outcome:** CI fails when total coverage of `server`, `model` and `collector` drops below the threshold, and every run shows the coverage table in the job summary.
- **Why now:** this repository is the pilot for ADR-0004 before other repositories adopt it.

## 2. Scope

| In scope | Out of scope (non-goals) |
|---|---|
| Pin the shared workflows to v1.1.0; turn on `coverage-threshold`; scope coverage to the three service modules | Writing new tests to raise coverage (follow-up spec); changing service behaviour; the vendored `service-auth` package's coverage |

## 3. Behaviour — scenarios

### AC-01 — Coverage below the threshold fails CI

- **Requirement:** ADR-0004 rule 4
- **Given** total coverage of the service modules is 83%
- **When** CI runs with `coverage-threshold: "90"`
- **Then** the `api` job fails with "Total coverage is below the 90% threshold"
- **Test:** CI run of commit "ci: coverage gate at 90 (red)" · level: CI

### AC-02 — Coverage at or above the threshold passes CI

- **Requirement:** ADR-0004 rule 4 (start at current coverage rounded down, at most 80)
- **Given** total coverage is 83%
- **When** CI runs with `coverage-threshold: "80"`
- **Then** the `api` job passes and the job summary shows the coverage table
- **Test:** CI run of commit "ci: coverage gate at 80 (green)" · level: CI

### AC-03 — Only the service modules are measured

- **Requirement:** ADR-0004 rule 4
- **Given** `[tool.coverage.run] source = ["server", "model", "collector"]`
- **When** CI measures coverage
- **Then** the report lists exactly `server.py`, `model.py`, `collector.py` (no tests, no `vendor/`)
- **Test:** coverage table in the AC-02 run's job summary · level: CI

## 4. Interfaces and data

| Interface | Change | Contract |
|---|---|---|
| `.github/workflows/ci.yml` | changed | `ci-python.yml` / `security.yml` pinned to v1.1.0 (`ff310ae`); `coverage-threshold: "80"` |
| `pyproject.toml` | changed | `[tool.coverage.run] source` |

- **Data model / migration:** N/A — no schema or runtime change.
- **Backward compatibility:** the service, its API and its container image are unchanged.

## 5. Non-functional requirements

| NFR | Target | How it is tested |
|---|---|---|
| Performance | CI `api` job time grows by under 30 s | Compare job durations before and after: 11 s on `main` (2026-10-18) and 11 s with the gate |
| Security / privacy | N/A — no data, secrets or permissions change | — |
| Reliability / observability | Gate fails closed when coverage data is missing (v1.1.0 behaviour) | Covered by the central self-test and local runs in platform-ci-workflows#2 |
| Accessibility / UX | N/A — no UI | — |

## 6. Test plan (TDD)

- **Test levels:** CI runs are the tests for this change (the change is CI configuration).
- **Test data:** the existing 68-test suite.
- **Coverage:** `coverage-threshold: "80"`; baseline 83% (collector 74%, model 97%, server 80%).
- **Not test-first (exceptions):** none. The red run (AC-01) is recorded before the green run (AC-02).

### Red / green log

| Scenario | Test | Red: commit / run + failure message | Green: commit / run | Refactor note |
|---|---|---|---|---|
| AC-01 | CI `api` job, threshold 90 | `e5b739e` / [run](https://github.com/bookchaowalit/platform-ai-usage-api/actions/runs/39534812491/job/119008892655) · `Total coverage is below the 90% threshold` (TOTAL 751 stmts, 128 miss, 83%; 68 tests passed) | — (expected red: the scenario is the failure) | none |
| AC-02 | CI `api` job, threshold 80 | `e5b739e` / [run](https://github.com/bookchaowalit/platform-ai-usage-api/actions/runs/39534812491/job/119008892655) (same build and data, gate fails at 90) | `ec4242e` / [run](https://github.com/bookchaowalit/platform-ai-usage-api/actions/runs/39534900412/job/119009178033) · TOTAL 83% ≥ 80 | none |
| AC-03 | AC-02 job summary | — | `ec4242e` / [run](https://github.com/bookchaowalit/platform-ai-usage-api/actions/runs/39534900412/job/119009178033) · report lists only `collector.py`, `model.py`, `server.py` | none |

## 7. Risks and open questions

| # | Risk or question | Impact | Owner | Resolution / date |
|---|---|---|---|---|
| 1 | `collector.py` is at 74%, so new collector code can lower the total while staying above 80% | Coverage drifts down toward the floor | Owner | Follow-up spec: tests for collector, then raise the threshold |

## 8. Change log

| Version | Date | Change | Scenarios affected | Approved by |
|---|---|---|---|---|
| 0.1 | 2026-10-21 | First draft | all | — |

## Approval

| Gate | Role | Name / date | Decision | Evidence |
|---|---|---|---|---|
| Spec ready (before code, DoR) | Reviewer (checker) | [Fresh Claude reviewer / 2026-10-21] | [pass / revise] | [PR comment] |
| Spec ready (before code, DoR) | Approver | Owner / pending | pending | — |
| Implemented (DoD) | Reviewer (checker) | [Fresh Claude reviewer / 2026-10-21] | [pass / revise] | [PR URL, CI run URL] |
