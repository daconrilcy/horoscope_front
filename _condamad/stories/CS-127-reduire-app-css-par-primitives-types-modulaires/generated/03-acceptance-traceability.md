# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Baseline records current App CSS metrics. | Add before metrics artifact. | `app-css-size-and-duplication-before.md`. | PASS |
| AC2 | `App.css` is below `2600` lines or reduced by at least `35%`. | Replace `App.css` body with typed imports and move CSS to `styles/app/**`. | `App.css` is 12 lines; `app-css-size-and-duplication-after.md`. | PASS |
| AC3 | Modules are grouped by type under `frontend/src/styles/app/`. | Add approved module files only and filename guard. | `npm run test -- design-system`; `rg --files src/styles/app`. | PASS |
| AC4 | Repeated UI patterns use primitives. | Add primitives such as `.notice`, `.state-centered`, `.select-card`, `.form-control`, `.stack`, `.cluster`. | primitive scan and `visual-smoke`. | PASS |
| AC5 | Token scales use generic names where migrated. | Keep/apply generic app token scale and block mechanical new names. | `theme-tokens`; mechanical-token scan has no hits. | PASS |
| AC6 | No migrated selector remains as an alias. | Remove or avoid alias/wrapper patterns. | Legacy/alias vocabulary scan has no hits in App CSS surface. | PASS |
| AC7 | App CSS guard prevents listed regressions. | Update `design-system-guards.test.ts` with required guard names. | `npm run test -- design-system`. | PASS |
| AC8 | Frontend validates after className migration. | Update low-risk TSX consumers and keep runtime stable. | `npm run lint`; `npm run build`; targeted Vitest command. | PASS |
| AC9 | Single-use custom properties are removed or justified. | Add variable usage artifact and guard. | `app-css-variable-usage.md`; design-system guard. | PASS |
| AC10 | JSX uses primitive class composition. | Compose primitives in selected TSX consumers. | primitive TSX scan. | PASS |
| AC11 | TSX consumers are migrated for every changed CSS class. | Add mapping artifact and stale consumer guard. | design-system guard and `app-css-tsx-consumers.md`. | PASS |
| AC12 | Total App CSS surface reduces duplicate bodies by 30%. | Merge/extract duplicated bodies and guard total surface. | duplicate bodies reduced 27 -> 10. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
