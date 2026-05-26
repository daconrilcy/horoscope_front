# Acceptance Traceability - CS-311

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The event catalog lists seven projection events. | `evidence/event-catalog.json` lists exactly seven `natal_projection_*` events. | Targeted test command PASS; catalog reviewed in final evidence. | PASS |
| AC2 | Analytics uses the existing frontend owner. | `frontend/src/hooks/useAnalytics.ts` owns event types and redaction; `NatalInterpretation.tsx` uses `useAnalytics`. | `rg useAnalytics frontend/src/features/natal-chart frontend/src/hooks`; direct provider scan PASS. | PASS |
| AC3 | Success state emits a projection success event. | `NatalInterpretation.tsx` emits `natal_projection_success` for projection data. | `natalInterpretation.test.tsx` success assertions PASS. | PASS |
| AC4 | API error state emits a public error event. | Non-403 errors emit `natal_projection_api_error` with `public_error_code`. | `natalInterpretation.test.tsx` API error/retry test PASS. | PASS |
| AC5 | Entitlement denial emits a public denied event. | HTTP 403 `ApiError` emits `natal_projection_entitlement_denied`; backend decision is not changed. | `natalInterpretation.test.tsx` entitlement test PASS. | PASS |
| AC6 | Missing birth-data or empty-display state emits a redacted empty event. | Missing `chartId` emits `missing_birth_data`; empty projection queries emit `empty_display`. | `natalInterpretation.test.tsx` empty and missing-data tests PASS. | PASS |
| AC7 | Degraded-without-time state emits a redacted degraded event. | `hasDegradedWithoutTime` emits `natal_projection_degraded` with `missing_birth_time`. | `natalInterpretation.test.tsx` degraded test PASS. | PASS |
| AC8 | User retry emits a retry event. | `projectionState.refetchAll` emits `natal_projection_retry` before user-triggered refetch. | `natalInterpretation.test.tsx` retry assertion PASS. | PASS |
| AC9 | Tracked payloads exclude sensitive keys. | `sanitizeAnalyticsProps` drops `SENSITIVE_ANALYTICS_FIELD_NAMES`; instrumentation sends public keys only. | `useAnalytics.test.tsx` redaction test PASS; `sensitive-key-scan.txt` documents static scan context. | PASS |
| AC10 | Observability limits are documented. | `evidence/observability-limits.md` records tracked states and explicit non-goals. | Evidence artifact present; final evidence references limits. | PASS |
| AC11 | Frontend validation passes. | No package, CSS, backend, or API contract changes. | `pnpm lint` PASS; targeted Vitest PASS; full Vitest PASS; local startup HTTP 200. | PASS |
| AC12 | Story evidence is persisted. | `evidence/*`, `generated/03-acceptance-traceability.md`, `generated/10-final-evidence.md`, and tracker updated. | Final `condamad_validate.py` PASS after evidence update. | PASS |
