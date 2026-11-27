# 01 — Business process (As-Is / To-Be)

ระบบนี้คือ **ai-usage**: CLI (`collector.py`, standard library เท่านั้น) + HTTP API แบบ read-only (`server.py`) ที่รันในเครื่องของเจ้าของ (local-first, systemd user units) เพื่อตอบคำถามเดียว: "โควตา Claude / Codex เหลือเท่าไร รีเซ็ตเมื่อไร และค่า AI รายเดือนคุ้มไหม" โดยไม่ใช้โควตาเอง ไม่เก็บ prompt / reply / account id / credential

Last reviewed: 2026-11-27 · commit `3971301`

## As-Is (จาก code วันนี้)

```mermaid
flowchart TD
  subgraph Collect["Collect (collector.py)"]
    C1["Claude Code refreshes status line"] --> C2["claude-statusline hook reads stdin JSON"]
    C2 --> C3{"rate_limits present?"}
    C3 -->|"yes"| C4["atomic write claude.json"]
    C3 -->|"no"| C5["keep old snapshot; print waiting for quota"]
    X1["systemd: collector.py codex --interval 300"] --> X2["spawn codex app-server --stdio"]
    X2 --> X3["JSON-RPC initialize then account/rateLimits/read"]
    X3 -->|"ok"| X4["atomic write codex.json"]
    X3 -->|"error or timeout"| X5["print unavailable; last snapshot ages to stale"]
  end
  subgraph Configure["Configure (owner, collector.py configure-*)"]
    S1["configure-fees / configure-subscription / configure-business"] --> S2["merge into settings.json"]
  end
  subgraph Serve["Read (server.py or collector.py status)"]
    R1["Owner runs collector.py status"] --> R2["render quota table in terminal"]
    D1["Dashboard GET /api/v1/ai-usage"] --> D2["auth check"]
    D2 --> D3["UsageStore.snapshot projects providers, subscriptions, alerts, ROI"]
    D3 --> D4["JSON response, Cache-Control no-store"]
  end
  C4 --> STATE[("AI_USAGE_STATE_DIR")]
  X4 --> STATE
  S2 --> STATE
  STATE --> R2
  STATE --> D3
  D4 --> O["Owner decides: use quota before reset, wait, or pause a subscription"]
  R2 --> O
```

ขั้นตอนธุรกิจจริงที่ code รองรับ:

1. **เก็บโควตา** — Claude ผ่าน status-line callback (`ingest_claude`), Codex ผ่าน polling ทุก 300 วินาที (`read_codex`); เก็บเฉพาะ allowlist field
2. **ตั้งค่าตัวเลขธุรกิจ** — ค่าสมาชิก (USD สำหรับ Claude/Codex, THB สำหรับทั้ง 5 เจ้า), plan, `active_days_30d`, รายได้ / กำไรก่อนหักค่า AI รายเดือน
3. **อ่าน / ตัดสินใจ** — `status` ใน terminal หรือ dashboard ผ่าน API; API คำนวณ alert (`quota_low` 85%, `quota_reached` 100%, `use_before_reset`) และ ROI (`target_ratio` 3, budget band 5–10% ของรายได้) ใหม่ทุก request; backend ไม่ส่ง notification ภายนอก

Sources: `collector.py` (`ingest_claude`, `read_codex`, `main`, `update_settings`), `server.py` (`AiUsageApi.handle`), `model.py` (`UsageStore.snapshot`, `window_alerts`, `project_roi`), `systemd/solo-ai-usage-collector.service`, `PRODUCT.md`, `contracts/ai-usage.v1.md`

## To-Be (ไม่มีที่เขียนไว้)

ไม่มี To-Be ที่เขียนไว้ — ไม่มี `docs/UPGRADE-PLAN.md`, ไม่มี ADR/roadmap และ `specs/` มีเพียง SPEC-001 (CI coverage gate) กับ SPEC-002 (L2 baseline) ซึ่งเป็นงาน tooling ไม่เปลี่ยน business process
`PRODUCT.md` ระบุสิ่งที่ "ไม่ทำ" (out of scope: billed API spend, quota ของ Gemini/Grok/Muse, write route) ซึ่งเป็นขอบเขตปัจจุบัน ไม่ใช่เป้าหมายที่ตกลงแล้ว จึงไม่วาด To-Be

Sources: `PRODUCT.md` (Constraints, Measures), `specs/README.md`, `specs/001-coverage-gate/spec.md`, `specs/002-l2-baseline/spec.md`

## Gap

| ID | As-Is → To-Be | Status | Owner | Evidence |
|---|---|---|---|---|
| G1 | ไม่มี To-Be ที่เขียนไว้ → owner กำหนดว่าจะเพิ่ม quota collector ของ Gemini / Grok / Muse หรือ billed API spend หรือไม่ | decide | owner | `PRODUCT.md` out of scope; ไม่มี spec หรือ ADR |

## Open questions

- dashboard ตัวไหนอ่าน `GET /api/v1/ai-usage` จริงวันนี้ (`PRODUCT.md` ระบุ `[ต้องยืนยัน]`); `PRODUCT.md` ระบุว่า relay `ai-usage-display` บน Railway **ไม่ได้** อ่าน API นี้ (รับ snapshot ที่ push เข้ามาเอง) ส่วน `docs/OWNER.th.md` ระบุ `owner-web` / `bookchaowalit/life-dashboard-web`
- image `Dockerfile` รันที่ไหนจริงหรือไม่ และ local units ตั้ง Sentry DSN หรือไม่ (`PRODUCT.md` [ต้องยืนยัน])
