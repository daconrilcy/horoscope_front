# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `NatalInterpretationSection` lives under `frontend/src/features/natal-chart/**`. | `frontend/src/features/natal-chart/NatalInterpretation.tsx` exports `NatalInterpretationSection`; old component file deleted. | PASS: `rg -n "export function NatalInterpretationSection" frontend/src/features/natal-chart`. | PASS |
| AC2 | `NatalChartPage` imports the section from the canonical feature owner. | `frontend/src/pages/NatalChartPage.tsx` imports `../features/natal-chart/NatalInterpretation`. | PASS: `rg -n "features/natal-chart" frontend/src/pages/NatalChartPage.tsx`; targeted page tests passed. | PASS |
| AC3 | The old `components/NatalInterpretation` import path is absent. | Old component path deleted and active imports moved. | PASS: old path scan under `frontend/src` returned zero active hits. | PASS |
| AC4 | Selector with astrologer dependency is no longer under `components/**`. | `frontend/src/features/natal-chart/NatalInterpretationPersonaSelector.tsx` owns `useAstrologers` and `AstrologerGrid`; old selector deleted. | PASS: `npm --prefix frontend run test -- component-architecture`; after/no-shim artifacts. | PASS |
| AC5 | `COMPONENT_API_IMPORT_EXCEPTIONS` has no natal entries or broad replacement. | Exact natal entries removed from `component-architecture-allowlist.ts`; no replacement added. | PASS: `npm --prefix frontend run test -- component-architecture`; allowlist scan returned zero natal hits. | PASS |
| AC6 | Natal interpretation interaction contract remains equivalent. | Runtime wiring and tests import the moved owner without product behavior changes. | PASS: `npm --prefix frontend run test -- component-architecture natalInterpretation NatalChartPage`; `npm --prefix frontend run lint`. | PASS |
| AC7 | CS-115 split invariant is preserved; presentational children stay API-free. | Guard now checks feature owner while presentational children remain under `components/natal-interpretation`. | PASS: `npm --prefix frontend run test -- component-architecture`; presentational API/feature scan returned zero hits. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
