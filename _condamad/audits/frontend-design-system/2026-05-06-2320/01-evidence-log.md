<!-- Journal de preuves pour l'audit frontend design-system apres CS-081. -->

# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Inspected path | Result | Notes |
|---|---|---|---|---|---|
| E-001 | audit_contract | Read skill workflow and contracts | `.agents/skills/condamad-domain-auditor/**` | PASS | Audit run follows read-only domain audit workflow, report contract, story candidate contract and No Legacy/DRY contract. Frontend design-system is an adapted bounded domain. |
| E-002 | guardrail_registry | Read regression guardrails | `_condamad/stories/regression-guardrails.md` | PASS | Applicable frontend invariants `RG-044` through `RG-058` are present. |
| E-003 | repo_status | `git status --short` | repository root | PASS | Worktree was clean before creating this audit folder. |
| E-004 | prior_audit_review | Prior audit review | `_condamad/audits/frontend-design-system/2026-05-04-2238` through `2026-05-06-2139` | PASS | Previous implemented stories moved the residual design-system risk toward hardcoded visual/typography literals after closing cross-page tokens, migration-only namespaces, runtime compatibility and admin redirects. |
| E-005 | test_coverage_inventory | `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | `frontend/` | PASS | 6 files passed; 134 tests passed. |
| E-006 | architecture_guard_inventory | `npm run lint` | `frontend/` | PASS | TypeScript lint configs passed with `tsc --noEmit`. |
| E-007 | runtime_contract_check | `npm run build` | `frontend/` | PASS | Production build passed. Vite reports `assets/index-By5F9VRQ.js` at 1,370.37 kB. |
| E-008 | test_coverage_inventory | `npm run test` | `frontend/` | PASS | Full Vitest suite passed: 115 files, 1252 tests passed, 8 skipped. |
| E-009 | targeted_forbidden_symbol_scan | `rg -n "style=" frontend\src -g "*.tsx"` | `frontend/src` | PASS | Five inline style hits remain and match exact dynamic/style-prop allowlists. |
| E-010 | targeted_forbidden_symbol_scan | `rg -n "var\(\s*--[a-zA-Z0-9_-]+\s*," frontend\src -g "*.css"` | `frontend/src` | PASS | Two CSS fallback hits remain, both `--usage-progress` dynamic exceptions. |
| E-011 | targeted_forbidden_symbol_scan | `rg -n --glob "*.css" -- "--settings-" frontend\src\pages\HelpPage.css` | `frontend/src/pages/HelpPage.css` | PASS | No HelpPage consumption of page-scoped `--settings-*` tokens. |
| E-012 | targeted_forbidden_symbol_scan | Route scan for `/admin/pricing`, `/admin/monitoring`, `/admin/personas` | `frontend/src` | PASS | No active source hit for removed legacy admin routes. |
| E-013 | targeted_forbidden_symbol_scan | `rg -n --glob "*.css" -- "--default_dropshadow\|migration-only\|compatibility\|legacy\|alias" frontend\src` | `frontend/src` | FAIL | One non-test CSS hit remains: `frontend/src/pages/admin/AdminPromptsPage.css:1792` contains `Route legacy : investigation hors catalogue`. |
| E-014 | repo_wide_negative_scan | PCRE2 hardcoded visual/typography scan | `frontend/src`, excluding tests and styles | FAIL | 66 non-test application files outside `frontend/src/styles/**` still contain visual or typography literals. |
| E-015 | static_scan_summary | Top hardcoded literal count by file | `frontend/src` | FAIL | Largest clusters are `App.css` 515 hits, `HelpPage.css` 239, `Settings.css` 193, `AstrologerProfilePage.css` 178, `NatalInterpretation.css` 142 and landing CSS 127+. |

## Command Outputs

### E-005

- Test files: 6 passed.
- Tests: 134 passed.

### E-007

- Build result: PASS.
- Build artifact warning: `assets/index-By5F9VRQ.js` is 1,370.37 kB after minification.

### E-008

- Test files: 115 passed.
- Tests: 1252 passed, 8 skipped.
- Non-failing warnings: jsdom canvas/navigation and React Router future flags.

### E-013

- `frontend/src/pages/admin/AdminPromptsPage.css:1792`: CSS comment contains `Route legacy : investigation hors catalogue`.

### E-014

- Full candidate-file inventory is in `00-audit-report.md` and `03-story-candidates.md`.

## Guardrail Mapping

- `RG-044`, `RG-046`, `RG-050`: E-005, E-006, E-014.
- `RG-045`, `RG-055`, `RG-056`, `RG-058`: E-005, E-014.
- `RG-047`: E-005, E-009.
- `RG-048`: E-005, E-010.
- `RG-049`: E-005, E-013.
- `RG-051`: E-005, E-011.
- `RG-052`: E-005, E-013.
- `RG-053`, `RG-057`: E-005.
- `RG-054`: E-005, E-012.

## Limitations

- The hardcoded-value scan is intentionally broad. It is valid as an exhaustive candidate-file inventory, but each implementation story must inspect the selected cluster and decide which literals belong in global tokens, page-scoped semantic tokens, component-scoped semantic tokens or typed constants.
- No browser screenshot pass was run for this audit because the requested output is a read-only design-system audit and existing visual-smoke tests passed.
