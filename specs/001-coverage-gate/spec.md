---
title: "SPEC-001 — CI coverage gate (TDD + SDD pilot)"
status: implemented
tags: [spec, sdd, tdd, ci, coverage]
created: 2026-10-21
updated: 2026-10-21
description: "Turn on the platform-ci-workflows v1.1.0 coverage gate for this service as the first adopter of the TDD + SDD standard."
---

# SPEC-001 — CI coverage gate (TDD + SDD pilot)

Standard: ADR-0004 — TDD + SDD (`docs/architecture/decisions/ADR-0004-tdd-sdd-standard.md`).
Template: `templates/sdlc/feature-spec.md`. Both live in the owner's private `architecture-docs` repository.

## Document control

| Field | Value |
|---|---|
| Spec ID / version | SPEC-001 / 1.0 |
| Status | **implemented** (approved by owner 2026-10-21) |
| Repository / path | bookchaowalit/platform-ai-usage-api / `specs/001-coverage-gate/spec.md` |
| Owner (maker) | Claude Code |
| Reviewer (checker) | Fresh Claude reviewer session |
| Approver | Owner (bookchaowalit) |
| Requirement links | Owner request 2026-10-21 ("Pilot it on one repo first"); ADR-0004 rule 4 |
| Related docs | [platform-ci-workflows v1.1.0](https://github.com/bookchaowalit/platform-ci-workflows/releases/tag/v1.1.0) |
| Created / approved | 2026-10-21 / 2026-10-21 |

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

- **Requirement:** ADR-0004 rule 4 (threshold = current coverage rounded down)
- **Given** total coverage is 82.96% (shown as 83%)
- **When** CI runs with `coverage-threshold: "82"`
- **Then** the `api` job passes and the job summary shows the coverage table
- **Test:** CI run of commit "ci: coverage gate at 82 ..." · level: CI

### AC-03 — Only the service modules are measured

- **Requirement:** ADR-0004 rule 4
- **Given** `[tool.coverage.run] source = ["server", "model", "collector"]`
- **When** CI measures coverage
- **Then** the report lists exactly `server.py`, `model.py`, `collector.py` (no tests, no `vendor/`)
- **Test:** coverage table in the AC-02 run's job summary · level: CI

## 4. Interfaces and data

| Interface | Change | Contract |
|---|---|---|
| `.github/workflows/ci.yml` | changed | `ci-python.yml` / `security.yml` pinned to v1.1.1 (`87dc5e1`; was v1.1.0 `ff310ae`); `coverage-threshold: "82"` |
| `pyproject.toml` | changed | `[tool.coverage.run] source` |

- **Data model / migration:** N/A — no schema or runtime change.
- **Backward compatibility:** the service, its API and its container image are unchanged.

## 5. Non-functional requirements

| NFR | Target | How it is tested |
|---|---|---|
| Performance | CI `api` job time grows by under 30 s | Compare job durations before and after: 11 s on `main` (run 39098905250, 2026-10-18); 10–17 s across the 12 runs with the gate on 2026-10-21, so at most +6 s (GitHub API job timings, recorded in the owner's PRJ-TDD-01 evidence E-06) |
| Security / privacy | N/A — no data, secrets or permissions change | — |
| Reliability / observability | Gate fails closed when coverage data is missing (v1.1.0 behaviour) | Covered by the central self-test and local runs in platform-ci-workflows#2 |
| Accessibility / UX | N/A — no UI | — |

## 6. Test plan (TDD)

- **Test levels:** CI runs are the tests for this change (the change is CI configuration).
- **Test data:** the existing 68-test suite.
- **Coverage:** `coverage-threshold: "82"`; baseline 82.96% (collector 74%, model 97%, server 80%).
- **Not test-first (exceptions):** recorded in the change log (v0.2); **approved by the owner on 2026-10-21** (DoD exceptions table below):
  1. **Implementation before spec approval.** The red and green commits came after the spec commit but before owner approval, because ADR-0004 itself was still `proposed` and the owner asked for the pilot directly. The owner approved the spec and the implementation together after PR #3 merged (2026-10-21).
  2. **AC-03 has no red run.** Scoping (`[tool.coverage.run] source`) landed in the same commit as the threshold-90 run, so no run shows tests or `vendor/` being measured. Replacement check: the green run's report lists exactly the three modules.
  3. **The red commit contains configuration as well as the "test".** For a config-only change the CI run is the test, so the pin and scoping ship with the first run.

### Red / green log

| Scenario | Test | Red: commit / run + failure message | Green: commit / run | Refactor note |
|---|---|---|---|---|
| AC-01 | CI `api` job, threshold 90 | `e5b739e` / [run](https://github.com/bookchaowalit/platform-ai-usage-api/actions/runs/39534812491/job/119008892655) · `Total coverage is below the 90% threshold` (TOTAL 751 stmts, 128 miss, 83%; 68 tests passed) | — (expected red: the scenario is the failure) | none |
| AC-02 | CI `api` job, threshold 82 | `e5b739e` / [run](https://github.com/bookchaowalit/platform-ai-usage-api/actions/runs/39534812491/job/119008892655) (same build and data, gate fails at 90) | `87f8b33` / [run](https://github.com/bookchaowalit/platform-ai-usage-api/actions/runs/39535338340/job/119010573412) · TOTAL 83% (82.96) ≥ 82; also green at 80 in `ec4242e` | none |
| AC-03 | AC-02 job summary | — (exception 2) | `87f8b33` / [run](https://github.com/bookchaowalit/platform-ai-usage-api/actions/runs/39535338340/job/119010573412) · report lists only `collector.py`, `model.py`, `server.py` | none |

### DoD exceptions

| Item | Criterion waived | Reason | Approved by | Follow-up |
|---|---|---|---|---|
| SPEC-001 | Spec approved before any implementation commit (DoR) | Pilot of a standard that was itself still `proposed`; owner asked for the pilot directly | Owner (bookchaowalit) / 2026-10-21 | None; later specs are approved before code |
| SPEC-001 AC-03 | Red run before green (test-first) | Coverage scoping shipped in the first CI run; replacement check: the green run's report lists exactly the three modules | Owner (bookchaowalit) / 2026-10-21 | None |
| SPEC-001 | Red commit contains only the test | Config-only change: the CI run is the test, so the pin and scoping ship with it | Owner (bookchaowalit) / 2026-10-21 | None |

## 7. Risks and open questions

| # | Risk or question | Impact | Owner | Resolution / date |
|---|---|---|---|---|
| 1 | `collector.py` is at 74%, so new collector code can lower the total while staying above 80% | Coverage drifts down toward the floor | Owner | Follow-up spec: tests for collector, then raise the threshold |

## 8. Change log

| Version | Date | Change | Scenarios affected | Approved by |
|---|---|---|---|---|
| 0.1 | 2026-10-21 | First draft | all | — |
| 0.2 | 2026-10-21 | Threshold 80 → 82 after ADR-0004 dropped the 80% cap; exceptions 1–3 recorded after the independent review | AC-02, AC-03 | Owner / 2026-10-21 |
| 1.0 | 2026-10-21 | Approved by owner with exceptions 1–3; status implemented (PR #3 merged) | all | Owner / 2026-10-21 |
| 1.0.1 | 2026-10-21 | Pin bumped to platform-ci-workflows v1.1.1: the v1.1.0 Python gate compared rounded coverage (79.5% passed 80%). No scope or behaviour change for this repo (82.96% vs 82 passes either way), so no re-approval | AC-01, AC-02 | not required (dependency fix) |
| 1.0.2 | 2026-10-21 | Evidence correction: CI time with the gate is 10–17 s over 12 runs (was "11–14 s", copied from two runs). Wording only; result unchanged (< 30 s) | NFR performance row | not required (evidence correction) |

## Approval

| Gate | Role | Name / date | Decision | Evidence |
|---|---|---|---|---|
| Spec ready (before code, DoR) | Reviewer (checker) | Fresh Claude reviewer session / 2026-10-21 | revise → fixed in v0.2 (1 blocking: missing exception record; 3 non-blocking) | PR #3 description |
| Spec ready (before code, DoR) | Approver | Owner (bookchaowalit) / 2026-10-21 | **approve** (after implementation, exception 1) | Owner message in the Claude Code session, 2026-10-21: "Approve ADR-0004 (G6) and the 3 exceptions in SPEC-001." |
| Implemented (DoD) | Reviewer (checker) | Fresh Claude reviewer session / 2026-10-21 | pass: config correct, red before green, evidence recorded | [PR #3](https://github.com/bookchaowalit/platform-ai-usage-api/pull/3), [green run](https://github.com/bookchaowalit/platform-ai-usage-api/actions/runs/39535338340/job/119010573412) |
| Implemented (DoD) | Approver | Owner (bookchaowalit) / 2026-10-21 | **approve** with DoD exceptions 1–3 | Same owner message; [PR #3](https://github.com/bookchaowalit/platform-ai-usage-api/pull/3) |
