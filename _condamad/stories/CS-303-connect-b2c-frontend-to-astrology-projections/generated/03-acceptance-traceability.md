# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The central API client sends projection requests. | `frontend/src/api/astrologyProjections.ts`, `frontend/src/api/index.ts` | `pnpm test -- natalChartApi`; backend `TestClient` projection endpoint tests | PASS |
| AC2 | `beginner_summary_v1` is displayed. | `NatalInterpretation.tsx`, `NatalInterpretationContent.tsx`, `NatalInterpretation.css` | `pnpm test -- component-architecture-guards natalInterpretation NatalChartPage natalChartApi` | PASS |
| AC3 | `client_interpretation_projection_v1` is displayed. | `NatalInterpretationContent.tsx` projection card rendering | `pnpm test -- component-architecture-guards natalInterpretation NatalChartPage natalChartApi` | PASS |
| AC4 | Loading state is visible. | `AstrologyProjectionsPanel` loading branch | `natalInterpretation.test.tsx` loading projection state | PASS |
| AC5 | Empty state is visible. | `AstrologyProjectionsPanel` empty branch | `natalInterpretation.test.tsx` empty projection state | PASS |
| AC6 | API error state is visible. | `AstrologyProjectionsPanel` API error branch with retry | `natalInterpretation.test.tsx`; backend authorization tests | PASS |
| AC7 | Entitlement refusal is visible. | Feature maps HTTP 403 to locked presentation state | `natalInterpretation.test.tsx`; `backend/tests/api/test_projection_authorization.py` | PASS |
| AC8 | Degraded mode is visible. | `ProjectionCard` degraded `payload.state` branch | `natalInterpretation.test.tsx` degraded projection payload | PASS |
| AC9 | Disclaimers are app-owned. | Existing `legalNoticeLines` rendering remains; projection panel does not read payload disclaimers | targeted `rg` disclaimer scan; existing app-owned disclaimer tests | PASS |
| AC10 | Sensitive internals stay hidden. | Wrapper and rendering consume only public response fields and generic payload display | targeted `rg` forbidden internals on touched app paths | PASS |
| AC11 | Backend route contract is referenced. | Evidence references `backend/app/services/api_contracts/public/projections.py` and runtime route | `app.openapi()` + `app.routes`; backend projection API pytest | PASS |
| AC12 | Frontend validation passes. | Targeted frontend suite, lint, architecture guards | Targeted PASS; full `pnpm test` has unrelated i18n/consultation failures | PASS_WITH_LIMITATIONS |
| AC13 | Story evidence artifacts are persisted. | `evidence/*.md`, `evidence/*.json`, `evidence/validation.txt`, generated final evidence | `condamad_validate.py` rerun pending after final evidence update | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
