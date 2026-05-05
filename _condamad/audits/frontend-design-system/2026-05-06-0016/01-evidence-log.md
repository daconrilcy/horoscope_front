# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Target | Result | Notes |
|---|---|---|---|---|---|
| E-001 | skill-contract | `Get-Content .agents/skills/condamad-domain-auditor/SKILL.md`, `workflow.md`, references | `.agents/skills/condamad-domain-auditor` | PASS | Read-only workflow, output contract, finding taxonomy, evidence profiles, and No Legacy / DRY contract loaded. |
| E-002 | regression-guardrails | `Get-Content _condamad/stories/regression-guardrails.md` | `_condamad/stories/regression-guardrails.md` | PASS | `RG-044` through `RG-050` apply to frontend design-system work. |
| E-003 | targeted-guard-suite | `npm run test -- css-fallback inline-style legacy-style theme-tokens design-system visual-smoke` | `frontend/` | PASS | 6 files, 125 tests passed. |
| E-004 | inline-style-scan | `rg -n "style=\\{" src -g "*.tsx"` plus allowlist inspection | `frontend/src` | PASS | 14 inline style attributes across 9 TSX files; `INLINE_STYLE_EXCEPTIONS` contains 14 entries. |
| E-005 | full-frontend-tests | `npm run test` | `frontend/` | PASS | 113 files passed, 1235 tests passed, 8 skipped. Console warnings are jsdom/router limitations, not failures. |
| E-006 | lint | `npm run lint` | `frontend/` | PASS | TypeScript checks passed for app and node configs. |
| E-007 | build | `npm run build` | `frontend/` | PASS | Build passed; Vite emitted a chunk-size warning for the main JS chunk. |
| E-008 | baseline-audits | Read previous executive summaries and story candidates | `_condamad/audits/frontend-design-system/2026-05-04-2238` through `2026-05-05-2053` | PASS | Baseline established after the implemented frontend design-system stories. |
| E-009 | css-fallback-scan | `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src -g "*.css"` plus allowlist inspection | `frontend/src` | PASS | 23 source lines across 10 CSS files; executable allowlist and markdown registry contain 24 fallback rows. |
| E-010 | inline-allowlist-inspection | `Get-Content src/tests/inline-style-allowlist.ts` and `design-system-allowlist.ts` | `frontend/src/tests` | PASS | Remaining inline styles are exact dynamic or style-prop exceptions. |
| E-011 | hardcoded-visual-scan | `rg -n <hardcoded visual regex> src -g "*.css" -g "*.tsx"` excluding canonical token sources | `frontend/src` | PASS | 5926 matches across 116 files. Broad scan is for story scoping, not direct deletion. |
| E-012 | legacy-surface-scan | `rg -n <legacy vocabulary regex> src/styles src/App.css src/pages/admin/AdminPromptsPage.css` plus registry inspection | `frontend/src` | PASS | 17 active registry rows classify remaining legacy selector and compatibility token surfaces. |

## Limitations

- The hardcoded visual scan is intentionally broad. It includes values that may be layout constraints, animation geometry, SVG attributes, legitimate component dimensions, or test expectations.
- This audit is read-only and does not run browser screenshots. Runtime evidence is based on Vitest, TypeScript checks, build output, and static design-system guards.
