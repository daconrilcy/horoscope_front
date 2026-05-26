<!-- Commentaire global: cette preuve de redaction documente les garanties CS-311 sur les payloads analytics publics. -->

# Redaction Proof

## Runtime Guard

`frontend/src/hooks/useAnalytics.ts` owns the redaction boundary:

- `SENSITIVE_ANALYTICS_FIELD_NAMES` lists the blocked keys.
- `sanitizeAnalyticsProps` removes blocked keys before Plausible, Matomo, or noop emission.
- `/natal` projection instrumentation only sends public fields: `route`, `state`, `projection_type`, `state_reason`, `public_error_code`, `plan_code`, and `source`.

## Test Evidence

- `frontend/src/tests/useAnalytics.test.tsx` proves sensitive keys are removed before Plausible emission.
- `frontend/src/tests/natalInterpretation.test.tsx` proves success, API error, entitlement denied, empty, degraded without time, and retry events are emitted with public payloads.
- The missing-birth-data test asserts tracked calls do not contain `birth_date`, `birth_time`, `birth_place`, `latitude`, `longitude`, `provider_response`, `raw_runtime`, `replay_snapshot`, `prompt`, `api_key`, or `password`.

## Static Scan Evidence

- Direct analytics provider calls are absent from `frontend/src/features`, `frontend/src/components`, and `frontend/src/api`.
- Direct projection `fetch`/`axios` calls are absent from `frontend/src`.
- Inline styles are absent from touched natal TSX surfaces.
- The broad sensitive-key scan returns existing repository matches and the redaction allowlist itself; it is classified as contextual evidence, not a clean negative scan.
