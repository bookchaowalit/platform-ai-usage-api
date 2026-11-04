# 05 — C4 Context

```mermaid
C4Context
  title ai-usage system context
  Person(owner, "Owner", "Runs collector.py in a terminal, sets fees and business numbers")
  System(aiusage, "ai-usage", "collector.py CLI and server.py read-only API on the owner machine")
  System_Ext(claude, "Claude Code", "Status line callback JSON on stdin")
  System_Ext(codex, "Codex CLI app-server", "Local JSON-RPC over stdio, account/rateLimits/read")
  System_Ext(dash, "Dashboard client", "owner-web, reads GET /api/v1/ai-usage")
  System_Ext(issuer, "JWT issuer", "Issues owner-scoped RS256 tokens, public key configured locally")
  System_Ext(sentry, "Sentry", "Errors only, opt-in via SENTRY_DSN")
  Rel(owner, aiusage, "status, install-claude, configure-*")
  Rel(claude, aiusage, "statusLine JSON")
  Rel(aiusage, codex, "spawn and JSON-RPC")
  Rel(dash, aiusage, "HTTP GET JSON")
  Rel(issuer, dash, "token")
  Rel(aiusage, sentry, "exceptions, scrubbed")
```

ผู้ใช้หลักคือเจ้าของคนเดียว ระบบไม่ติดต่อ provider cloud API ตรง ๆ: Claude ส่งข้อมูลเข้ามาเอง (stdin) และ Codex อ่านผ่าน CLI ที่ล็อกอินอยู่แล้ว JWT ตรวจด้วย public key ในเครื่อง (ไม่เรียก issuer ทาง network)

Sources: `README.md`, `PRODUCT.md` (Users, Operating Context), `collector.py` (`ingest_claude`, `read_codex`), `server.py`, `vendor/service-auth/service_auth/__init__.py` (`AuthPolicy.from_env`, local `load_pem_public_key`), `error_reporting.py`, `docs/OWNER.th.md`

## Open questions

- Dashboard client ที่ใช้งานจริง: `owner-web` (`docs/OWNER.th.md`); relay `ai-usage-display` ไม่ได้อ่าน API นี้ แต่รับ snapshot ที่ `platform-ai-usage-display` push ไป (ดู 16-deployment)
- Sentry DSN ตั้งไว้กับ local units หรือไม่ (PRODUCT.md `[ต้องยืนยัน]`)
