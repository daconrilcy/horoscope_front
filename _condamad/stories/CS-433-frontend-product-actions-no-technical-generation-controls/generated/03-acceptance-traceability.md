# Acceptance Traceability — CS-433

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Frontend request bodies omit `use_case_level`. | `frontend/src/api/natal-chart/index.ts` defines `ThemeNatalReadingCommandRequest` without `use_case_level`; old `fetchNatalInterpretation` removed. | `natalChartApi` body assertion; `rg` scoped control scan PASS; `pnpm --dir frontend test -- natalChartApi` PASS. | PASS |
| AC2 | Frontend request bodies omit `variant_code`. | Product-action body has no variant field; `NatalInterpretation` no longer derives request behavior from `variant_code`. | scoped control scan PASS; `natalChartApi` body assertion PASS. | PASS |
| AC3 | Basic upgrade does not auto-start short generation. | `shouldRefreshShortAfterBasicUpgrade` effect deleted; Basic history candidate disables automatic product-action query. | `pnpm --dir frontend test -- natalInterpretation NatalChartPage` PASS; test `ne relance pas une génération courte Basic...` PASS. | PASS |
| AC4 | Product-action command bodies omit force refresh controls. | Refresh state replaced by `readingAction` + `clientRequestId`; regenerate is `action: "regenerate"`. | scoped control scan PASS; `natalChartApi` body assertion rejects `force_refresh`. | PASS |
| AC5 | The full CTA sends `action: "generate_full"`. | `handleUpgrade` sets `readingAction` to `generate_full` for the full CTA. | `natalInterpretation` expects `action: "generate_full"` and client request id. | PASS |
| AC6 | The preview CTA sends `action: "preview"`. | PDF preview handler now calls `requestThemeNatalReadingAction(... action: "preview")`. | `natalInterpretation` preview action assertion PASS. | PASS |
| AC7 | The regenerate CTA sends `action: "regenerate"`. | Regenerate CTA sets next full action to `regenerate` when a complete reading exists. | `pnpm --dir frontend test -- natalInterpretation NatalChartPage` PASS; product-action positive scan confirms symbol. | PASS |
| AC8 | The download CTA sends `action: "download"`. | Download handler now calls `requestThemeNatalReadingAction(... action: "download")`. | `natalInterpretation` download action assertion PASS. | PASS |
| AC9 | Public generation request types omit technical fields. | `ThemeNatalReadingCommandRequest` exposes only `chart_id`, `action`, `persona_profile_id`, `locale`, `client_request_id`. | `pnpm --dir frontend lint` PASS; `natalChartApi` JSON body assertion PASS. | PASS |
| AC10 | The UI renders controlled slot states. | API hook exposes normalized `ThemeNatalReadingSlotState`; `NatalInterpretation` handles loading/generating/error/locked/paywall/rejected through explicit branches. | `pnpm --dir frontend test -- natalInterpretation NatalChartPage` PASS. | PASS |
| AC11 | Basic rendering consumes only public schema fields. | No changes to `NatalInterpretationContent` public Basic renderer; accepted product payload is mapped without provider internals. | `pnpm --dir frontend test` PASS; RG-154 DOM scans PASS. | PASS |
| AC12 | Legal mentions remain deduplicated. | `BasicV2Reading` and legal rendering untouched. | `pnpm --dir frontend build` PASS; `pnpm --dir frontend test` PASS including public DOM/basic tests. | PASS |
| AC13 | Removed frontend controls stay absent after implementation. | Added after-scan evidence at `evidence/frontend-control-scan-after.txt`. | scoped `rg` control scan PASS; `git diff --check` PASS. | PASS |
| AC14 | Old generator functions are deleted or readonly non-generative compat. | `fetchNatalInterpretation` deleted; hook body replaced with product-action command; PDF helpers retained as non-generation document utilities only. | `evidence/removal-audit.md`; scan for old POST path and helper PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
