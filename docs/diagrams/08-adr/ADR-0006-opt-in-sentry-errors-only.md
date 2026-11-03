# ADR-0006 — Opt-in Sentry, errors only, scrubbed

- Status: accepted (retro-documented)

## Decision

`error_reporting.init_sentry()` เป็น no-op ถ้าไม่มี `SENTRY_DSN`; เมื่อเปิด: `traces_sample_rate=None`, `send_default_pii=False`, `include_local_variables=False`, `max_request_body_size="never"`, `before_send=_scrub_event` (เหลือแค่ request method, scrub URL password / token / bearer / JWT), ปิด logging integration, tag `service=ai-usage-api` ใช้เฉพาะ `server.py`; `capture()` ถูกเรียกเฉพาะใน 500 branch

## Evidence

- `error_reporting.py`, `server.py` (`init_sentry()` ใน `main`, `capture(exc)` ใน `handle`)
- `tests/test_error_reporting.py`, `specs/002-l2-baseline/spec.md` AC-01…AC-06

## Consequences

- collector ไม่มี error reporting เลย (stdout JSON line เท่านั้น)
- ไม่ทราบว่า local units ตั้ง DSN หรือไม่ (PRODUCT.md `[ต้องยืนยัน]`)
