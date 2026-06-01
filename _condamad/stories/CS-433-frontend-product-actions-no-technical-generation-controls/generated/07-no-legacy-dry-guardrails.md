# No Legacy / DRY Guardrails — CS-433

## Canonical ownership

- Product-action transport stays in `frontend/src/api/natal-chart/index.ts`.
- Natal interpretation orchestration stays in `frontend/src/features/natal-chart/NatalInterpretation.tsx`.
- Presentational rendering stays in `frontend/src/components/natal-interpretation/**`; no API calls added there.
- Tests reuse `frontend/src/tests/natalInterpretation.test.tsx`, `NatalChartPage.test.tsx`, `natalChartApi.test.tsx`, and the architecture guard suite.

## Removed legacy surfaces

- Deleted old POST helper path to `/v1/natal/interpretation`.
- Removed `shouldRefreshShortAfterBasicUpgrade`.
- Removed frontend request fields `use_case_level`, `variant_code`, `forceRefresh`, `force_refresh`, `useCaseLevel`, `variantCode` from the natal API/action surface.
- Replaced hidden refresh behavior with explicit product actions: `preview`, `generate_full`, `regenerate`, `download`.

## Compatibility classification

- `downloadNatalInterpretationPdf` and `previewNatalInterpretationPdf` remain document utilities only; they are not natal reading generation helpers.
- `useNatalInterpretation` remains as the existing hook import path but its implementation is a product-action query wrapper with no legacy request fields. No adapter translates old technical options into product actions.

## Guardrails applied

- `RG-071`: `NatalInterpretation` remains the feature owner; component architecture tests PASS.
- `RG-073`: orchestration remains under `frontend/src/features/natal-chart/**`; no wrapper/re-export added.
- `RG-153`: `/natal` page composition guard scan PASS.
- `RG-154`: public DOM denylist scan PASS.
- `RG-158`: narrative accordion guard scan PASS.
- `RG-170`: Basic sources/legal dedup covered by full Vitest suite and build.
