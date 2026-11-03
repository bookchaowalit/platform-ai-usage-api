# 09 — ERD

ไม่มี database: ข้อมูลที่ persist คือ JSON 3 ไฟล์ใน `AI_USAGE_STATE_DIR` (ADR-0004) ERD ข้างล่างวาด document model ของไฟล์ (persisted) และ response projection ของ `GET /api/v1/ai-usage` (ไม่ persist, คำนวณใหม่ทุก request) แยกกัน

## Persisted files

```mermaid
erDiagram
  STATE_DIR ||--o| PROVIDER_SNAPSHOT : "claude.json / codex.json"
  STATE_DIR ||--o| SETTINGS : "settings.json"
  PROVIDER_SNAPSHOT ||--o{ SNAPSHOT_WINDOW : "windows (max 20 read)"
  PROVIDER_SNAPSHOT ||--o| SESSION : "session"
  SETTINGS ||--o| MONTHLY_FEES_USD : "monthly_fees_usd"
  SETTINGS ||--o{ SUBSCRIPTION_SETTING : "subscriptions keyed by id"
  SETTINGS ||--o| BUSINESS : "business"

  STATE_DIR {
    string path "AI_USAGE_STATE_DIR or default under local state"
    string permissions "dir 0700 files 0600"
  }
  PROVIDER_SNAPSHOT {
    string schema_version "solo-empire.ai-usage.snapshot.v1"
    string provider "claude or codex"
    string source "claude_statusline or codex_app_server"
    string collected_at "UTC ISO"
    string plan "nullable, allowlisted"
  }
  SNAPSHOT_WINDOW {
    string id "five_hour seven_day primary secondary"
    string label
    float used_percent "0..100"
    float remaining_percent "ignored by API, recomputed"
    string resets_at "UTC ISO"
    int window_minutes "nullable, 1..525600"
  }
  SESSION {
    float estimated_cost_usd "nullable"
    int input_tokens "always null from collector"
    int output_tokens "always null from collector"
  }
  MONTHLY_FEES_USD {
    float claude
    float codex
  }
  SUBSCRIPTION_SETTING {
    string id "claude codex gemini grok muse"
    float monthly_fee_thb
    string plan
    int active_days_30d "0..30"
  }
  BUSINESS {
    string month "YYYY-MM"
    float monthly_revenue_thb
    float monthly_profit_before_ai_thb "may be negative"
  }
```

## Response projection (not persisted)

```mermaid
erDiagram
  USAGE_RESPONSE ||--|{ PROVIDER : "providers, always claude and codex"
  USAGE_RESPONSE ||--|| SUMMARY : "summary"
  USAGE_RESPONSE ||--|{ SUBSCRIPTION : "subscriptions, 5 fixed"
  USAGE_RESPONSE ||--|| ROI : "roi"
  PROVIDER ||--o{ WINDOW : "windows"
  PROVIDER ||--o{ ALERT : "alerts"
  SUBSCRIPTION ||--|| USAGE : "usage"

  USAGE_RESPONSE {
    string schema_version "solo-empire.ai-usage.v1"
    string generated_at
  }
  PROVIDER {
    string id
    string status "ready stale not_connected error"
    string source
    string collected_at
    string plan
    float monthly_fee_usd
    float api_billed_cost_usd "always null"
    string next_action
  }
  WINDOW {
    string id
    string label "from API allowlist"
    float used_percent
    float remaining_percent
    string resets_at
    int window_minutes
    string status "active expired"
  }
  ALERT {
    string id "provider:window:kind:resets_at"
    string kind "use_before_reset quota_low quota_reached"
    string window_id
    string message "Thai"
  }
  SUMMARY {
    int connected
    float monthly_fee_usd
    bool fees_complete
  }
  SUBSCRIPTION {
    string id
    float monthly_fee_thb
    bool has_quota_collector
    bool consider_pausing
  }
  USAGE {
    string signal "quota self_reported unknown"
    string level "active near_zero unknown"
    float used_percent
    int active_days_30d
  }
  ROI {
    float ai_spend_thb
    float profit_to_ai_ratio
    int target_ratio "3"
    string ratio_status
    string budget_status
    string verdict
  }
```

Sources: `collector.py` (`claude_snapshot`, `codex_snapshot`, `window`, `update_settings`, `main` configure-*), `model.py` (`read_snapshot`, `project_provider`, `project_window`, `window_alerts`, `project_subscription`, `project_roi`, `UsageStore.snapshot`), `contracts/ai-usage.v1.md`
