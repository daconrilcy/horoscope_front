# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Target | Result | Notes |
|---|---|---|---|---|---|
| E-001 | skill-contract | `Get-Content -Raw .\.agents\skills\condamad-domain-auditor\SKILL.md` | `.agents/skills/condamad-domain-auditor/SKILL.md` | PASS | Skill loaded; audit is read-only except `_condamad/audits/**`. |
| E-002 | regression-guardrails | `Get-Content -Raw _condamad\stories\regression-guardrails.md` | `_condamad/stories/regression-guardrails.md` | PASS | `RG-044` through `RG-050` apply to frontend design-system governance. |
| E-003 | targeted-guard-suite | `npm run test -- css-fallback inline-style legacy-style theme-tokens design-system visual-smoke` | `frontend` | PASS | 6 test files, 126 tests passed. |
| E-004 | full-frontend-tests | `npm run test` | `frontend` | PASS | 114 test files, 1238 tests passed, 8 skipped. Console warnings remain non-failing. |
| E-005 | lint | `npm run lint` | `frontend` | PASS | TypeScript lint/typecheck scripts passed. |
| E-006 | build | `npm run build` | `frontend` | PASS | Build passed; Vite chunk-size warning remains. |
| E-007 | package-scripts | `Get-Content -Raw frontend\package.json` | `frontend/package.json` | PASS | Frontend scripts are `test`, `lint`, `build`; no formatter was run. |
| E-008 | baseline-audits | Baseline audit review | `_condamad/audits/frontend-design-system/*` | PASS | Prior stories and findings reviewed to compare remaining surfaces after refactors. |
| E-009 | css-fallback-scan | `rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," frontend\src -g "*.css"` | `frontend/src/**/*.css` | FAIL | 10 active fallback lines remain in 9 CSS files. |
| E-010 | inline-style-scan | `rg -n "style=\{" frontend\src -g "*.tsx"` | `frontend/src/**/*.tsx` | FAIL | 9 active inline style attributes remain in 6 TSX files. |
| E-011 | hardcoded-visual-scan | `rg -l "...visual literal regex..." frontend\src --glob "*.css" --glob "*.tsx" --glob "!**/styles/design-tokens.css" --glob "!**/styles/theme.css" --glob "!**/styles/premium-theme.css"` | `frontend/src` | FAIL | 110 files contain broad hardcoded visual or typography signals outside main token source files. This is a broad signal and needs per-story classification. |
| E-012 | registry-inspection | `Get-Content -Raw` on design-system registries and allowlists | `frontend/src/styles`, `frontend/src/tests` | PASS | Registries and executable allowlists are exact enough for current guards. |
| E-013 | legacy-surface-scan | `rg -n legacy-or-token-alias-pattern frontend\src\styles frontend\src\App.css frontend\src\pages\admin\AdminPromptsPage.css` | legacy selectors and compatibility aliases | FAIL | Admin prompt legacy selectors and compatibility token aliases remain classified. |
| E-014 | premium-token-scan | `rg -n -e "--premium-text-muted" -e "--premium-glass-border-soft" -e "--premium-radius-pill" ...` | premium theme and premium consumers | FAIL | `--premium-radius-pill` exists; `--premium-text-muted` and `--premium-glass-border-soft` are consumed but not declared in `premium-theme.css`. |
| E-015 | git-status | `git status --short` | repository root | PASS | No pre-existing uncommitted changes were present before the audit artifact writes. |

## Guardrail Mapping

- `RG-044`: evidenced by `token-namespace-registry.md`, `theme-tokens.test.ts`, and `design-system-guards.test.ts`.
- `RG-045`: evidenced by the hardcoded value scan and design-system tests.
- `RG-046`: evidenced by `typography-roles.md`, `visual-smoke.test.tsx`, and design-system tests.
- `RG-047`: evidenced by inline style scan, `inline-style-allowlist.ts`, and `inline-style-policy.test.ts`.
- `RG-048`: evidenced by fallback scan, `css-fallback-allowlist.md`, and `css-fallback-policy.test.ts`.
- `RG-049`: evidenced by `legacy-style-surface-registry.md` and `legacy-style-policy.test.ts`.
- `RG-050`: evidenced by the targeted design-system guard suite.
