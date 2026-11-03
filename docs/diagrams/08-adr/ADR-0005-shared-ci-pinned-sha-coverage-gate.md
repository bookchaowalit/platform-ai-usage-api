# ADR-0005 — Shared CI workflows pinned by SHA, coverage gate 82% (ADR-0004 TDD + SDD pilot)

- Status: accepted (retro-documented)

## Context

repo นี้เป็น public และเป็น pilot แรกของ standard TDD + SDD (central ADR-0004)

## Decision

- `.github/workflows/ci.yml` เรียก reusable workflows `ci-python.yml` และ `security.yml` ของ `bookchaowalit/platform-ci-workflows` pin ที่ SHA `87dc5e1…` (v1.1.1) บน GitHub-hosted runner (default `ubuntu-24.04`)
- `coverage-threshold: "82"` (ratchet: measured 84.01% เมื่อ 2026-10-22, threshold = measured − 2), วัดเฉพาะ `server`, `model`, `collector`, `error_reporting`
- Renovate group update ของ `platform-ci-workflows`

## Evidence

- `.github/workflows/ci.yml`, `pyproject.toml` `[tool.coverage.run]`, `renovate.json`
- `specs/001-coverage-gate/spec.md` (red `e5b739e` / green `87f8b33`)
- Central: [ADR-0004 TDD + SDD standard](https://github.com/bookchaowalit/architecture-docs/blob/main/docs/architecture/decisions/ADR-0004-tdd-sdd-standard.md) (section "Pilot — platform-ai-usage-api")

## Consequences

- CI เป็น gate เดียว ไม่มี CD; branch `main` ไม่มี branch protection (GitHub API `branches/main/protection` ตอบ 404 "Branch not protected", 2026-11-03) จึงไม่บังคับ CI ก่อน merge
