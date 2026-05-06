<!-- Journal de preuves pour l'audit frontend design-system apres refactors CS-071 a CS-073. -->

# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Inspected path | Result | Notes / limitations |
|---|---|---|---|---|---|
| E-001 | architecture_guard_inventory | `_condamad/stories/regression-guardrails.md` | guardrail registry | PASS | `RG-044` a `RG-050` consultes avant classification des findings. |
| E-002 | test_coverage_inventory | `npm run test -- legacy-style ConsultationMigration consultationStore design-system theme-tokens css-fallback inline-style visual-smoke HelpPage` | `frontend` | PASS | 9 files, 149 tests passed. |
| E-003 | check_only_lint | `npm run lint` | `frontend` | PASS | TypeScript lint configs passed. |
| E-004 | build_check | `npm run build` | `frontend` | PASS | Build passed; Vite warned that `assets/index-DDOtgX-E.js` is 1,374.72 kB after minification. |
| E-005 | targeted_forbidden_symbol_scan | `rg -n "\.([a-zA-Z0-9_-]*(legacy\|alias)[a-zA-Z0-9_-]*)\|--default_dropshadow" frontend\src -g "*.css" -g "*.tsx" -g "*.ts"` | `frontend/src` | PASS | Zero active CSS selector or `--default_dropshadow` usage hit. |
| E-006 | targeted_forbidden_symbol_scan | `rg -n "legacy\|Legacy" frontend\src\i18n\consultations.ts` | `frontend/src/i18n/consultations.ts` | PASS | Zero hit; CS-072 removed visible consultation legacy labels from this source. |
| E-007 | targeted_forbidden_symbol_scan | `rg -n "var\(\s*--[a-zA-Z0-9_-]+\s*," frontend\src -g "*.css"` | `frontend/src` | PASS | Exactly two dynamic fallback hits remain, both `--usage-progress`. |
| E-008 | architecture_guard_inventory | `frontend/src/styles/css-fallback-allowlist.md` and `frontend/src/tests/design-system-allowlist.ts` | fallback registry and executable allowlist | PASS | The two `--usage-progress` fallbacks are classified in Markdown and TS allowlist. |
| E-009 | targeted_forbidden_symbol_scan | `rg -n "style=\{" frontend\src -g "*.tsx"` | `frontend/src` | PASS | Exactly five inline-style hits remain and match `INLINE_STYLE_EXCEPTIONS`. |
| E-010 | targeted_forbidden_symbol_scan | `rg --pcre2 --files-with-matches "<hardcoded visual regex>" src --glob "*.css" --glob "*.tsx" --glob "!**/tests/**" --glob "!**/*.test.tsx" --glob "!**/*.test.ts" --glob "!src/styles/**"` | `frontend/src`, excluding tests and `src/styles/**` | FAIL | 101 non-test, non-global-style files still contain hardcoded visual or typography literals. Full file inventory is in `00-audit-report.md`. |
| E-011 | dependency_direction_scan | `rg -n -- "--settings-\|--profile-\|--astro-\|--default_dropshadow" frontend\src\App.css frontend\src\pages\settings\Settings.css frontend\src\pages\AstrologerProfilePage.css frontend\src\pages\HelpPage.css frontend\src\styles\token-namespace-registry.md` | page-scoped token owners and registry | FAIL | `HelpPage.css` consumes `--settings-*`; `--settings-*`, `--profile-*`, `--astro-*` remain migration-only; stale `--default_dropshadow` registry row remains despite zero active usage. |
| E-012 | targeted_forbidden_symbol_scan | `rg -n "mapLegacyConsultationKey\|isLegacy\|buildLegacyBlocks" frontend\src\types\consultation.ts frontend\src\pages\ConsultationWizardPage.tsx frontend\src\pages\ConsultationResultPage.tsx frontend\src\features\consultations\components\ConsultationTypeStep.tsx frontend\src\features\consultations\components\ConsultationFormStep.tsx` | consultation runtime compatibility surface | FAIL | Legacy consultation mapping and result block compatibility remain active after label cleanup. |
| E-013 | targeted_forbidden_symbol_scan | `rg -n "Legacy redirects\|path: \"pricing\"\|path: \"monitoring\"\|path: \"personas\"" frontend\src\app\routes.tsx frontend\src\tests\AdminPage.test.tsx` | admin frontend routes | FAIL | Three legacy admin redirects remain active and tested. |
| E-014 | targeted_forbidden_symbol_scan | `rg -n "Fallback for older API versions\|Legacy codes\|normalizeLegacy\|legacyMap\|buildTimelineFallbackSummary\|Fallback Legacy" frontend\src\utils frontend\src\components\prediction -g "*.ts" -g "*.tsx"` | prediction compatibility mappers | FAIL | Multiple frontend mappers still preserve older API payload compatibility without a frontend legacy-surface registry. |

## Limitations

- This audit did not run Playwright screenshots. It relies on the existing `visual-smoke` Vitest suite for UI smoke evidence.
- The hardcoded-value regex is intentionally broad and must be refined per story before editing. It is still useful as an exhaustive candidate-file inventory for the next bounded migrations.
- Backend/API runtime compatibility was not audited; this run is scoped to the frontend design-system and adjacent frontend legacy surfaces evidenced above.
