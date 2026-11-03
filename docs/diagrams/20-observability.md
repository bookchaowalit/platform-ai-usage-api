# 20 — Observability

```mermaid
flowchart LR
  subgraph API_proc["server.py"]
    E1["Unexpected exception in handle"] --> CAP["capture: no-op unless SENTRY_DSN"]
    BOOT["Startup prints running on host:port; sentry enabled line to stderr"]
    HL["/health liveness"]
    RD["/ready status, source, auth"]
    PS["providers[].status and collected_at in /api/v1/ai-usage"]
    NOLOG["Access log disabled: log_message returns"]
  end
  subgraph COL_proc["collector.py codex loop"]
    JL["stdout JSON line: status collected or unavailable"]
  end
  CAP -.->|"scrubbed, errors only, tag service ai-usage-api"| SEN["Sentry"]
  BOOT --> JR["systemd journal (default stdout capture)"]
  JL --> JR
  HL --> DH["Docker HEALTHCHECK hits /ready every 15 s, image only"]
  PS --> DASH["Dashboard shows stale / not_connected"]
  ST["collector.py status: stale marker over 15 min"] --> OWN["Owner"]
  DASH --> OWN
  JR --> OWN
```

| Signal | Source | Watched by |
|---|---|---|
| Errors (500 path) | `error_reporting.capture` | Sentry, only when `SENTRY_DSN` set (unknown for local units) |
| Liveness / readiness | `/health`, `/ready` | Docker `HEALTHCHECK` (image only); **no uptime monitor targets this API** (PRODUCT.md Measures) |
| Data freshness | `providers[].status` (`stale` > 900 s), `summary.connected` | dashboard / owner |
| Collector success | stdout JSON lines | systemd journal (no alert) |
| CI health | GitHub Actions `CI` | GitHub UI |

- ไม่มี metrics, tracing (`traces_sample_rate=None`), structured request logs, heartbeat หรือ PostHog ใน repo นี้
- PRODUCT.md: `platform-uptime-worker` watches only the `ai-usage-display` relay, not this API

Sources: `server.py`, `error_reporting.py`, `collector.py` (`main` loop prints, `render_status`), `model.py` (`STALE_SECONDS`), `vendor/service-auth/service_auth/__init__.py` (`readiness`), `Dockerfile` (`HEALTHCHECK`), `systemd/*.service`, `PRODUCT.md` (Measures)

## Open questions

- Sentry project / DSN สำหรับ ai-usage-api มีหรือไม่ (PRODUCT.md `[ต้องยืนยัน]`)
- ต้องการ alert เมื่อ collector `unavailable` ต่อเนื่องหรือไม่
