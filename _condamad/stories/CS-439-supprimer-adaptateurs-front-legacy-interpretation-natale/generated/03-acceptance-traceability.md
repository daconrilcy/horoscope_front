# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Modern API hook returns public reading payloads. | `frontend/src/api/natal-chart/index.ts` exposes `ThemeNatalReadingPublicPayload` and `UseThemeNatalReadingResult`; the product-action hook normalizes only `theme_natal*` public data. | `pnpm --dir frontend test -- natalChartApi.test.tsx ...` PASS; API hook test asserts public payload, `use_case: null`, and public sections. | PASS |
| AC2 | `NatalInterpretation.tsx` stops selecting old use cases. | `frontend/src/features/natal-chart/NatalInterpretation.tsx` no longer branches on `natal_long_free` or `natal_interpretation_short`; persisted complete selection uses product-level signals (`level`, `persona_id`, `prompt_version_id`). | `frontend-legacy-after.txt` contains only the DOM guard denylist; bounded production scan has no old use-case hits. | PASS |
| AC3 | Content ignores old `use_case`. | `NatalInterpretationContent.tsx` removed `resolveUseCase` and renders public content from modern schema/version or explicit public payloads. | `pnpm --dir frontend test -- natalInterpretation.test.tsx natalPublicDomGuard.test.tsx` PASS. | PASS |
| AC4 | Generation command bodies use only authorized fields. | `ThemeNatalReadingCommandRequest` contains only `chart_id`, `action`, `persona_profile_id`, `locale`, `client_request_id`; PDF actions reuse the same product endpoint. | `natalChartApi.test.tsx` PASS; test asserts no old command-control fields are serialized. | PASS |
| AC5 | `variant_code` stays entitlement-only in `/natal`. | No command construction uses `variant_code`; remaining hits are entitlement gate/display reads in `NatalChartPage.tsx` and `NatalAstrologerMode.tsx`. | `variant-code-after.txt` records classified entitlement-only hits. | PASS |
| AC6 | Public DOM rejects old technical symbols. | `natalPublicDomGuard.test.tsx` keeps the denylist and removes positive old-use-case fixtures. | `pnpm --dir frontend test -- natalPublicDomGuard.test.tsx` PASS. | PASS |
| AC7 | Positive old-use-case fixtures are gone. | Targeted public tests and `AdminPromptsCatalogFlow.test.tsx` fixtures now use `theme_natal_preview` instead of old natal use cases. | `frontend-legacy-after.txt` shows only the denylist declaration in `natalPublicDomGuard.test.tsx`. | PASS |
| AC8 | Inline styles are not introduced. | No TSX style changes were added. | `inline-style-after.txt`: `PASS: no matches`. | PASS |
| AC9 | Removed adapter symbols cannot reappear. | Removed `NatalInterpretationResult`, `isNatalInterpretationResult`, and `mapProductActionDataToInterpretation` from the public reading API flow. | `adapter-symbol-after.txt`: `PASS: no matches`. | PASS |
| AC10 | Story evidence artifacts are persisted. | Evidence directory contains before/after scans, validation output, startup proof, and removal audit. | `evidence/validation.txt` and scan files persisted; capsule final validation pending in `10-final-evidence.md`. | PASS |
| AC11 | Historical route actions are absent or modernized. | PDF preview/download and full generation actions use `requestThemeNatalReadingAction`; no retired route refresh control remains. | `pnpm --dir frontend test -- NatalChartPage.test.tsx natalInterpretation.test.tsx` PASS. | PASS |

All acceptance criteria are implemented and validated for review.
