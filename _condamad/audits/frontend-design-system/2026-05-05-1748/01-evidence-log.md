# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Inspected path | Result | Notes / Limitations |
|---|---|---|---|---|---|
| E-001 | guardrail-source | `Get-Content _condamad\stories\regression-guardrails.md` | `_condamad/stories/regression-guardrails.md` | PASS | `RG-044` through `RG-050` remain active for frontend token namespaces, hardcoded values, typography, inline styles, CSS fallbacks, legacy surfaces, and anti-drift guards. |
| E-002 | registry-inventory | `Get-ChildItem frontend\src\styles` | `frontend/src/styles` | PASS | Registries exist for token namespaces, typography roles, CSS fallback allowlist, legacy style surface registry, design tokens, theme, premium theme, utilities, glass, and backgrounds. |
| E-003 | guard-source-review | `Get-Content frontend\src\tests\design-system-guards.test.ts`, `css-fallback-policy.test.ts`, `inline-style-policy.test.ts`, `legacy-style-policy.test.ts` | `frontend/src/tests` | PASS | Guard tests validate token namespace classification, typography roles, migrated hardcoded literals, inline-style exceptions, CSS fallback exceptions, and legacy selector registry entries. |
| E-004 | targeted-tests | `npm run test -- design-system theme-tokens inline-style css-fallback legacy-style` | `frontend` | PASS | Vitest reported 5 files passed and 108 tests passed. |
| E-005 | lint | `npm run lint` | `frontend` | PASS | TypeScript lint scripts completed successfully. |
| E-006 | build | `npm run build` | `frontend` | PASS | Production build passed; Vite warned that `assets/index-DOSLloov.js` is larger than 500 kB after minification. |
| E-007 | full-tests | `npm run test` | `frontend` | PASS | Vitest reported 113 test files passed, 1234 tests passed, and 8 skipped. The previous `HelpPage.test.tsx` full-run failure was not reproduced. |
| E-008 | inline-style-count | `(rg -n "style=\{" frontend/src -g "*.tsx" \| Measure-Object).Count` | `frontend/src` | FAIL | 30 TSX `style` attributes remain. They are allowlisted, but several preserve static layout/color declarations in TSX. |
| E-009 | inline-style-file-list | `rg -l "style=\{" frontend/src -g "*.tsx"` | `frontend/src` | FAIL | 17 TSX files still contain `style` attributes; full file list is in `00-audit-report.md`. |
| E-010 | css-fallback-count | `(rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," frontend/src -g "*.css" \| Measure-Object).Count` | `frontend/src` | FAIL | 165 CSS variable fallback usages remain. They are executable-allowlisted, but remain compatibility or migration debt. |
| E-011 | css-fallback-file-list | `rg -l "var\(\s*--[A-Za-z0-9_-]+\s*," frontend/src -g "*.css"` | `frontend/src` | FAIL | 30 CSS files still contain fallback literals; full file list is in `00-audit-report.md`. |
| E-012 | visual-counts | Static `rg` counts for color, typography, spacing, radius, and shadow declarations | `frontend/src` | FAIL | Counts: 1671 color-like hits, 1570 typography declaration hits, 2653 spacing/radius/shadow declaration hits. Broad counts include legitimate CSS and are used only as debt indicators. |
| E-013 | markdown-fallback-registry | `Get-Content frontend\src\styles\css-fallback-allowlist.md` | `frontend/src/styles/css-fallback-allowlist.md` | FAIL | The markdown says it is an exact allowlist but currently documents only 7 rows. |
| E-014 | executable-fallback-allowlist | `Get-Content frontend\src\tests\design-system-allowlist.ts` | `frontend/src/tests/design-system-allowlist.ts` | PASS | `CSS_FALLBACK_EXCEPTIONS` contains the executable fallback contract used by guards and covers the current 165 fallback entries. |
| E-015 | migrated-batch-guard | `Get-Content frontend\src\tests\design-system-guards.test.ts` | `frontend/src/tests/design-system-guards.test.ts` | PASS | Guard keeps exact migrated literals from CS-027 out of `App.css`, `AdminPromptsPage.css`, `HelpPage.css`, `Settings.css`, and `AstrologerProfilePage.css`. |
| E-016 | git-status | `git status --short` | repository root | PASS | No pre-existing dirty worktree output was reported before writing audit artifacts. |

## Limitations

- Static counts are broad indicators and include legitimate component CSS. Findings classify them as migration/debt evidence only when combined with guard, registry, and allowlist evidence.
- No browser visual regression run was executed because the requested work was a read-only domain audit and frontend lint/build/tests passed.
