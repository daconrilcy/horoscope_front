# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Target | Result | Notes |
|---|---|---|---|---|---|
| E-001 | skill-contract | `Get-Content -Raw .\.agents\skills\condamad-domain-auditor\SKILL.md` | `.agents/skills/condamad-domain-auditor/SKILL.md` | PASS | Skill loaded; read-only code audit, writes limited to `_condamad/audits/**`. |
| E-002 | regression-guardrails | `Get-Content -Raw _condamad\stories\regression-guardrails.md` | `_condamad/stories/regression-guardrails.md` | PASS | `RG-044` through `RG-050` apply to frontend design-system governance. |
| E-003 | targeted-guard-suite | `npm run test -- css-fallback inline-style legacy-style theme-tokens design-system visual-smoke` | `frontend` | PASS | 6 test files, 126 tests passed. |
| E-004 | full-frontend-tests | `npm run test` | `frontend` | PASS | 114 test files, 1238 tests passed, 8 skipped; non-failing React Router/jsdom warnings remain. |
| E-005 | lint | `npm run lint` | `frontend` | PASS | TypeScript lint/typecheck scripts passed. |
| E-006 | build | `npm run build` | `frontend` | PASS | Build passed; Vite chunk-size warning remains on `index-*.js` around 1374 kB minified. |
| E-007 | package-scripts | `Get-Content -Raw frontend\package.json` | `frontend/package.json` | PASS | Frontend scripts are `test`, `lint`, `build`; no formatter was run. |
| E-008 | baseline-audits | Review of requested audit folders plus `2026-05-06-0108` | `_condamad/audits/frontend-design-system/*` | PASS | Prior implemented stories compared with current scans. |
| E-009 | css-fallback-scan | `rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," frontend\src -g "*.css"` | `frontend/src/**/*.css` | FAIL | 3 active fallback lines remain: `App.css`, `Settings.css`, `AdminEntitlementsPage.css`. |
| E-010 | inline-style-scan | `rg -n "style=\{" frontend\src -g "*.tsx"` | `frontend/src/**/*.tsx` | FAIL | 6 active inline style attributes remain in 6 TSX files. |
| E-011 | hardcoded-visual-scan | `rg -l "...visual literal regex..." frontend\src --glob "*.css" --glob "*.tsx" --glob "!**/styles/design-tokens.css" --glob "!**/styles/theme.css" --glob "!**/styles/premium-theme.css"` | `frontend/src` | FAIL | 113 files contain broad hardcoded visual or typography signals outside main token source files. Broad signal requires per-story classification. |
| E-012 | registry-inspection | `Get-Content -Raw` on token, typography, fallback, inline and legacy registries | `frontend/src/styles`, `frontend/src/tests` | PASS | Registries and executable allowlists are exact for current guards. |
| E-013 | legacy-surface-scan | `rg -n "legacy OR --text- OR --glass OR --primary" frontend\src\styles frontend\src\App.css frontend\src\pages\admin\AdminPromptsPage.css` | legacy selectors and compatibility aliases | FAIL | Admin prompt legacy selectors and compatibility token aliases remain classified. |
| E-014 | premium-token-scan | `rg -n -e "--premium-text-muted" -e "--premium-glass-border-soft" -e "--premium-radius-pill" frontend\src\styles\premium-theme.css frontend\src\pages\NatalChartPage.css frontend\src\components\NatalInterpretation.css` | premium tokens and consumers | PASS | Premium tokens consumed by natal surfaces are now declared in `premium-theme.css`. |
| E-015 | git-status | `git status --short` | repository root | PASS | No pre-existing uncommitted changes were present before audit artifact writes. |

## Guardrail Mapping

- `RG-044`: evidenced by `token-namespace-registry.md`, `theme-tokens.test.ts`, and `design-system-guards.test.ts`.
- `RG-045`: evidenced by hardcoded visual scan and design-system tests.
- `RG-046`: evidenced by `typography-roles.md`, `visual-smoke.test.tsx`, and design-system tests.
- `RG-047`: evidenced by inline style scan, `inline-style-allowlist.ts`, and `inline-style-policy.test.ts`.
- `RG-048`: evidenced by fallback scan, `css-fallback-allowlist.md`, and `css-fallback-policy.test.ts`.
- `RG-049`: evidenced by `legacy-style-surface-registry.md` and `legacy-style-policy.test.ts`.
- `RG-050`: evidenced by the targeted design-system guard suite.
