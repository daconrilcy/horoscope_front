<!-- Journal des preuves de l'audit frontend design-system apres refactors. -->

# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Inspected path | Result | Notes |
|---|---|---|---|---|---|
| E-001 | guardrail_registry | Read regression guardrails | `_condamad/stories/regression-guardrails.md` | PASS | `RG-044` through `RG-060` consulted; frontend design-system invariants are active. |
| E-002 | prior_story_evidence | Read delivered story final evidence and after artifacts | `_condamad/stories/CS-073*` through `_condamad/stories/CS-085*` | PASS | Delivered evidence exists for Help, runtime compatibility, admin route cleanup, prediction premium, UI shared, Chat, App, Settings and Landing clusters. |
| E-003 | test_coverage_inventory | `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke App FaqSection` | `frontend/` | PASS | 11 test files, 203 tests passed. React Router future warnings and jsdom canvas warnings are test-environment limitations, not failures. |
| E-004 | test_coverage_inventory | `npm run test` | `frontend/` | PASS | 115 test files, 1258 tests passed, 8 skipped. |
| E-005 | architecture_guard_inventory | `npm run lint` | `frontend/` | PASS | TypeScript lint/typecheck scripts passed. |
| E-006 | runtime_contract_check | `npm run build` | `frontend/` | PASS | Build passed; Vite emitted chunk-size warning for `assets/index-Dg5Awx35.js` at 1,370.45 kB. |
| E-007 | repo_wide_negative_scan | `rg --pcre2 -l "...literal scan..." src --glob "*.css" --glob "!src/styles/**"` | `frontend/src` | FAIL | Raw scan finds 86 CSS application files with visual/typography literal candidates. This includes already-closed owner blocks and therefore overstates actionable debt. |
| E-008 | derived_inventory | Raw CSS scan minus closed clusters evidenced by exact guards | `frontend/src` | FAIL | 50 CSS files remain actionably unclosed for hardcoded visual/typography ownership. |
| E-009 | targeted_forbidden_symbol_scan | `rg -n "style=\\{" src --glob "*.tsx"` | `frontend/src` | PASS | 5 inline style hits; all are existing exact dynamic exceptions in `frontend/src/tests/design-system-allowlist.ts` or `inline-style-allowlist.ts`. |
| E-010 | targeted_forbidden_symbol_scan | No Legacy vocabulary scan over CSS files | `frontend/src` | PASS | Hits are legitimate fallback UI class names, shimmer keyframes, or admin prompt graph domain terms already covered by current guards; no new stale design-system vocabulary finding. |

## Raw CSS Scan Result

The raw scan is intentionally broad. It proves that literal candidates still exist, but it is not by itself the actionable file list because already-migrated clusters keep owner blocks with semantic variables.

- Raw files: 86.
- Closed by exact guard/final evidence: 36.
- Residual actionable files: 50.

## Limitations

- Browser visual screenshots were not rerun for this audit; `visual-smoke.test.tsx` and build evidence were used as executable frontend rendering guards.
- The audit is read-only and did not modify application code.
