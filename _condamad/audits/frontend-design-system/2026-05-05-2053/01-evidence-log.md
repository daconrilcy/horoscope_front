# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Target | Result | Notes |
|---|---|---|---|---|---|
| E-001 | skill-contract | `Get-Content .agents/skills/condamad-domain-auditor/SKILL.md`, `workflow.md`, references | `.agents/skills/condamad-domain-auditor` | PASS | Read-only audit workflow, output contract, finding taxonomy, evidence profiles, and No Legacy / DRY contract loaded. |
| E-002 | regression-guardrails | `Get-Content _condamad/stories/regression-guardrails.md` | `_condamad/stories/regression-guardrails.md` | PASS | `RG-044` through `RG-050` remain applicable to frontend design-system work. |
| E-003 | targeted-guard-suite | `npm run test -- design-system css-fallback inline-style legacy-style theme-tokens` | `frontend/` | PASS | 5 files, 108 tests passed. |
| E-004 | visual-smoke | `npm run test -- visual-smoke` | `frontend/` | PASS | `visual-smoke.test.tsx` now passes after CS-047. |
| E-005 | full-frontend-tests | `npm run test` | `frontend/` | PASS | 113 files passed, 1234 tests passed, 8 skipped. Console warnings are jsdom/router limitations, not failures. |
| E-006 | lint | `npm run lint` | `frontend/` | PASS | TypeScript lint checks passed for app and node configs. |
| E-007 | build | `npm run build` | `frontend/` | PASS | Build passed; Vite emitted a chunk-size warning for the main JS chunk. |
| E-008 | baseline-audits | Read previous audit reports, finding registers, and story candidates | `_condamad/audits/frontend-design-system/2026-05-04-2238` through `2026-05-05-1942` | PASS | Baseline established: CS-026 through CS-051 were implemented and marked done. |
| E-009 | css-fallback-scan | `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src -g "*.css"` plus allowlist inspection | `frontend/src` | PASS | 53 source lines across 10 CSS files; exact executable allowlist contains 54 fallback entries because nested fallbacks can share a line. |
| E-010 | inline-style-scan | `rg -n "style=\\{" src -g "*.tsx"` plus allowlist inspection | `frontend/src` | PASS | 15 inline style attributes across 9 TSX files; exact allowlists cover every remaining entry. |
| E-011 | hardcoded-visual-scan | `rg -l <hardcoded visual regex> src -g "*.css" -g "*.tsx"` excluding tests and canonical token sources | `frontend/src` | PASS | 106 application files still contain hardcoded visual or typography signals outside canonical token sources and tests. |
| E-012 | legacy-surface-scan | `rg -n <legacy vocabulary regex> src/styles src` and registry inspection | `frontend/src` | PASS | Active design-system legacy surfaces are classified in `legacy-style-surface-registry.md` and token namespace registry. |

## Limitations

- The hardcoded visual scan is intentionally broad. It includes values that may be layout constraints, animation geometry, SVG attributes, or legitimate component dimensions. It is useful for story scoping, not as a direct deletion list.
- The audit is read-only and does not run browser screenshots. Runtime evidence is based on Vitest, TypeScript checks, build output, and static design-system guards.
