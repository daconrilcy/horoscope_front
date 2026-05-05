# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Inspected path | Result | Notes / Limitations |
|---|---|---|---|---|---|
| E-001 | guardrail-source | `rg -n "RG-04[4-9]\|RG-050" _condamad\stories\regression-guardrails.md` | `_condamad/stories/regression-guardrails.md` | PASS | `RG-044` through `RG-050` remain active for frontend token namespaces, hardcoded values, typography, inline styles, CSS fallbacks, legacy surfaces, and anti-drift guards. |
| E-002 | story-inventory | `Get-ChildItem -LiteralPath '_condamad\stories' -Directory ...` | `_condamad/stories` | PASS | Frontend stories `CS-026` through `CS-032`, plus cleanup stories `CS-034` and `CS-035`, are present. |
| E-003 | registry-inventory | `rg --files frontend/src/styles frontend/src/tests ...` | `frontend/src/styles`, `frontend/src/tests` | PASS | Registries exist for token namespaces, typography roles, CSS fallback allowlist, legacy style surface registry, inline-style allowlist, and design-system guard allowlist. |
| E-004 | guard-source-review | `Get-Content frontend\src\tests\design-system-guards.test.ts`, `inline-style-policy.test.ts`, `css-fallback-policy.test.ts` | `frontend/src/tests` | PASS | Guard tests validate token namespace classification, typography roles, migrated hardcoded literals, inline-style exceptions, and CSS fallback exceptions. |
| E-005 | targeted-tests | `npm run test -- design-system inline-style css-fallback legacy-style theme-tokens` | `frontend` | PASS | Vitest reported 5 files passed and 108 tests passed. |
| E-006 | lint | `npm run lint` | `frontend` | PASS | TypeScript lint scripts completed successfully. |
| E-007 | build | `npm run build` | `frontend` | PASS | Production build passed; Vite warned that the main chunk is larger than 500 kB after minification. |
| E-008 | full-tests | `npm run test` | `frontend` | PASS | Vitest reported 113 test files passed, 1234 tests passed, and 8 skipped. The previous `HelpPage.test.tsx` full-run failure was not reproduced. |
| E-009 | inline-style-count | `(rg -n "style=\{" frontend/src -g "*.tsx" \| Measure-Object).Count` | `frontend/src` | PASS | 68 TSX `style` attributes remain, down from 85 in the previous audit. |
| E-010 | inline-style-scan | `rg -n "style=\{" frontend/src/components/prediction/TurningPointsList.tsx ...` | selected TSX files | FAIL | Static inline style debt remains in `TurningPointsList.tsx`, `AccountSettings.tsx`, `AstrologerProfilePage.tsx`, and `NotFoundPage.tsx`. |
| E-011 | css-fallback-count | `(rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," frontend/src -g "*.css" \| Measure-Object).Count` | `frontend/src` | PASS | 262 CSS variable fallback usages remain, down from 329 in the previous audit. |
| E-012 | css-fallback-scan | `rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," frontend/src/components/ui/Select/Select.css ...` | selected CSS files | FAIL | Fallbacks remain in shared UI and page CSS, including `Select`, `Modal`, `Card`, `Field`, `Button`, `UserAvatar`, `LockedSection`, `EmptyState`, `Skeleton`, `HelpPage.css`, and `App.css`. |
| E-013 | color-scan | `(rg -n "#[0-9A-Fa-f]{3,8}\b\|rgba?\(\|hsla?\(" frontend/src ... \| Measure-Object).Count` | `frontend/src` excluding core token CSS | FAIL | 1899 color-like hits remain outside `design-tokens.css`, `theme.css`, and `premium-theme.css`. |
| E-014 | visual-declaration-scan | `(rg -n "(?i)(margin\|padding\|gap\|border-radius\|box-shadow\|font-size\|font-weight\|line-height\|letter-spacing)\s*:" frontend/src -g "*.css" \| Measure-Object).Count` | `frontend/src` CSS | FAIL | 4172 visual or typography declarations remain in CSS. This broad count includes both acceptable component CSS and remaining non-tokenized debt. |
| E-015 | migrated-batch-scan | `rg -n "border-radius:\s*999px;\|gap:\s*(8px\|12px);" frontend/src/App.css ...` | CS-027 migrated files | PASS | No hits found for the exact migrated literal regressions in the guarded batch. |

## Limitations

- Static counts are broad indicators and include legitimate CSS declarations. Findings use them as drift/debt evidence only when combined with guard and allowlist evidence.
- No browser visual regression run was executed because the requested audit is read-only and the relevant guard/lint/build/test commands passed.
