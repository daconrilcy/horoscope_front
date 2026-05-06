<!-- Journal des preuves de l'audit frontend design-system. -->

# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Inspected path | Result | Notes |
|---|---|---|---|---|---|
| E-001 | repo_status | `git status --short` | repository root | PASS | Worktree clean before writing audit artifacts. |
| E-002 | guardrail_registry | `_condamad/stories/regression-guardrails.md` | `RG-044` through `RG-057` | PASS | Applicable frontend design-system and compatibility invariants were read before findings. |
| E-003 | test_coverage_inventory | `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke ConsultationMigration consultationStore TurningPointsEnriched DailyHoroscopePage AdminPage` | `frontend` | PASS | 11 test files and 192 tests passed. JSDOM emitted existing canvas `getContext` warnings. |
| E-004 | architecture_guard_inventory | `npm run lint` | `frontend` | PASS | TypeScript lint command completed successfully. |
| E-005 | runtime_contract_check | `npm run build` | `frontend` | PASS | Production build completed; main JS chunk reported at 1,370.37 kB, above the 500 kB warning threshold. |
| E-006 | dependency_direction_scan | `rg -n -- "--settings-" frontend/src/pages/HelpPage.css frontend/src` | `frontend/src` | PASS | Hits are limited to `token-namespace-registry.md`, `Settings.css`, and the guard test; no HelpPage use remains. |
| E-007 | targeted_forbidden_symbol_scan | `rg -n "Deprecated:\|backwards compatibility\|backward compatibility\|legacy fallback\|Legacy codes\|aspectLegacy\|compatibility" frontend/src` | `frontend/src` | PASS | Zero runtime/source hits for the CS-080 forbidden vocabulary. |
| E-008 | targeted_forbidden_symbol_scan | `rg -n "admin/pricing\|admin/monitoring\|admin/personas" frontend/src` | `frontend/src` | PASS | Zero hits for removed admin legacy paths. |
| E-009 | targeted_forbidden_symbol_scan | `rg -n -- "--default_dropshadow\|migration-only" frontend/src/styles frontend/src/tests` | style registries and guard tests | PASS | No `--default_dropshadow`; `migration-only` appears only in registry prose and guard expectations, not active token rows. |
| E-010 | targeted_forbidden_symbol_scan | `rg -n "style=\{" frontend/src -g "*.tsx"` | `frontend/src` | PASS | Exactly five inline style hits remain, matching allowlisted dynamic/style-prop exceptions. |
| E-011 | targeted_forbidden_symbol_scan | `rg -n "var\(\s*--[a-zA-Z0-9_-]+\s*," frontend/src -g "*.css"` | `frontend/src` | PASS | Exactly two CSS fallback hits remain: `--usage-progress` dynamic bridges in `App.css` and `Settings.css`. |
| E-012 | targeted_forbidden_symbol_scan | broad PCRE2 hardcoded visual/typography scan | `frontend/src`, excluding tests and styles | FAIL | 98 non-test application files still contain literal visual or typography values; full inventory is in `00-audit-report.md`. |

## Command Outputs

### E-003

- Test files: 11 passed.
- Tests: 192 passed.
- Notable warning: repeated JSDOM `HTMLCanvasElement.getContext()` not implemented messages during visual smoke coverage.

### E-005

- Build artifact warning: `assets/index-D7XVvH_X.js` is 1,370.37 kB after minification.
- Build result: PASS.

### E-010 Inline Style Hits

- `frontend/src/layouts/TwoColumnLayout.tsx:22`
- `frontend/src/components/DomainRankingCard.tsx:48`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx:139`
- `frontend/src/components/ui/Skeleton/Skeleton.tsx:26`
- `frontend/src/components/ui/Skeleton/Skeleton.tsx:53`

### E-011 CSS Fallback Hits

- `frontend/src/App.css:3124`
- `frontend/src/pages/settings/Settings.css:1052`

## Guardrail Mapping

- `RG-044`, `RG-046`, `RG-050`: E-003, E-004, E-012.
- `RG-045`, `RG-055`, `RG-056`: E-003, E-012.
- `RG-047`: E-003, E-010.
- `RG-048`: E-003, E-011.
- `RG-049`: E-003, E-009.
- `RG-051`: E-003, E-006.
- `RG-052`: E-003, E-009.
- `RG-053`, `RG-057`: E-003, E-007.
- `RG-054`: E-003, E-008.

## Limitations

- The hardcoded-value scan is intentionally broad. It is valid as an exhaustive candidate-file inventory, but each implementation story must inspect the selected cluster and decide which literals belong in global tokens, page-scoped semantic tokens, component-scoped semantic tokens or typed constants.
- No browser visual screenshot pass was run for this audit because the requested output is a read-only design-system audit and existing visual-smoke tests passed.
