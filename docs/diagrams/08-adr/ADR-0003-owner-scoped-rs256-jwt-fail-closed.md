# ADR-0003 — Owner-scoped RS256 JWT via vendored service-auth; fail closed beyond loopback

- Status: accepted (retro-documented)

## Context

API อาจถูกเปิดนอก loopback (Docker image ตั้ง `AI_USAGE_API_HOST=0.0.0.0`) ข้อมูลเป็นของเจ้าของคนเดียว

## Decision

- ใช้สำเนา vendored ของ `bookchaowalit/platform-auth-sdk` ที่ `vendor/service-auth` ("do not edit here")
- ตรวจ JWT ด้วย public key ในเครื่อง: `alg=RS256` เท่านั้น ปฏิเสธ `jku/jwk/x5u/x5c/crit`, key ≥ 2048 bit, issuer ต้องเป็น `https://` origin, claims ครบ (`iss aud sub tenant_id scope iat nbf exp jti`), lifetime ≤ 120 s, `tenant_id=owner`, `sub` อยู่ใน allowlist, `scope=ai-usage:read`
- bind ที่ไม่ใช่ loopback → บังคับ `production`; ถ้า policy ไม่ ready → `parser.error` ไม่ยอม start
- static token (`AI_USAGE_API_TOKEN`) และการอ่านไม่ใช้ auth อนุญาตเฉพาะ development ที่ไม่ได้ตั้ง policy

## Evidence

- `vendor/service-auth/service_auth/__init__.py` (`AuthPolicy`, `authenticate`, `check_read_auth`)
- `vendor/service-auth/README.md`
- `server.py` `main` (non-loopback branch)
- `tests/test_server.py::test_remote_bind_requires_owner_auth_even_in_development`, `vendor/service-auth/tests/test_auth.py`
- `contracts/ai-usage.v1.md` (Routes และ authorization)

## Consequences

- `jti` ถูกตรวจรูปแบบแต่ไม่ได้เก็บกัน replay (ภายในอายุ ≤ 120 s token ใช้ซ้ำได้)
- vendored copy ต้อง sync เองเมื่อ SDK ต้นทางเปลี่ยน
