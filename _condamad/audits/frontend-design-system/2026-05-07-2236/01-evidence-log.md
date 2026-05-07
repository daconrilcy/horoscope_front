<!-- Journal des preuves de l'audit frontend design-system apres refactors. -->

# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Inspected path | Result | Notes |
|---|---|---|---|---|---|
| E-001 | skill_contract | `Get-Content .agents/skills/condamad-domain-auditor/SKILL.md` and references | `.agents/skills/condamad-domain-auditor/**` | PASS | Skill contract loaded; audit remains read-only for application code. |
| E-002 | guardrail_registry | `Get-Content _condamad/stories/regression-guardrails.md` | `_condamad/stories/regression-guardrails.md` | PASS | Relevant active invariants are `RG-044` through `RG-060`. |
| E-003 | prior_audit_inventory | `Get-Content _condamad/audits/frontend-design-system/2026-05-07-1730/02-finding-register.md` and `03-story-candidates.md` | previous audit | PASS | Previous 50-file residual list used as historical baseline, not copied as current truth. |
| E-004 | architecture_guard_inventory | `Get-Content frontend/src/tests/design-system-guards.test.ts` | `frontend/src/tests/design-system-guards.test.ts` | PASS | Guards now include CS-084 settings, CS-085 landing, CS-086 admin, and residual CSS token cluster checks. |
| E-005 | test_coverage_inventory | `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | `frontend` | PASS | 6 files, 142 tests passed. |
| E-006 | architecture_guard_inventory | `npm run lint` | `frontend` | PASS | TypeScript lint command passed. |
| E-007 | runtime_contract_check | `npm run build` | `frontend` | PASS | Build passed; Vite emitted a chunk-size warning for the main JS bundle. |
| E-008 | derived_inventory | PowerShell regex inventory for hardcoded visual/type CSS literals | `frontend/src/**/*.css` | PASS | Current hit files reduced to `App.css`, `DailyAdviceCard.css`, `DailyHoroscopePage.css`, `HelpPage.css`, `backgrounds.css`, `glass.css`, plus canonical token owner files. |
| E-009 | targeted_forbidden_symbol_scan | `rg -n "style=\\{" frontend/src -g "*.tsx"` | `frontend/src/**/*.tsx` | PASS | Inline style hits match the exact allowlist in `design-system-allowlist.ts`. |
| E-010 | targeted_forbidden_symbol_scan | No Legacy vocabulary scan over frontend source | `frontend/src` | PASS | CSS No Legacy comments are guarded; non-CSS hits are runtime/product vocabulary outside this CSS audit scope. |
| E-011 | registry_inventory | Token owner registry scan for app, help, settings, landing, chat, admin, premium, and glass namespaces | style registries | PASS | Token namespace registry classifies key frontend token owners, including page-scoped owners and daily premium glass tokens. |
| E-012 | targeted_forbidden_symbol_scan | Targeted literal scan for visual and typography declarations in residual files | six residual implementation files | FAIL | Local literals remain in the six target implementation files listed by this audit. |

## Evidence Details

### E-005

Command:

```powershell
npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke
```

Result:

- `src/tests/inline-style-policy.test.ts`: 4 tests passed.
- `src/tests/design-system-guards.test.ts`: 17 tests passed.
- `src/tests/css-fallback-policy.test.ts`: 3 tests passed.
- `src/tests/legacy-style-policy.test.ts`: 4 tests passed.
- `src/tests/theme-tokens.test.ts`: 96 tests passed.
- `src/tests/visual-smoke.test.tsx`: 18 tests passed.

### E-008

The hardcoded CSS inventory reported these current hit counts:

| File | Hits |
|---|---:|
| `frontend/src/App.css` | 561 |
| `frontend/src/pages/HelpPage.css` | 300 |
| `frontend/src/styles/design-tokens.css` | 388 |
| `frontend/src/layouts/LandingLayout.css` | 175 |
| `frontend/src/pages/settings/Settings.css` | 125 |
| `frontend/src/pages/ChatPage.css` | 95 |
| `frontend/src/styles/premium-theme.css` | 36 |
| `frontend/src/styles/theme.css` | 21 |
| `frontend/src/styles/backgrounds.css` | 20 |
| `frontend/src/pages/DailyHoroscopePage.css` | 11 |
| `frontend/src/styles/glass.css` | 7 |
| `frontend/src/components/prediction/DailyAdviceCard.css` | 4 |

Classification:

- Canonical/global token owner files: `design-tokens.css`, `theme.css`, `premium-theme.css`.
- Page-scoped owner blocks already covered by current guards: `LandingLayout.css`, `Settings.css`, `ChatPage.css`.
- Residual implementation files requiring new stories: `App.css`, `HelpPage.css`, `DailyHoroscopePage.css`, `DailyAdviceCard.css`, `backgrounds.css`, `glass.css`.
