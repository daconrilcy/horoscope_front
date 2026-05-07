<!-- Journal des preuves de l'audit frontend design-system apres refactors CS-087 a CS-089. -->

# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Inspected path | Result | Notes |
|---|---|---|---|---|---|
| E-001 | skill_contract | `Get-Content .agents/skills/condamad-domain-auditor/SKILL.md` and references | `.agents/skills/condamad-domain-auditor/**` | PASS | Skill contract loaded; audit remained read-only for application code. |
| E-002 | guardrail_registry | `Get-Content _condamad/stories/regression-guardrails.md` | `_condamad/stories/regression-guardrails.md` | PASS | Frontend design-system invariants `RG-044` through `RG-063` are active. |
| E-003 | prior_audit_inventory | Previous finding/story registers from `2026-05-04-2238` through `2026-05-07-2236` | `_condamad/audits/frontend-design-system/**` | PASS | Previous remaining candidates were `App.css`, Help subscriptions, and shared premium surfaces. |
| E-004 | architecture_guard_inventory | `rg -n "CS-087\|CS-088\|CS-089\|collectResidualCssTokenCluster" frontend/src/tests/design-system-guards.test.ts` | `frontend/src/tests/design-system-guards.test.ts` | PASS | Guards cover App active declarations, Help subscriptions, premium shared surfaces, residual cluster, UI, chat, landing, settings, admin, fallback, inline style, and No Legacy vocabulary. |
| E-005 | story_evidence_inventory | `rg -n "RG-061\|RG-062\|RG-063\|CS-087\|CS-088\|CS-089" _condamad/stories -g "*.md"` | `_condamad/stories/**` | PASS | Final evidence and guardrail rows exist for the three stories from the last audit. |
| E-006 | targeted_forbidden_symbol_scan | `rg -n "style=" frontend/src -g "*.tsx"` | `frontend/src/**/*.tsx` | PASS | Inline style hits match exact dynamic allowlist entries only. |
| E-007 | targeted_forbidden_symbol_scan | `rg --pcre2 -n "var\\(\\s*--[a-zA-Z0-9_-]+\\s*," frontend/src -g "*.css"` | `frontend/src/**/*.css` | PASS | CSS fallback scan reports only `--usage-progress` in `App.css` and `Settings.css`, matching `CSS_FALLBACK_EXCEPTIONS`. |
| E-008 | targeted_visual_scan | Targeted PCRE2 visual/type literal scan over uncovered-looking CSS candidates | selected CSS files | PASS | `TimezoneSelect.css`, `AuthLayout.css`, `TwoColumnLayout.css`, `NotFoundPage.css`, and selected prediction CSS files had no visual/type literal hits. |
| E-009 | test_coverage_inventory | `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke DailyHoroscopePage HelpPage` | `frontend` | PASS | 8 files and 171 tests passed. |
| E-010 | architecture_guard_inventory | `npm run lint` | `frontend` | PASS | TypeScript lint configs passed. |
| E-011 | runtime_contract_check | `npm run build` | `frontend` | PASS | Build passed; Vite emitted a main chunk-size warning. |
| E-012 | full_test_inventory | `npm run test` | `frontend` | PASS | 115 test files passed; 1263 tests passed and 8 skipped. |
| E-013 | source_inventory | `git status --short` | repository root | PASS | No dirty worktree entries before audit artifact creation. |

## Evidence Details

### E-009

Command:

```powershell
npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke DailyHoroscopePage HelpPage
```

Result:

- 8 test files passed.
- 171 tests passed.
- Noted stderr warnings are test-environment limitations: jsdom canvas `getContext()` not implemented and React Router v7 future-flag notices.

### E-011

Command:

```powershell
npm run build
```

Result:

- Build passed.
- Main output: `assets/index-BjrgoFoV.js` at `1,370.45 kB`, gzip `396.35 kB`.
- Vite warning: chunk larger than `500 kB`.

### E-012

Command:

```powershell
npm run test
```

Result:

- 115 test files passed.
- 1263 tests passed.
- 8 tests skipped.
