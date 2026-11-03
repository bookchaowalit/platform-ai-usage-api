# 10 — Sequences

## S1 — Dashboard reads usage (production JWT path)

```mermaid
sequenceDiagram
  autonumber
  participant D as Dashboard client
  participant H as AiUsageRequestHandler
  participant A as AiUsageApi.handle
  participant AU as service_auth
  participant S as UsageStore
  participant F as State dir files
  D->>H: GET /api/v1/ai-usage with Origin and Bearer JWT
  H->>H: Origin in allowlist?
  alt origin not allowed
    H-->>D: 403 origin_not_allowed
  else allowed or no Origin
    H->>A: handle(method, path, headers)
    A->>AU: check_read_auth(policy, headers, environment, token)
    AU->>AU: verify RS256, iss, aud, claims, lifetime, tenant, sub, scope
    alt invalid
      AU-->>A: AuthError 401 / 403 / 503
      A-->>H: error JSON
    else valid
      A->>S: snapshot()
      S->>F: read settings.json, claude.json, codex.json (O_NOFOLLOW, max 1 MiB)
      F-->>S: JSON or missing
      S->>S: project providers, alerts, subscriptions, ROI
      S-->>A: payload
      A-->>H: 200
    end
    H-->>D: JSON, Cache-Control no-store, ACAO origin
  end
```

## S2 — Claude status-line ingest

```mermaid
sequenceDiagram
  autonumber
  participant CC as Claude Code
  participant C as collector.py claude-statusline
  participant F as claude.json
  participant P as Passthrough command
  CC->>C: statusLine JSON on stdin (max 1 MiB)
  C->>C: claude_snapshot keeps rate_limits.five_hour, seven_day, cost.total_cost_usd
  alt windows not empty
    C->>F: atomic_json write
  else no rate_limits
    C->>C: keep old snapshot timestamp
  end
  alt passthrough configured
    C->>P: run existing statusLine command with same stdin, timeout 5 s
    P-->>CC: its own status line text
  else no passthrough
    C-->>CC: "Claude · 5-hour N% left · weekly N% left"
  end
```

## S3 — Codex collection (systemd poll every 300 s)

```mermaid
sequenceDiagram
  autonumber
  participant SD as systemd collector unit
  participant C as collector.py codex
  participant X as codex app-server --stdio
  participant F as codex.json
  SD->>C: start --interval 300
  loop every interval
    C->>X: spawn with analytics.enabled=false, mcp_servers empty
    C->>X: initialize (clientInfo solo_ai_usage)
    X-->>C: result id 1
    C->>X: initialized
    C->>X: account/rateLimits/read excludeResetCreditDetails true
    X-->>C: result id 2 rateLimits
    alt ok within 20 s and 1 MiB
      C->>F: atomic_json codex_snapshot
      C->>SD: stdout status collected
    else error, timeout, closed
      C->>SD: stdout status unavailable
    end
    C->>X: SIGTERM process group, SIGKILL after 2 s
  end
```

Sources: `server.py` (`_dispatch`, `handle`, `_write`), `vendor/service-auth/service_auth/__init__.py`, `model.py` (`UsageStore.snapshot`, `read_snapshot`), `collector.py` (`ingest_claude`, `claude_snapshot`, `read_codex`, `rpc_result`, `main` loop), `systemd/solo-ai-usage-collector.service`
