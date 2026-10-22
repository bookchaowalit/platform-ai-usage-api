# Product

<!-- impeccable:product-schema 1 -->

## Platform

api (plus a standard-library CLI, `collector.py`)

## Users

- The owner at the terminal: `python3 collector.py status` prints how much Claude and Codex
  subscription quota is left and when each window resets.
- Claude Code itself: the `claude-statusline` hook feeds Claude's status-line JSON to the
  collector, which saves a snapshot and prints a short quota line.
- A local web dashboard or small device display that reads `GET /api/v1/ai-usage` (default CORS
  origins `http://127.0.0.1:3600` and `http://localhost:3600`). Which dashboard and which relay
  read it today: [ต้องยืนยัน] (the registry names an `ai-usage-display` relay on Railway).

## Product Purpose

Show remaining Claude and Codex quota, reset times, low-quota and "use it before it resets"
alerts, and the monthly cost and ROI of the owner's five AI subscriptions (Claude, Codex, Gemini,
Grok, Muse), without ever spending quota or storing prompts, replies, account ids or credentials.

Success: the numbers the owner sees match what the Claude and Codex CLIs report, stale data is
labelled stale, and an expired window is never shown as available quota.

## Positioning

A local-first, read-only projection. The collector reads numbers the CLIs already report (Claude's
status line, Codex's local `app-server` `account/rateLimits/read`) and never starts an AI turn.
The API serves only sanitized snapshots and owner settings; it has no write route.

## Operating Context

- Local by design (registry `online-systems.yaml`, id `ai-usage`, status `exception`, host
  `local`): systemd user units `solo-ai-usage-api` (`server.py --host 127.0.0.1 --port 3520`) and
  `solo-ai-usage-collector` (`collector.py codex --interval 300`) run from this checkout.
- Not deployed on Railway; `service.yaml` has `deploy.target: unassigned`. The `Dockerfile` builds
  an image that serves `/health` and `/ready` on port 3520 and needs `AI_USAGE_API_AUTH_*` to start
  on a non-loopback host. Whether that image runs anywhere: [ต้องยืนยัน].
- Snapshots live in `AI_USAGE_STATE_DIR` (default `~/.local/state/solo-empire/ai-usage/`).
- Errors from the API go to Sentry only when `SENTRY_DSN` is set (errors only, no personal data,
  tokens and URLs scrubbed). Whether a DSN is configured for the local units: [ต้องยืนยัน].

## Capabilities and Constraints

- `GET /health` (liveness and schema version), `GET /ready` (`status`, `source`, `auth`),
  `GET /api/v1/ai-usage` (providers, summary, subscriptions, alerts, ROI), `OPTIONS` (CORS
  preflight). Other methods on the usage route answer 405; unknown paths 404; unexpected failures a
  generic 500 with no exception text.
- Auth: on loopback in development, no auth (or a static token if `AI_USAGE_API_TOKEN` is set).
  Beyond loopback the server forces production and requires owner-scoped RS256 JWTs
  (`aud=ai-usage-api`, `scope=ai-usage:read`, lifetime at most 120 s); without valid
  `AI_USAGE_API_AUTH_*` it refuses to start. Origins outside the allowlist get 403.
- Snapshot rules: at most 1 MiB, no symlinks, duplicate JSON keys rejected; older than 900 s is
  `stale` (no alerts); more than 60 s in the future is `error`; percentages are clamped to 0..100
  and remaining is recomputed from used; a window whose reset has passed is `expired` with no
  remaining value.
- Alerts: `quota_low` at 85% used, `quota_reached` at 100%, `use_before_reset` when at least 30%
  is left and the reset is within 6 h (windows up to 360 min) or 24 h (weekly windows). The
  backend sends no external notification.
- Subscriptions and ROI: monthly fees are owner-entered THB amounts (never inferred from a plan
  or converted from USD); `consider_pausing` flags a paid subscription with near-zero use.
- Out of scope: billed API spend (`api_billed_cost_usd` is always `null`), any write route,
  quota for Gemini, Grok and Muse (cost-only entries).

## Measures

- Providers in `ready` state versus `stale`/`not_connected` (`summary.connected`).
- Snapshot age at read time (target: under 900 s while the collector runs).
- Subscriptions flagged `consider_pausing` each month, and `roi` against the profit target.
- 5xx answers on `/api/v1/ai-usage` (Sentry, when enabled). No uptime monitor targets this local
  API; `platform-uptime-worker` watches only the `ai-usage-display` relay.
