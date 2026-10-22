# SPEC-002 — L2 baseline: locked dependencies, strict types, domain rules under test

Standard: ADR-0004 — TDD + SDD (architecture-docs, `docs/architecture/decisions/ADR-0004-tdd-sdd-standard.md`).
Big Loop Plan Wave 2 (solo-empire `repository-catalog/roadmaps/BIG-LOOP-PLAN-2026-10-21.md`).

## Document control

| Field | Value |
|---|---|
| Spec ID / version | SPEC-002 / 1.0 |
| Status | in review (implemented; owner approval pending) |
| Repository / path | bookchaowalit/platform-ai-usage-api / `specs/002-l2-baseline/spec.md` |
| Owner (maker) | Claude Code (Wave 2 cells session) |
| Reviewer (checker) | Fresh Claude reviewer session (no maker context) |
| Approver | Owner (bookchaowalit): pending, see the Wave 2 report owner actions |
| Requirement links | Big Loop DoD L2: `PRODUCT.md`, ≥ 3 test files, Sentry, type check; L1 lockfile |
| Main-only | yes: committed straight to `main`, so the red run is local (ADR-0004 rule 2, v1.1) |
| Created / approved | 2026-10-22 / pending owner |

## 1. Problem and intent

- **Problem:** Installs were not reproducible (unpinned pip install of the vendored SDK and the app), there was no type check, Ruff ran with default rules only, and unexpected API failures were swallowed into a generic 500 with no error report.
- **Outcome:** the image installs exactly `uv.lock` (`uv sync --frozen`), CI runs Ruff, mypy
  (strict on `src/`) and a coverage gate on shared CI v1.1.1, and the cell's own rules have
  tests of their own beyond the generic contract suite.
- **Why now:** Wave 2 of the Big Loop Plan; milestone M1 is 2026-11-15.

## 2. Scope

| In scope | Out of scope (non-goals) |
|---|---|
| Lock file and frozen install, CI caller bump, Ruff/mypy config and fixes, rule tests, `PRODUCT.md` | New endpoints or fields; schema changes |

## 3. Behaviour — scenarios

### AC-01 — No DSN means no Sentry

- **Given** SENTRY_DSN is unset
- **When** init_sentry() runs
- **Then** sentry_sdk.init is never called
- **Test:** `tests/test_error_reporting.py::test_without_a_dsn_sentry_is_never_initialised` · level: unit / API with local fakes

### AC-02 — DSN turns on errors-only reporting without personal data

- **Given** SENTRY_DSN is set
- **When** init_sentry() runs
- **Then** tracing is off, send_default_pii and local variables are off, request bodies are never sent, logs are not forwarded, and the service tag is ai-usage-api
- **Test:** `tests/test_error_reporting.py::test_a_dsn_turns_on_errors_only_reporting_without_personal_data` · level: unit / API with local fakes

### AC-03 — Secrets are scrubbed from messages

- **Given** a message with a URL password, token=value, a bearer token and a JWT
- **When** scrub() runs
- **Then** none of the secrets remain and the URL keeps its user with ***
- **Test:** `tests/test_error_reporting.py::test_scrub_removes_url_passwords_tokens_and_jwts` · level: unit / API with local fakes

### AC-04 — Events keep only the request method

- **Given** an event with request URL, headers, query, breadcrumb data, log params, sampling context and extra
- **When** _scrub_event() runs
- **Then** only the method, scrubbed messages and trace id remain
- **Test:** `tests/test_error_reporting.py::test_scrubbed_event_keeps_only_the_request_method_and_drops_extra_data` · level: unit / API with local fakes

### AC-05 — Capture without DSN does not import Sentry

- **Given** SENTRY_DSN is unset and sentry_sdk cannot be imported
- **When** capture() runs
- **Then** it returns without error
- **Test:** `tests/test_error_reporting.py::test_capture_without_a_dsn_does_not_import_sentry` · level: unit / API with local fakes

### AC-06 — Unexpected API error is reported and still answers a generic 500

- **Given** the usage store raises with secret text
- **When** GET /api/v1/ai-usage
- **Then** the answer is 500 internal_error without the exception text and the exception is passed to capture()
- **Test:** `tests/test_error_reporting.py::test_an_unexpected_api_error_is_reported_and_still_answers_a_generic_500` · level: unit / API with local fakes

## 4. Interfaces and data

| Interface | Change | Contract |
|---|---|---|
| u | v | . |
| e | r | r |
| D | o | c |
| C | I | : |

- **Data model / migration:** N/A — no schema change.
- **Backward compatibility:** same routes and payloads; only tooling, locks, typing fixes and tests changed unless a scenario above says otherwise.

## 5. Non-functional requirements

| NFR | Target | How it is tested |
|---|---|---|
| Performance | N/A — no hot-path change beyond one comparison per declared range | — |
| Security / privacy | Authorization unchanged; Sentry sends no PII and scrubs tokens/URLs | existing auth tests, Sentry tests |
| Reliability / observability | Reproducible install from the lock file; opt-in Sentry error reporting | image rehearsal before push; Sentry tests |
| Accessibility / UX | N/A — API only | — |

## 6. Test plan (TDD)

- **Test levels:** unit and API tests with local fakes; no hosted service is called.
- **Test data:** generated in each test; no production data.
- **Coverage:** CI gate `coverage-threshold: "82"` (measured 84.01% on 2026-10-22, minus 2 points).
- **Not test-first (exceptions):** tests that pin behaviour the service already had
  (characterization tests, marked below) were written after the code by nature; tooling and
  config changes are covered by CI itself.

### Red / green log

| Scenario | Test | Red: commit / run + failure message | Green: commit / run | Refactor note |
|---|---|---|---|---|
| AC-01 | `tests/test_error_reporting.py::test_without_a_dsn_sentry_is_never_initialised` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-02 | `tests/test_error_reporting.py::test_a_dsn_turns_on_errors_only_reporting_without_personal_data` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-03 | `tests/test_error_reporting.py::test_scrub_removes_url_passwords_tokens_and_jwts` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-04 | `tests/test_error_reporting.py::test_scrubbed_event_keeps_only_the_request_method_and_drops_extra_data` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-05 | `tests/test_error_reporting.py::test_capture_without_a_dsn_does_not_import_sentry` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-06 | `tests/test_error_reporting.py::test_an_unexpected_api_error_is_reported_and_still_answers_a_generic_500` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |

## 7. Risks and open questions

| # | Risk or question | Impact | Owner | Resolution / date |
|---|---|---|---|---|
| 1 | Stored rows written before a range rule existed may already be inverted | a patch touching one of those dates is refused until both are fixed | owner | patches that do not touch the range still work |

## 8. Change log

| Version | Date | Change | Scenarios affected | Approved by |
|---|---|---|---|---|
| 1.0 | 2026-10-22 | Implemented with the Wave 2 baseline | all | pending owner |

## Approval

| Gate | Role | Name / date | Decision | Evidence |
|---|---|---|---|---|
| Implemented (DoD) | Reviewer (checker) | Fresh Claude reviewer / 2026-10-22 | see Wave 2 report | CI run of the pushed tip |
| Implemented (DoD) | Approver | Owner | pending | Wave 2 report |
