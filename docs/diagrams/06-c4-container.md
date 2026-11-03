# 06 — C4 Container

```mermaid
C4Container
  title ai-usage containers on the owner machine
  Person(owner, "Owner")
  System_Ext(claude, "Claude Code")
  System_Ext(codex, "Codex CLI app-server")
  System_Ext(dash, "Dashboard client")
  System_Ext(sentry, "Sentry")
  System_Boundary(host, "Owner machine, systemd user session") {
    Container(collector, "collector.py", "Python 3.11+ stdlib", "CLI: status, codex poll, claude-statusline, install-claude, configure-*")
    Container(api, "server.py", "Python ThreadingHTTPServer, PyJWT, sentry-sdk", "Read-only API on 127.0.0.1:3520")
    ContainerDb(state, "State dir", "JSON files", "claude.json, codex.json, settings.json in AI_USAGE_STATE_DIR")
    Container(csettings, "Claude settings", "JSON file", ".claude/settings.local.json statusLine command")
  }
  Rel(owner, collector, "runs")
  Rel(claude, collector, "stdin JSON via statusLine command")
  Rel(collector, codex, "subprocess JSON-RPC stdio")
  Rel(collector, state, "atomic write 0600")
  Rel(collector, csettings, "install-claude writes")
  Rel(api, state, "read only, no symlinks, max 1 MiB")
  Rel(dash, api, "GET /api/v1/ai-usage")
  Rel(api, sentry, "capture if SENTRY_DSN")
```

Optional container: `Dockerfile` สร้าง image `python:3.12-slim` (`AI_USAGE_API_HOST=0.0.0.0`, `AI_USAGE_API_ENV=production`, state `/app/state` mount read-only) แต่ `service.yaml` `deploy.target: unassigned` จึงไม่ได้วาดเป็น container ที่รันอยู่

Sources: `systemd/solo-ai-usage-api.service`, `systemd/solo-ai-usage-collector.service`, `server.py`, `collector.py`, `model.py` (`read_snapshot`, `default_state_dir`), `pyproject.toml`, `Dockerfile`, `service.yaml`, `error_reporting.py`

## Open questions

- Docker image รันที่ไหนหรือไม่ (PRODUCT.md `[ต้องยืนยัน]`)
