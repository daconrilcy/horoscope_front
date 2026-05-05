# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Inspected path | Result | Notes / Limitations |
|---|---|---|---|---|---|
| E-001 | skill-contract | `Get-Content .agents/skills/condamad-domain-auditor/SKILL.md` plus references | `.agents/skills/condamad-domain-auditor`, `_condamad/stories/regression-guardrails.md` | PASS | Read-only audit, frontend design-system bounded domain, mandatory DRY / No Legacy / guardrail dimensions loaded. |
| E-002 | baseline-audits | `Get-Content` prior audit finding registers | `_condamad/audits/frontend-design-system/2026-05-04-2238`, `2026-05-05-1411`, `2026-05-05-1501`, `2026-05-05-1748` | PASS | Prior findings established baseline: ownership remediated, fallback registry drift existed in `1748`, residual inline/fallback/hardcoded debt remained. |
| E-003 | guard-inventory | `Test-Path` / file inventory for registries and policy tests | `frontend/src/styles`, `frontend/src/tests` | PASS | Guardrail registries and test files exist: token namespace, typography roles, CSS fallback allowlist, legacy style registry, design-system allowlist, CSS fallback policy, inline policy, legacy policy, theme tokens. |
| E-004 | targeted-tests | `npm run test -- design-system css-fallback inline-style legacy-style theme-tokens` | `frontend` | PASS | 5 test files passed, 108 tests passed. Confirms fallback registry parity, inline allowlist, legacy style policy, token roles, and design-system guards. |
| E-005 | lint | `npm run lint` | `frontend` | PASS | TypeScript lint/typecheck completed with exit code 0. |
| E-006 | full-tests | `npm run test` | `frontend` | PASS | 113 test files passed, 1234 tests passed, 8 skipped. Console warnings are React Router future flags, jsdom canvas limitations, and jsdom navigation limitations. |
| E-007 | build | `npm run build` | `frontend` | PASS | Vite build succeeded. Non-blocking warning: one generated JS chunk exceeds 500 kB after minification. |
| E-008 | inline-style-scan | `rg -n "style=" frontend\\src -g "*.tsx"` | `frontend/src` | PASS | 16 inline style attributes remain across 10 TSX files, all covered by the central allowlist according to E-004. |
| E-009 | css-fallback-scan | `rg -n "var\\([^)]*," frontend\\src -g "*.css"` | `frontend/src` | PASS | 117 CSS fallback usages remain across 19 CSS files, all covered by the central allowlist according to E-004. |
| E-010 | hardcoded-visual-scan | `rg -l "#[0-9a-fA-F]{3,8}\|rgba?\\(\|font-size\\s*:\|font-weight\\s*:\|line-height\\s*:\|letter-spacing\\s*:\|border-radius\\s*:\|margin...\|padding...\|gap\\s*:\|box-shadow\\s*:" frontend\\src -g "*.css" -g "*.tsx"` | `frontend/src` | PASS | 109 CSS/TSX files contain hardcoded visual or typography declarations. This is a broad migration surface, not a single runtime failure. |
| E-011 | git-status | `git status --short` | repository root | PASS | Worktree was clean before audit artifact creation. |
