<!-- Journal de preuves pour le nouvel audit frontend design-system apres refactors. -->

# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Inspected path | Result | Notes |
|---|---|---|---|---|---|
| E-001 | audit_contract | Read `condamad-domain-auditor` workflow and contracts | `.agents/skills/condamad-domain-auditor/**` | PASS | Read-only audit workflow, report contract, story candidate contract and No Legacy/DRY contract were applied to the bounded `frontend-design-system` domain. |
| E-002 | guardrail_registry | Read regression guardrails | `_condamad/stories/regression-guardrails.md` | PASS | Frontend design-system invariants `RG-044` through `RG-060` are present and applicable. |
| E-003 | repo_status | `git status --short` | repository root | PASS | Worktree was clean before this audit folder was created. |
| E-004 | prior_audit_review | Prior frontend design-system audits | `_condamad/audits/frontend-design-system/2026-05-04-2238` through `2026-05-07-0017` | PASS | Implemented stories closed cross-page token consumption, migration-only namespaces, runtime compatibility, legacy admin redirects, CSS No Legacy vocabulary, and several hardcoded-value clusters. |
| E-005 | test_coverage_inventory | `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | `frontend/` | PASS | 6 test files passed; 138 tests passed. |
| E-006 | architecture_guard_inventory | `npm run lint` | `frontend/` | PASS | TypeScript lint configs passed with `tsc --noEmit`. |
| E-007 | runtime_contract_check | `npm run build` | `frontend/` | PASS | Production build passed; Vite still reports the main JS chunk above 500 kB. |
| E-008 | test_coverage_inventory | `npm run test` | `frontend/` | PASS | Full Vitest suite passed: 115 files, 1256 tests passed, 8 skipped. |
| E-009 | targeted_forbidden_symbol_scan | `rg -n "style=" frontend/src -g "*.tsx"` | `frontend/src` | PASS | Five inline style hits remain and match the exact dynamic/style-prop allowlists. |
| E-010 | targeted_forbidden_symbol_scan | `rg -n "var\(\s*--[a-zA-Z0-9_-]+\s*," frontend/src -g "*.css"` | `frontend/src` | PASS | Two CSS fallback hits remain, both `--usage-progress` dynamic exceptions. |
| E-011 | targeted_forbidden_symbol_scan | `rg -n "\b(?:legacy\|compatibility\|alias\|shim\|fallback\|migration-only)\b" frontend/src -g "*.css"` | `frontend/src` | PASS | Active CSS No Legacy vocabulary is limited to classified selector names and guarded tests/registries; CSS comment vocabulary is covered by `legacy-style-policy`. |
| E-012 | targeted_forbidden_symbol_scan | `rg -n -- "--settings-" frontend/src -g "*.css"` | `frontend/src` | PASS | `--settings-*` usage is page-scoped to `frontend/src/pages/settings/Settings.css` plus tests/registry evidence. |
| E-013 | repo_wide_negative_scan | Hardcoded visual/typography scan using color, shadow, radius and typography literal patterns | `frontend/src`, CSS files outside `frontend/src/styles/**` | FAIL | 70 CSS application files still contain hardcoded visual or typography literals and require cluster-by-cluster classification or migration. |

## Command Outputs

### E-005

- Test files: 6 passed.
- Tests: 138 passed.

### E-007

- Build result: PASS.
- Warning: `assets/index-tzuNTTVF.js` is 1,370.37 kB after minification, above Vite's 500 kB chunk warning threshold.

### E-008

- Test files: 115 passed.
- Tests: 1256 passed, 8 skipped.
- Non-failing warnings: jsdom canvas/navigation limitations and React Router future flag warnings.

### E-009

- `frontend/src/layouts/TwoColumnLayout.tsx:22`
- `frontend/src/components/DomainRankingCard.tsx:48`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx:139`
- `frontend/src/components/ui/Skeleton/Skeleton.tsx:26`
- `frontend/src/components/ui/Skeleton/Skeleton.tsx:53`

### E-010

- `frontend/src/App.css:3156`
- `frontend/src/pages/settings/Settings.css:1205`

## Guardrail Mapping

- `RG-044`, `RG-046`, `RG-050`: E-005, E-006, E-013.
- `RG-045`, `RG-055`, `RG-056`, `RG-058`, `RG-059`: E-005, E-013.
- `RG-047`: E-005, E-009.
- `RG-048`: E-005, E-010.
- `RG-049`: E-005, E-011.
- `RG-051`: E-005, E-012.
- `RG-052`: E-005, E-011.
- `RG-053`, `RG-057`: E-005, E-011.
- `RG-054`: E-005 and prior route tests from E-008.
- `RG-060`: E-005, E-011.

## Limitations

- The hardcoded-value scan is intentionally broad. Each implementation story must inspect the selected cluster and decide which literals are legitimate semantic owner declarations versus values to promote to global tokens, semantic tokens, typography roles, typed runtime constants, or existing CSS variables.
- No browser screenshot pass was run because this audit is read-only and the existing Vitest visual-smoke suite passed.
