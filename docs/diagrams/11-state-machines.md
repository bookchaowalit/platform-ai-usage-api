# 11 — State machines

## Provider status (`providers[].status`, computed per request)

```mermaid
stateDiagram-v2
  [*] --> not_connected: snapshot file missing
  [*] --> error: unreadable, symlink, too large, duplicate keys
  [*] --> Validate: snapshot parsed
  Validate --> error: schema, provider or source mismatch, bad collected_at, more than 60 s in future
  Validate --> error: no window with usable used_percent
  Validate --> ready: age 900 s or less
  Validate --> stale: age over 900 s
  ready --> stale: time passes without new snapshot
  stale --> ready: collector writes a fresh snapshot
  error --> ready: valid fresh snapshot written
  not_connected --> ready: first snapshot written
```

`next_action`: `not_connected` → `connect_provider`; `error` → `check_source`; `stale` → `refresh_usage`; `ready` → `quota_reached` / `quota_low` / `use_before_reset` (ตามลำดับความสำคัญ) หรือ `monitor`

## Quota window (`windows[].status`) and alerts

```mermaid
stateDiagram-v2
  [*] --> active: resets_at in future or unknown
  [*] --> expired: resets_at at or before now
  active --> expired: reset time passes
  state active {
    [*] --> no_alert
    no_alert --> use_before_reset: remaining 30 or more and reset within 6 h or 24 h window rule
    no_alert --> quota_low: used 85 or more
    quota_low --> quota_reached: used 100
    use_before_reset --> no_alert: blocked when another active window has remaining 0
  }
  expired --> [*]: remaining null, no alerts
```

## ROI verdict (`roi.verdict`)

```mermaid
stateDiagram-v2
  [*] --> incomplete: any subscription fee missing
  [*] --> incomplete: profit_before_ai unknown
  [*] --> no_spend: total spend 0
  [*] --> paying_for_itself: ratio 3 or more
  [*] --> not_paying_for_itself: ratio below 3
```

## API readiness (`/ready`)

```mermaid
stateDiagram-v2
  [*] --> not_ready_development: development and no policy configured, 503 auth development
  [*] --> not_ready_disabled: policy configured but invalid, or production without policy, 503 auth disabled
  [*] --> not_ready_source: store.snapshot raised, 503 source unavailable
  [*] --> ready: snapshot ok and policy ready, 200
```

Sources: `model.py` (`project_provider`, `empty_provider`, `project_window`, `window_alerts`, `quota_usage`, `project_roi`, `STALE_SECONDS`, `FUTURE_TOLERANCE_SECONDS`), `vendor/service-auth/service_auth/__init__.py` (`readiness`), `contracts/ai-usage.v1.md`
