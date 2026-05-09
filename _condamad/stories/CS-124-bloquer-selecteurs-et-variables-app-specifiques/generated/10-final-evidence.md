# Final Evidence — CS-124 bloquer-selecteurs-et-variables-app-specifiques

## Story status

- Validation outcome: PASS
- Final status: done
- Capsule path: `_condamad/stories/CS-124-bloquer-selecteurs-et-variables-app-specifiques`
- Source finding closure: full-closure for F-004; no residual in-domain guard work remains.

## AC validation

| AC | Evidence | Status |
|---|---|---|
| AC1 | `app-specificity-guard-before.md` records residual specificity baseline. | PASS |
| AC2 | `frontend/src/tests/design-system-guards.test.ts` blocks App-specific names. | PASS |
| AC3 | `APP_CSS_SPECIFICITY_EXCEPTIONS` is empty; no expiring exception needed. | PASS |
| AC4 | No unclassified No Legacy vocabulary remains in `App.css`. | PASS |
| AC5 | Full design-system and visual smoke suite passes. | PASS |

## Files changed

- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/App.css`
- `_condamad/stories/regression-guardrails.md`
- Story evidence files under this capsule.

## Commands run

| Command | Working directory | Result |
|---|---|---|
| `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | `frontend/` | PASS |
| `npm run test -- ConsultationResultPage ConsultationWizardPage ConsultationsPage AstrologerSelectStep ChatPage ChatComponents HelpPage design-system visual-smoke` | `frontend/` | PASS, 138 tests passed |
| `npm run test` | `frontend/` | PASS, 113 files passed, 1188 passed, 8 skipped |
| `npm run lint` | `frontend/` | PASS |
| `npm run build` | `frontend/` | PASS |
| `rg -n "(astrologer|consultation|dashboard|settings|wizard)" src/App.css` | `frontend/` | PASS, zero hit |
| `rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" src/App.css` | `frontend/` | PASS, zero hit |
| `git diff --check` | repo root | PASS after whitespace fix |
| Story validate + strict lint with venv activated | repo root | PASS |

## Guardrails

- Added `RG-075` to `_condamad/stories/regression-guardrails.md`.
- Applicable existing guardrails preserved: `RG-044` to `RG-050`, `RG-059`, `RG-061`.

## Review/fix loop

- Iteration 1 found validation failures: TypeScript contract mismatches and visual smoke Settings regression.
- Iteration 2 found full-suite regressions: chat/help/consultation i18n and class-name mismatches.
- Final review: CLEAN after lint, targeted tests, full Vitest suite, build, scans and `git diff --check`.

## Remaining risks

- Aucun risque restant identifie.

