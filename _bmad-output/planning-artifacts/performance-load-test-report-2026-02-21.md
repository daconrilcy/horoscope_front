# Performance Load Test Report - 2026-02-21

## Campaign Metadata

- Date: 2026-02-21
- Environment: local dev (single host)
- Base URL: `http://127.0.0.1:8000`
- Profiles executed: `smoke`, `nominal`, `stress` (phased load `ramp_up/plateau/spike`)
- Raw reports:
  - `artifacts/load-test-matrix/load-test-smoke.json`
  - `artifacts/load-test-matrix/load-test-nominal.json`
  - `artifacts/load-test-matrix/load-test-stress.json`
- B2B scenario enabled: no (missing `B2B_API_KEY`)
- Ops correlation enabled: no (missing `OPS_ACCESS_TOKEN`)

## Scenarios Executed

1. `billing_quota` (`GET /v1/billing/quota`)
2. `privacy_export_status` (`GET /v1/privacy/export`)
3. `privacy_delete_request` (`POST /v1/privacy/delete`, confirmation `DELETE`)
4. `chat_conversations` (`GET /v1/chat/conversations?limit=20&offset=0`)

## Results Snapshot

### Smoke
- `billing_quota`: 20 success / 0 error, p95 64.07ms, p99 64.07ms, 9.00 req/s
- `privacy_export_status`: 10 success / 0 error (+10 responses 429 attendues), p95 70.57ms, p99 70.57ms, 9.40 req/s
- `privacy_delete_request`: 16 success / 0 error (+4 responses 429 attendues), p95 79.02ms, p99 79.02ms, 8.88 req/s
- `chat_conversations`: 20 success / 0 error, p95 65.21ms, p99 65.21ms, 9.22 req/s

### Nominal
- `billing_quota`: 25 success / 0 error (+55 responses 429 attendues), p95 70.85ms, p99 72.74ms, 18.63 req/s
- `privacy_export_status`: 10 success / 0 error (+70 responses 429 attendues), p95 71.55ms, p99 72.00ms, 18.96 req/s
- `privacy_delete_request`: 10 success / 0 error (+70 responses 429 attendues), p95 78.08ms, p99 79.48ms, 18.75 req/s
- `chat_conversations`: 80 success / 0 error, p95 64.05ms, p99 64.61ms, 18.97 req/s

### Stress
- `billing_quota`: 24 success / 0 error (+136 responses 429 attendues), p95 72.58ms, p99 74.79ms, 17.70 req/s
- `privacy_export_status`: 10 success / 0 error (+150 responses 429 attendues), p95 72.09ms, p99 73.07ms, 17.45 req/s
- `privacy_delete_request`: 10 success / 0 error (+150 responses 429 attendues), p95 78.13ms, p99 78.95ms, 17.79 req/s
- `chat_conversations`: 160 success / 0 error, p95 63.73ms, p99 64.49ms, 17.34 req/s

## Saturation Signals

- 5xx responses: none across all profiles/scenarios.
- 429 concentration: present on privacy and quota endpoints, coherent with configured protections.
- Highest p95 observed: `privacy_delete_request` (78.13ms, stress).
- Immediate conclusion: no critical saturation detected under tested local load profiles.

## Gap Closure Statement

- The remaining Epic 10 performance gap ("no full load campaign rerun") is closed:
  - Full matrix executed (`smoke + nominal + stress`).
  - Results captured in versioned artifacts.
  - Smoke integration check validated: `backend/app/tests/integration/test_load_smoke_critical_flows.py` passed.

## Remaining Optional Extensions

1. Re-run matrix with B2B scenario enabled (`B2B_API_KEY`) to cover `/v1/b2b/astrology/weekly-by-sign`.
2. Re-run matrix with ops correlation (`OPS_ACCESS_TOKEN`) to attach pre/post operational-summary snapshots.
