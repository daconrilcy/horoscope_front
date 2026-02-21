# Ops Observability Runbook (Story 8.2)

## Scope

Parcours critiques surveilles:
- auth
- billing/quota
- chat/guidance
- privacy
- natal chart
- b2b api

## KPI minimaux

- Disponibilite API: `availability_percent`
- Erreurs serveur: `error_5xx_rate`
- Latence p95 API: `p95_latency_ms`
- Saturation quota: `quota_exceeded_total`
- Echecs privacy: `privacy_failures_total`
- Echecs auth b2b: `b2b_auth_failures_total`

## Seuils d alerte initiaux

- `availability_degraded` (critical): < 99%
- `error_rate_5xx_high` (high): > 2%
- `latency_p95_high` (medium): > 1200 ms
- `quota_exceeded_spike` (medium): >= 25 evenements/fenetre
- `privacy_failures_detected` (high): > 0 evenement/fenetre
- `b2b_auth_failures_spike` (medium): >= 10 evenements/fenetre

## Dashboards operationnels

Dashboard API health:
- requests_total
- errors_4xx_total / errors_5xx_total
- availability_percent
- p95_latency_ms

Dashboard metier:
- quota_exceeded_total
- privacy_failures_total
- llm_error_count / out_of_scope_rate (via conversation-kpis)

Dashboard B2B:
- b2b_auth_failures_total
- b2b quota exceeded

## Triage rapide

1. Recuperer `operational-summary` avec `window=1h` puis `window=24h`.
2. Identifier les alertes `status=firing` et severite.
3. Correlation avec logs via `request_id` pour erreurs 5xx.
4. Si `latency_p95_high`, verifier services dependants (DB/LLM).
5. Si `privacy_failures_detected`, suspendre operations privacy non critiques et analyser code d erreur.
6. Si `b2b_auth_failures_spike`, verifier rotation/etat credentials entreprise.
