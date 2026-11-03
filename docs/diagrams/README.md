# Core 22 SDLC diagram pack — platform-ai-usage-api

ชุด diagram 22 รายการตาม SDLC Diagram Catalog v2 (knowledge-base `knowledge/tech/core-cs/sdlc-diagram-catalog.md`) วาดจาก code / config ของ repo นี้ที่ `origin/main` `b4881fa` (2026-10-22)

repo นี้คือ **ai-usage**: `collector.py` (CLI standard library เท่านั้น อ่านโควตา Claude ผ่าน status line และ Codex ผ่าน local app-server) + `server.py` (HTTP API read-only บน `127.0.0.1:3520`) รันเป็น systemd user units บนเครื่องเจ้าของ ไม่มี hosted deploy (`service.yaml` `deploy.target: unassigned`) และไม่มี database (JSON snapshot 3 ไฟล์) ทุก diagram มี `Sources:` และ "Open questions" แยกไว้

| # | Item | Status | File | Sources read |
|---|---|---|---|---|
| 01 | Business process (As-Is / To-Be) | done (To-Be = out-of-scope list + open question) | [01-business-process.md](01-business-process.md) | collector.py, server.py, model.py, systemd/, PRODUCT.md, contract, specs/ |
| 02 | Use cases | done | [02-use-cases.md](02-use-cases.md) | collector.py, server.py, service_auth, systemd/, contract |
| 03 | User flows (CLI + HTTP; no UI) | done | [03-user-flows.md](03-user-flows.md) | collector.py, server.py, service_auth, README.md |
| 04 | Traceability (RTM) | done | [04-traceability.md](04-traceability.md) | PRODUCT.md, contract, specs/001, specs/002, code, tests/, ci.yml |
| 05 | C4 Context | done | [05-c4-context.md](05-c4-context.md) | README.md, PRODUCT.md, collector.py, server.py, service_auth, OWNER.th.md |
| 06 | C4 Container | done | [06-c4-container.md](06-c4-container.md) | systemd/, server.py, collector.py, model.py, Dockerfile, service.yaml |
| 07 | C4 Component | done | [07-c4-component.md](07-c4-component.md) | server.py, model.py, error_reporting.py, service_auth, collector.py |
| 08 | ADRs (6) | done | [08-adr/](08-adr/) | systemd/, service.yaml, pyproject.toml, Dockerfile, service_auth, model.py, collector.py, ci.yml, error_reporting.py, specs/ |
| 09 | ERD | done (JSON document model; no DB) | [09-erd.md](09-erd.md) | collector.py, model.py, contract |
| 10 | Sequences | done (3) | [10-sequences.md](10-sequences.md) | server.py, service_auth, model.py, collector.py, systemd unit |
| 11 | State machines | done (4) | [11-state-machines.md](11-state-machines.md) | model.py, service_auth `readiness`, contract |
| 12 | API and integrations | reused + extended | [12-api-integration.md](12-api-integration.md) → [`contracts/ai-usage.v1.md`](../../contracts/ai-usage.v1.md) | server.py, collector.py, error_reporting.py, service_auth, contract |
| 13 | Threat model (DFD + STRIDE) | done | [13-threat-model.md](13-threat-model.md) | server.py, service_auth, model.py, collector.py, error_reporting.py, ci.yml, shared security.yml, gh branch protection API |
| 14 | Backup / DR | done (no backup exists; RTO/RPO not defined) | [14-backup-dr.md](14-backup-dr.md) | model.py, collector.py, service.yaml, ci.yml, OWNER.th.md |
| 15 | CI/CD pipeline | done (CI only, no CD) | [15-cicd-pipeline.md](15-cicd-pipeline.md) | ci.yml, platform-ci-workflows @87dc5e1, renovate.json, gh run view |
| 16 | Deployment | done (local systemd; Docker image optional, not deployed) | [16-deployment.md](16-deployment.md) | systemd/, OWNER.th.md, service.yaml, Dockerfile, server.py, PRODUCT.md |
| 17 | Test coverage matrix | done | [17-test-coverage-matrix.md](17-test-coverage-matrix.md) | tests/*.py, vendor/service-auth/tests, ci.yml, pyproject.toml |
| 18 | Git / release workflow | done | [18-git-release-workflow.md](18-git-release-workflow.md) | git log, gh pr list, gh branch protection / rulesets API, OWNER.th.md, SPEC-002 |
| 19 | Service dependency map | done | [19-service-dependency-map.md](19-service-dependency-map.md) | pyproject.toml, vendor/service-auth, code, Dockerfile, ci.yml, renovate.json |
| 20 | Observability | done (Sentry opt-in, health endpoints; no monitor) | [20-observability.md](20-observability.md) | server.py, error_reporting.py, collector.py, Dockerfile, PRODUCT.md |
| 21 | Incident response | done (manual detection; no alert channel) | [21-incident-response.md](21-incident-response.md) | OWNER.th.md, collector.py, server.py, contract, gh run list / view |
| 22 | DORA | done (proxies; no recorded deploys) | [22-dora.md](22-dora.md) | git log, gh pr list, gh run list |

## ADRs

- [ADR-0001](08-adr/ADR-0001-local-first-systemd-loopback.md) Local-first: systemd user units บน loopback, ไม่มี hosted deploy
- [ADR-0002](08-adr/ADR-0002-stdlib-python-http-and-zero-dep-collector.md) Python stdlib: collector ไม่มี dependency, HTTP server stdlib
- [ADR-0003](08-adr/ADR-0003-owner-scoped-rs256-jwt-fail-closed.md) Owner-scoped RS256 JWT (vendored service-auth), fail closed นอก loopback
- [ADR-0004](08-adr/ADR-0004-file-snapshots-not-database.md) JSON snapshot files แทน database
- [ADR-0005](08-adr/ADR-0005-shared-ci-pinned-sha-coverage-gate.md) Shared CI pin SHA + coverage gate 82%
- [ADR-0006](08-adr/ADR-0006-opt-in-sentry-errors-only.md) Sentry opt-in, errors only, scrubbed

## Related docs (reused, not copied)

- [`contracts/ai-usage.v1.md`](../../contracts/ai-usage.v1.md) — API v1 contract (field reference)
- [`PRODUCT.md`](../../PRODUCT.md), [`docs/OWNER.th.md`](../OWNER.th.md), [`README.md`](../../README.md)
- [`specs/001-coverage-gate/spec.md`](../../specs/001-coverage-gate/spec.md), [`specs/002-l2-baseline/spec.md`](../../specs/002-l2-baseline/spec.md)
- Central: [ADR-0004 TDD + SDD standard](https://github.com/bookchaowalit/architecture-docs/blob/main/docs/architecture/decisions/ADR-0004-tdd-sdd-standard.md) (this repo is the pilot)

## Open questions for the owner (รวม)

1. Dashboard / relay ที่อ่าน API จริง: `owner-web` หรือ `ai-usage-display` บน Railway และ relay เข้าถึง API ที่ bind loopback อย่างไร (01, 05, 12, 16)
2. Sentry DSN ตั้งให้ local units หรือไม่ (05, 20)
3. Docker image รันที่ไหนหรือไม่ (06, 16)
4. JWT issuer จริงและมี client ใช้ production mode หรือไม่ (02, 12)
5. Backup ของ `settings.json` และ RTO / RPO (14)
6. วิธี / ความถี่ update local checkout หลัง merge; ไม่มีบันทึก deploy จึงคำนวณ DORA จริงไม่ได้ (18, 22)
7. Alert เมื่อ collector unavailable / snapshot stale, และที่เก็บ postmortem (20, 21)
8. SPEC-002 approval ค้างและตาราง §4 เสีย; `specs/README.md` ไม่ list SPEC-002 (04)
9. Hardening ถ้าจะเปิดนอก loopback: `jti` replay cache, rate limit, branch protection บน `main` (13)
10. To-Be: collector ของ Gemini / Grok / Muse หรือ billed API spend (01)
