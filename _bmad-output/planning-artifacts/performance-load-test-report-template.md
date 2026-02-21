# Performance Load Test Report Template (Story 8.4)

## Campaign Metadata

- Date:
- Environment:
- Backend version/commit:
- Base URL:
- Iterations per scenario:
- Concurrency:
- B2B scenario enabled: yes/no

## Scenarios Covered

1. `billing_quota` (`GET /v1/billing/quota`)
2. `privacy_export_status` (`GET /v1/privacy/export`)
3. `privacy_delete_request` (`POST /v1/privacy/delete`, confirmation DELETE)
4. `chat_conversations` (`GET /v1/chat/conversations`)
5. `b2b_weekly_by_sign` (`GET /v1/b2b/astrology/weekly-by-sign`) if API key available

## Results Snapshot

For each scenario:
- total requests
- success count / error count
- error rate (%)
- throughput (req/s)
- latency p50/p95/p99 (ms)
- status code distribution

## Saturation Signals

- Any 5xx spikes:
- Any 429 concentration (rate limiting/quota):
- Highest p95/p99 scenario:
- Notes from ops monitoring (`/v1/ops/monitoring/operational-summary`):
- Ops correlation status (pre-run / post-run call status):

## Prioritized Tuning Actions

Top 5 actions:
1. Action:
   - Target scenario:
   - Expected impact:
   - Effort:
   - Risk:
2. Action:
   - Target scenario:
   - Expected impact:
   - Effort:
   - Risk:
3. Action:
   - Target scenario:
   - Expected impact:
   - Effort:
   - Risk:
4. Action:
   - Target scenario:
   - Expected impact:
   - Effort:
   - Risk:
5. Action:
   - Target scenario:
   - Expected impact:
   - Effort:
   - Risk:

## Re-test Criteria

- Which metrics must improve:
- Acceptance thresholds for next run:
- Planned date for re-test:
