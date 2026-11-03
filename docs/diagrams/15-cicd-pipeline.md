# 15 — CI/CD pipeline

workflow เดียว: `.github/workflows/ci.yml` (name `CI`) เรียก reusable workflows ของ `bookchaowalit/platform-ci-workflows` pin SHA `87dc5e1c…` (v1.1.1) runner default `"ubuntu-24.04"` (GitHub-hosted, public repo) ไม่มี CD job

```mermaid
flowchart TD
  T1["push to main"] --> CI["workflow CI, permissions contents read, concurrency ci-ref cancel-in-progress"]
  T2["pull_request"] --> CI
  T3["workflow_dispatch"] --> CI
  CI --> API["job api: ci-python.yml, python 3.12, coverage-threshold 82"]
  CI --> SEC["job security: security.yml defaults"]
  subgraph PY["api / python (.)"]
    P1["Checkout"] --> P2["Set up uv and Python"]
    P2 --> P3["Install: auto, uv sync --frozen --all-extras"]
    P3 --> P4["Start PostgreSQL: skipped, postgres false"]
    P4 --> P5["Lint: Ruff check and format --check"]
    P5 --> P6["Typecheck: mypy"]
    P6 --> P7["Test: pytest incl. vendor/service-auth/tests"]
    P7 --> P8["Coverage gate: fail below 82"]
  end
  API --> P1
  subgraph SC["security jobs, parallel"]
    S1["gitleaks"]
    S2["semgrep p/default"]
    S3["osv-scanner"]
    S4["trivy-fs HIGH,CRITICAL vuln,misconfig"]
  end
  SEC --> S1
  SEC --> S2
  SEC --> S3
  SEC --> S4
  P8 --> END["status checks on commit / PR; no deploy step"]
  S1 --> END
  S2 --> END
  S3 --> END
  S4 --> END
  REN["Renovate: Monday before 9am Asia/Bangkok, lock maintenance monthly"] -.->|"opens PRs"| T2
```

- ไม่มี `needs:` ระหว่าง `api` และ `security` (รันขนาน)
- ตัวอย่าง run จริง: `api / python (.)`, `security / semgrep`, `security / gitleaks`, `security / osv-scanner`, `security / trivy-fs` (run 39019148129)

Sources: `.github/workflows/ci.yml`, platform-ci-workflows @ `87dc5e1` `.github/workflows/ci-python.yml` / `security.yml` (local clone `~/work/oa-infra/platform-ci-workflows`, read-only), `renovate.json`, `gh run view 39019148129 --json jobs`
