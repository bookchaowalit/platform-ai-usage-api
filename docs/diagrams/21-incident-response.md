# 21 — Incident response

ไม่มี alert channel อัตโนมัติสำหรับ service นี้ (ไม่มี uptime monitor, ไม่มี Telegram / heartbeat ใน repo; Sentry opt-in) การตรวจพบจึงมาจากเจ้าของเห็นเอง flow ข้างล่างใช้ช่องทางที่มีจริงเท่านั้น

```mermaid
flowchart TD
  D1["Dashboard shows stale, not_connected or error"] --> T
  D2["collector.py status shows stale or not connected"] --> T
  D3["Sentry issue, only if SENTRY_DSN set"] --> T
  D4["CI red on main or PR"] --> T
  T["Triage"] --> T1["systemctl --user status solo-ai-usage-api solo-ai-usage-collector"]
  T --> T2["journalctl --user for collector JSON lines"]
  T --> T3["curl 127.0.0.1:3520/ready and /health"]
  T --> T4["collector.py codex once, check exit code"]
  T1 --> F{"Cause"}
  T2 --> F
  T3 --> F
  T4 --> F
  F -->|"unit stopped or code moved"| X1["daemon-reload and restart units"]
  F -->|"codex not logged in or not on PATH"| X2["fix codex CLI login or AI_USAGE_CODEX_BIN"]
  F -->|"Claude hook missing"| X3["re-run install-claude"]
  F -->|"code bug"| X4["fix with test, CI green, pull, restart"]
  X1 --> V["Verify providers ready in API"]
  X2 --> V
  X3 --> V
  X4 --> V
  V --> PM["Postmortem: no template or location in repo, open question"]
```

Commands มาจาก repo: restart (`docs/OWNER.th.md`), `collector.py codex` exit 0/1 (`collector.py main`), `/ready` (contract) `journalctl` เป็นคำสั่งมาตรฐาน systemd สำหรับ unit ที่ไม่ได้ตั้ง `StandardOutput` (ไม่ได้ระบุใน repo)

ประวัติเหตุการณ์ที่เห็นได้: CI แดง 2 ครั้งบน PR เท่านั้น (run 39019148129: Ruff `EXE001 Shebang is present but file is not executable`, แก้ใน commit ถัดไปของ PR #1 ภายใน ~1 นาที; run 39534812491: red โดยตั้งใจของ SPEC-001 AC-01) CI บน `main` เขียวทุกครั้ง (8/8)

Sources: `docs/OWNER.th.md`, `collector.py`, `server.py`, `contracts/ai-usage.v1.md`, `error_reporting.py`, `PRODUCT.md` (Measures), `gh run list -R bookchaowalit/platform-ai-usage-api`, `gh run view 39019148129 --log-failed`

## Open questions

- severity, เป้าเวลาแก้ไข และที่เก็บ postmortem สำหรับ service local นี้
- ควรมี alert (เช่น heartbeat) เมื่อ snapshot stale นานหรือไม่
