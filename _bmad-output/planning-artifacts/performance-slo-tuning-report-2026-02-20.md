# Performance SLO Tuning Report - 2026-02-20

## Scope

- Story: `10-3-tuning-performance-guide-par-slo`
- Critical flows: chat, billing, privacy, b2b API
- Baseline source: `artifacts/load-test-report.json` (profile `smoke`)

## SLO Targets

- API latency:
  - p95 <= 300 ms on critical read endpoints
  - p99 <= 700 ms on critical read endpoints
- Error budget:
  - 5xx rate <= 0.5%
  - controlled protection statuses (429/409) accepted per endpoint policy
- Availability target:
  - >= 99.5% monthly on API availability probes

## Baseline Snapshot (Before 10.3 tuning)

- Billing quota (`/v1/billing/quota`):
  - p95: 66.03 ms
  - p99: 67.08 ms
  - error_rate: 0%
- Privacy export status:
  - p95: 73.26 ms
  - p99: 73.77 ms
  - error_rate: 0%
- Privacy delete request:
  - p95: 77.31 ms
  - p99: 78.00 ms
  - error_rate: 0%
- Chat conversations:
  - p95: 64.88 ms
  - p99: 65.65 ms
  - error_rate: 0%

## Applied Tuning

### DB

- Added composite indexes for critical sort/filter patterns:
  - `chat_conversations(user_id, status, updated_at, id)`
  - `chat_conversations(user_id, updated_at, id)`
  - `chat_messages(conversation_id, created_at, id)`
  - `user_privacy_requests(user_id, request_kind, requested_at, id)`
  - `user_subscriptions(user_id, updated_at, id)`
  - `enterprise_daily_usages(enterprise_account_id, usage_date)`
- Migration: `backend/migrations/versions/20260220_0019_add_performance_indexes.py`

### Cache

- Introduced short-lived subscription status cache in `BillingService`:
  - key: `user_id`
  - TTL: `BILLING_SUBSCRIPTION_CACHE_TTL_SECONDS` (default `5s`)
  - explicit invalidation on checkout/retry/plan-change

### Query path reduction

- `/v1/billing/quota` now reuses preloaded subscription from router.
- Removed one redundant subscription lookup in quota path.
- Measurable structural gain: subscription lookup count for this path reduced from `2` to `1` (`-50%`).

### Retry/timeout policy

- Added configurable backoff + jitter for guidance retries:
  - `CHAT_LLM_RETRY_BACKOFF_SECONDS`
  - `CHAT_LLM_RETRY_BACKOFF_MAX_SECONDS`
  - `CHAT_LLM_RETRY_JITTER_SECONDS`
- Added metrics:
  - `guidance_retry_backoff_seconds`
  - `guidance_retry_backoff_total`

## Validation

- Lint:
  - `ruff format .`
  - `ruff check .`
- Tests:
  - `pytest -q backend/app/tests/unit/test_billing_service.py backend/app/tests/unit/test_quota_service.py backend/app/tests/unit/test_guidance_service.py`
  - `pytest -q backend/app/tests/integration/test_billing_api.py backend/app/tests/integration/test_privacy_api.py backend/app/tests/integration/test_load_smoke_critical_flows.py`

All listed checks passed.

## Cost/Latency Trade-offs

- Cache TTL is deliberately short (5s) to limit stale exposure while cutting repeated DB reads from front polling.
- Composite indexes increase write cost slightly but lower read latency risk on high-frequency list/status endpoints.
- Retry backoff is configurable and defaults to conservative values to avoid unexpected latency inflation.

## Guardrails / Rollback

- Disable cache quickly by setting `BILLING_SUBSCRIPTION_CACHE_TTL_SECONDS=0`.
- Disable retry backoff by setting:
  - `CHAT_LLM_RETRY_BACKOFF_SECONDS=0`
  - `CHAT_LLM_RETRY_JITTER_SECONDS=0`
- Rollback DB index tuning with Alembic downgrade to `20260220_0018`.

## Remaining tuning backlog (prioritized)

1. Add explicit query timing instrumentation per repository method for top-N slow query reporting.
2. Add Redis-backed cache implementation for multi-instance deployments.
3. Add scheduled SLO regression report generation (baseline vs current) in CI/perf pipeline.
