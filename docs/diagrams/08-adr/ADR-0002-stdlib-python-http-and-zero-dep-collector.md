# ADR-0002 — Python standard library: zero-dependency collector, stdlib HTTP server

- Status: accepted (retro-documented)

## Context

collector ต้องรันได้ทันทีหลัง `git clone` บนเครื่องใดก็ได้ที่มี Python 3.11+

## Decision

- `collector.py` ใช้ standard library เท่านั้น (ไม่ import `error_reporting`)
- `server.py` ใช้ `http.server.ThreadingHTTPServer` + `BaseHTTPRequestHandler` (ไม่มี web framework); dependency runtime มีแค่ `solo-empire-service-auth` (vendored, PyJWT[crypto]) และ `sentry-sdk`
- dependency ล็อกด้วย `uv.lock` และติดตั้งแบบ `uv sync --frozen` ทั้งใน CI และ Dockerfile

## Evidence

- `README.md` ("Zero dependencies. The collector is a single Python 3.11+ file")
- `pyproject.toml` (`requires-python = ">=3.11"`, dependencies, comment "collector.py stays standard-library only")
- `server.py` imports; `error_reporting.py` docstring ("collector.py does not use this module")
- `Dockerfile` (`uv sync --frozen --no-dev`), `.github/workflows/ci.yml` comment, `specs/002-l2-baseline/spec.md`

## Consequences

- ไม่มี request timeout / rate limit / TLS ใน server เอง; พึ่ง loopback bind
- access log ถูกปิด (`log_message` return) จึงไม่มี request log
