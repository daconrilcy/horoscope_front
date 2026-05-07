<!-- Journal de preuves pour l'audit frontend design-system apres refactors. -->

# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Inspected path | Result | Notes |
|---|---|---|---|---|---|
| E-001 | audit_contract | Read skill workflow and contracts | `.agents/skills/condamad-domain-auditor/**` | PASS | Audit run follows read-only domain audit workflow, report contract, story candidate contract and No Legacy/DRY contract. Frontend design-system is an adapted bounded domain. |
| E-002 | guardrail_registry | Read regression guardrails | `_condamad/stories/regression-guardrails.md` | PASS | Applicable frontend invariants `RG-044` through `RG-060` are present. |
| E-003 | repo_status | `git status --short` | repository root | PASS | Worktree was clean before creating this audit folder. |
| E-004 | prior_audit_review | Prior audit review | `_condamad/audits/frontend-design-system/2026-05-04-2238` through `2026-05-06-2320` | PASS | Previous implemented stories moved residual design-system risk toward hardcoded visual/typography literals after closing cross-page tokens, migration-only namespaces, runtime compatibility, admin redirects and CSS comment vocabulary. |
| E-005 | test_coverage_inventory | `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | `frontend/` | PASS | 6 files passed; 136 tests passed. |
| E-006 | architecture_guard_inventory | `npm run lint` | `frontend/` | PASS | TypeScript lint configs passed with `tsc --noEmit`. |
| E-007 | runtime_contract_check | `npm run build` | `frontend/` | PASS | Production build passed. Vite reports `assets/index-BK31TCkH.js` at 1,370.37 kB. |
| E-008 | test_coverage_inventory | `npm run test` | `frontend/` | PASS | Full Vitest suite passed: 115 files, 1254 tests passed, 8 skipped. |
| E-009 | targeted_forbidden_symbol_scan | `rg -n "style=" frontend\src -g "*.tsx"` | `frontend/src` | PASS | Five inline style hits remain and match exact dynamic/style-prop allowlists. |
| E-010 | targeted_forbidden_symbol_scan | `rg -n "var\(\s*--[a-zA-Z0-9_-]+\s*," frontend\src -g "*.css"` | `frontend/src` | PASS | Two CSS fallback hits remain, both `--usage-progress` dynamic exceptions. |
| E-011 | targeted_forbidden_symbol_scan | `rg -n -- "--settings-" frontend\src\pages\HelpPage.css` | `frontend/src/pages/HelpPage.css` | PASS | No HelpPage consumption of page-scoped `--settings-*` tokens. |
| E-012 | targeted_forbidden_symbol_scan | Route scan for `/admin/pricing`, `/admin/monitoring`, `/admin/personas` | `frontend/src` | PASS | No active source hit for removed legacy admin routes. |
| E-013 | targeted_forbidden_symbol_scan | CSS comment vocabulary scan for `legacy`, `compatibility`, `alias`, `shim`, `fallback`, `migration-only` | `frontend/src/**/*.css` | PASS | No CSS comment vocabulary hits remain. |
| E-014 | targeted_forbidden_symbol_scan | Runtime compatibility vocabulary scan for CS-080 terms | `frontend/src` | PASS | No active source hit for `Deprecated:`, backward compatibility wording, `legacy fallback`, `Legacy codes`, `aspectLegacy` or `compatibility`. |
| E-015 | repo_wide_negative_scan | Hardcoded visual/typography scan using color, shadow, radius and typography literal patterns | `frontend/src`, excluding tests and styles | FAIL | 68 non-test application files outside `frontend/src/styles/**` still contain visual or typography literals. |
| E-016 | static_scan_summary | Top hardcoded literal count by file | `frontend/src` | FAIL | Largest clusters are `App.css` 563 hits, `HelpPage.css` 296, `Settings.css` 237, `AstrologerProfilePage.css` 214, `LandingPage.css` 161 and `NatalInterpretation.css` 154. |

## Command Outputs

### E-005

- Test files: 6 passed.
- Tests: 136 passed.

### E-007

- Build result: PASS.
- Build artifact warning: `assets/index-BK31TCkH.js` is 1,370.37 kB after minification.

### E-008

- Test files: 115 passed.
- Tests: 1254 passed, 8 skipped.
- Non-failing warnings: jsdom canvas/navigation and React Router future flags.

### E-009

- `frontend/src/layouts/TwoColumnLayout.tsx:22`
- `frontend/src/components/DomainRankingCard.tsx:48`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx:139`
- `frontend/src/components/ui/Skeleton/Skeleton.tsx:26`
- `frontend/src/components/ui/Skeleton/Skeleton.tsx:53`

### E-010

- `frontend/src/App.css:3156`
- `frontend/src/pages/settings/Settings.css:1052`

### E-013

- Result: `NO CSS COMMENT VOCABULARY HITS`.

### E-015

- Full candidate-file inventory is in `00-audit-report.md` and `03-story-candidates.md`.

## Guardrail Mapping

- `RG-044`, `RG-046`, `RG-050`: E-005, E-006, E-015.
- `RG-045`, `RG-055`, `RG-056`, `RG-058`, `RG-059`: E-005, E-015.
- `RG-047`: E-005, E-009.
- `RG-048`: E-005, E-010.
- `RG-049`: E-005, E-013.
- `RG-051`: E-005, E-011.
- `RG-052`: E-005, E-013.
- `RG-053`, `RG-057`: E-005, E-014.
- `RG-054`: E-005, E-012.
- `RG-060`: E-005, E-013.

## Limitations

- The hardcoded-value scan is intentionally broad. It is valid as an exhaustive candidate-file inventory, but each implementation story must inspect the selected cluster and decide which literals belong in global tokens, page-scoped semantic tokens, component-scoped semantic tokens, typed constants or existing semantic owner blocks.
- No browser screenshot pass was run for this audit because the requested output is a read-only design-system audit and existing visual-smoke tests passed.
