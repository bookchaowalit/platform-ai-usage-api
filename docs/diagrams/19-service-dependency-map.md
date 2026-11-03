# 19 — Service dependency map

```mermaid
flowchart LR
  subgraph Runtime_local["Runtime on owner machine"]
    API["server.py"]
    COL["collector.py"]
    ST[("State dir JSON")]
    CX["codex CLI app-server"]
    CC["Claude Code"]
    SD["systemd user manager"]
  end
  subgraph Libraries
    SA["solo-empire-service-auth 0.1.0, vendored from platform-auth-sdk"]
    JWT["PyJWT crypto >=2.10.1,<3"]
    SS["sentry-sdk >=2.72,<3"]
    PY["Python 3.11+ stdlib"]
  end
  subgraph External
    SEN["Sentry, optional"]
    DASH["Dashboard consumer: owner-web or ai-usage-display relay"]
  end
  subgraph Build_time["Build and CI"]
    GH["GitHub Actions"]
    PCW["platform-ci-workflows @87dc5e1 v1.1.1"]
    UV["uv and uv.lock"]
    IMG["python:3.12-slim and ghcr.io/astral-sh/uv:0.13.1"]
    REN["Renovate"]
  end
  SD --> API
  SD --> COL
  API --> SA
  SA --> JWT
  API --> SS
  SS -.-> SEN
  API --> ST
  COL --> PY
  COL --> ST
  COL --> CX
  CC --> COL
  DASH --> API
  GH --> PCW
  PCW --> UV
  IMG --> UV
  REN --> PCW
```

| Dependency | Kind | Required? | Failure effect |
|---|---|---|---|
| State dir | local files | yes | missing → `not_connected`; unreadable → `error`; `/ready` 503 only if `snapshot()` raises |
| codex CLI | subprocess | for Codex data | `codex_not_installed` / `unavailable`; snapshot ages to `stale` |
| Claude Code status line | inbound callback | for Claude data | no refresh → `stale` after 900 s |
| service-auth / PyJWT | library | for API | import failure → API won't start |
| sentry-sdk | library | imported only if `SENTRY_DSN` | none when unset |
| platform-ci-workflows | CI | for CI only | CI fails, runtime unaffected |

Sources: `pyproject.toml`, `uv.lock` (present), `vendor/service-auth/pyproject.toml`, `vendor/service-auth/README.md`, `server.py`, `collector.py`, `model.py`, `error_reporting.py`, `Dockerfile`, `.github/workflows/ci.yml`, `renovate.json`, `systemd/*.service`, `PRODUCT.md`, `docs/OWNER.th.md`
