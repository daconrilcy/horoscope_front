# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Inspected path | Result | Notes / Limitations |
|---|---|---|---|---|---|
| E-001 | baseline-audits | Read previous audit summaries and finding registers | `_condamad/audits/frontend-design-system/2026-05-04-2238`, `2026-05-05-1411`, `2026-05-05-1501`, `2026-05-05-1748`, `2026-05-05-1831` | PASS | Baseline established: prior High risks closed; residual debt focused on fallbacks, inline styles, hardcoded values. |
| E-002 | guardrail-registry | Read regression guardrail registry | `_condamad/stories/regression-guardrails.md` | PASS | `RG-044` through `RG-050` apply to frontend design-system governance. |
| E-003 | registry-inventory | Read frontend registries and allowlists | `frontend/src/styles/*.md`, `frontend/src/tests/*allowlist.ts` | PASS | CSS fallback markdown rows and executable entries both count 68; inline entries count 16. |
| E-004 | targeted-tests | `npm run test -- design-system css-fallback inline-style legacy-style theme-tokens` | `frontend` | PASS | 5 files passed, 108 tests passed. |
| E-005 | lint | `npm run lint` | `frontend` | PASS | TypeScript lint command completed without errors. |
| E-006 | build | `npm run build` | `frontend` | PASS | Production build completed; Vite reported a non-blocking chunk-size warning. |
| E-007 | full-tests | `npm run test` | `frontend` | FAIL | Full suite: 112 test files passed, 1 failed; 1232 tests passed, 2 failed, 8 skipped. Failures are in `visual-smoke.test.tsx`. |
| E-008 | targeted-failing-test | `npm run test -- visual-smoke` plus targeted `rg` typography scan | `frontend/src/App.css`, `frontend/src/tests/visual-smoke.test.tsx` | FAIL | Isolated test reproduces 2 failures: test expects old literals while CSS uses tokens. |
| E-009 | inline-style-scan | `rg -n "style=\\{" src -g "*.tsx"` and executable allowlist count | `frontend/src` | FAIL | 16 inline style occurrences remain across 10 TSX files; all are allowlisted. |
| E-010 | css-fallback-scan | `rg -n "var\\(--[^,\\)]+,\\s*[^\\)]+\\)" src -g "*.css"` and allowlist count | `frontend/src` | FAIL | 68 registered fallback entries remain; scan touches 14 CSS files. |
| E-011 | hardcoded-visual-scan | Broad hardcoded visual scan excluding tests and canonical token sources | `frontend/src` | FAIL | 107 application files contain color, dimension, spacing, radius, shadow, or typography literal signals. |
| E-012 | legacy-surface-scan | targeted `rg` scan for legacy, compatibility, migration-only, and compatibility token aliases | `frontend/src` | FAIL | 6 files contain active classified legacy or compatibility surfaces. |
| E-013 | git-status | `git status --short` before audit artifact generation | Repository root | PASS | No pre-existing tracked diff was reported before writing this audit. |

## Command Details

Targeted guard command:

```powershell
npm run test -- design-system css-fallback inline-style legacy-style theme-tokens
```

Validation commands that passed:

```powershell
npm run lint
npm run build
```

Validation commands that failed:

```powershell
npm run test
npm run test -- visual-smoke
```

The Python CONDAMAD validators were run only after activating `.venv`, as required by the repository instructions; their result is recorded after report generation.
