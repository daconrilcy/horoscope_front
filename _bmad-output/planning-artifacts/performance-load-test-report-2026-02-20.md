# Performance Load Test Report - 2026-02-20

## Campaign Metadata

- Date: 2026-02-20
- Environment: local dev (single host)
- Base URL: `http://127.0.0.1:8000`
- Profile: `smoke` with phased load (`ramp_up`/`plateau`/`spike`)
- Iterations per scenario: 24
- Concurrency baseline: 6 (phase peak concurrency: 9)
- B2B scenario enabled: yes
- Raw report: `artifacts/load-test-report.json`

## Scenarios Executed

1. `billing_quota` (`GET /v1/billing/quota`)
2. `privacy_export_status` (`GET /v1/privacy/export`)
3. `privacy_delete_request` (`POST /v1/privacy/delete`, confirmation `DELETE`)
4. `chat_conversations` (`GET /v1/chat/conversations?limit=20&offset=0`)
5. `b2b_weekly_by_sign` (`GET /v1/b2b/astrology/weekly-by-sign`)

## Results Snapshot

- `billing_quota`
  - success/error: 24 / 0
  - error rate: 0%
  - throughput: 9.49 req/s
  - latency: p50 63.60ms, p95 66.03ms, p99 67.08ms
- `privacy_export_status`
  - success/error: 8 / 0 (+16 responses 429 attendues par protections)
  - error rate: 0%
  - throughput: 9.50 req/s
  - latency: p50 64.14ms, p95 73.26ms, p99 73.77ms
- `privacy_delete_request`
  - success/error: 9 / 0 (+15 responses 429 attendues par protections)
  - error rate: 0%
  - throughput: 9.41 req/s
  - latency: p50 73.80ms, p95 77.31ms, p99 78.00ms
- `chat_conversations`
  - success/error: 24 / 0
  - error rate: 0%
  - throughput: 9.82 req/s
  - latency: p50 61.09ms, p95 64.88ms, p99 65.65ms
- `b2b_weekly_by_sign`
  - success/error: 24 / 0
  - error rate: 0%
  - throughput: 9.49 req/s
  - latency: p50 65.39ms, p95 71.48ms, p99 77.41ms

## Saturation Signals

- 5xx responses: none
- 429 concentration: presente sur privacy (export/delete), attendue via rate limits
- Highest p95: `privacy_delete_request` (77.31ms)
- Ops correlation:
  - pre-run `/v1/ops/monitoring/operational-summary`: 200
  - post-run `/v1/ops/monitoring/operational-summary`: 200
- Immediate conclusion: pas de saturation critique, protections privacy actives et stables sous charge.

## Prioritized Tuning Actions

1. Affiner les seuils rate-limit privacy (`export/delete`) pour equilibrer protection et UX.
   - Impact: reduit les 429 non necessaires en charge legitime.
2. Executer le profil `nominal` puis `stress` en staging avec charge soutenue plus longue.
   - Impact: valide les limites au-dela du smoke et revele les derives p95/p99.
3. Ajouter des seuils de throughput minimum par scenario dans le gate de performance.
   - Impact: transforme la campagne en garde-fou objectivable.
4. Capturer automatiquement un snapshot ops monitoring pre/post dans les artefacts de pipeline.
   - Impact: facilite la comparaison run-to-run.
5. Completer une matrice B2B par plan (fixed + volume) pour observer les effets quota/facturation.
   - Impact: aligne perf et comportement metier B2B.

## Re-test Criteria

- Conserver 0 erreurs 5xx sur tous les scenarios.
- Maintenir p95 < 120ms sur smoke pour billing/chat/b2b.
- Monitorer les 429 privacy et garder un ratio coherent avec la politique de protection.
- Executer smoke + nominal + stress, puis comparer throughput et p95/p99.
