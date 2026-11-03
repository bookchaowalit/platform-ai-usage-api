# 03 — User flows

ไม่มี UI ใน repo นี้ flow จึงเป็น CLI commands (`collector.py`) และ HTTP routes (`server.py`) ต่อ role

## Flow A — Owner: ติดตั้งและดูโควตา

```mermaid
flowchart TD
  A0["git clone and cd"] --> A1["python3 collector.py status"]
  A1 --> A2{"codex on PATH and not --offline?"}
  A2 -->|"yes"| A3["read_codex live, write codex.json; on failure keep last"]
  A2 -->|"no"| A4["read stored snapshots only"]
  A3 --> A5["render_status"]
  A4 --> A5
  A5 --> A6{"snapshot has windows?"}
  A6 -->|"no"| A7["not connected, hint: run collector.py install-claude or codex"]
  A6 -->|"yes"| A8{"age over 15 min?"}
  A8 -->|"yes"| A9["header marked stale"]
  A8 -->|"no"| A10["bars with percent left and resets in"]
  A9 --> A10
  A7 --> B0["python3 collector.py install-claude --settings-path ..."]
  B0 --> B1{"different statusLine already set?"}
  B1 -->|"yes"| B2["error existing_statusline_preserved"]
  B1 -->|"no"| B3["write statusLine command, optional --passthrough-settings"]
  B3 --> B4["next Claude refresh writes claude.json"]
```

## Flow B — Owner: ตั้งค่าตัวเลขค่าใช้จ่ายและธุรกิจ

```mermaid
flowchart LR
  F1["configure-fees --claude-fee --codex-fee"] --> V{"values valid?"}
  F2["configure-subscription --provider --fee-thb --plan --active-days"] --> V
  F3["configure-business --month --revenue-thb --profit-before-ai-thb"] --> V
  V -->|"no"| E["argparse error, exit 2"]
  V -->|"yes"| M["update_settings merges one section"]
  M --> W["atomic_json settings.json"]
  W --> OK["prints *_configured"]
```

## Flow C — Dashboard: อ่านข้อมูลผ่าน API

```mermaid
flowchart TD
  H0["Request to 127.0.0.1:3520"] --> H1{"Origin header present and not allowed?"}
  H1 -->|"yes"| H403["403 origin_not_allowed"]
  H1 -->|"no"| H2{"method and path"}
  H2 -->|"OPTIONS"| H204["204 with Allow-Methods GET, OPTIONS"]
  H2 -->|"GET /health"| H200a["200 status ok"]
  H2 -->|"GET /ready"| HR["readiness: 200 ready or 503 not_ready"]
  H2 -->|"any /api/v1/ai-usage"| HA["check_read_auth"]
  H2 -->|"other"| H404["404 not_found"]
  HA -->|"AuthError"| HE["401 / 403 / 503 reads_disabled"]
  HA -->|"ok, not GET"| H405["405 method_not_allowed"]
  HA -->|"ok, GET"| HS["200 UsageStore.snapshot"]
  HS --> UI["Dashboard shows providers[].status, alerts, roi.verdict"]
```

Sources: `collector.py` (`main`, `render_status`, `install_claude`, `update_settings`), `server.py` (`_dispatch`, `handle`, `_write`), `vendor/service-auth/service_auth/__init__.py` (`readiness`, `check_read_auth`), `README.md` (Quick start, Commands)

## Open questions

- หน้า dashboard ที่แสดงข้อมูลนี้อยู่นอก repo (`docs/OWNER.th.md` อ้าง `owner-web`); flow ฝั่ง browser notification อยู่ใน frontend นั้น ไม่ได้วาดที่นี่
