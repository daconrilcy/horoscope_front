<!-- Journal de preuves de l'audit CONDAMAD frontend components. -->

# Evidence Log - frontend-components

| ID | Evidence type | Command / Source | Result | Notes |
|---|---|---|---|---|
| E-001 | file_inventory | `rg --files frontend/src/components` | PASS | Inventaire du domaine audite, 150 fichiers environ sous `frontend/src/components/**`. |
| E-002 | prior_audit_review | `_condamad/audits/frontend-design-system/2026-05-08-0054`, `_condamad/audits/frontend-react-pages/2026-05-08-1323`, `_condamad/audits/frontend-layouts/2026-05-08-2227` | PASS | Les audits precedents ferment design-system, pages et layouts, mais ne ferment pas les responsabilites internes de `components`. |
| E-003 | dependency_direction_scan | `rg -n 'from ["''](\\.\\./pages\|@/pages\|\\.\\./features\|@/features\|\\.\\./api\|@/api)\|apiFetch\\(\|fetch\\(\|axios\|localStorage\|sessionStorage\|@ts-nocheck' frontend/src/components -g '*.ts' -g '*.tsx'` | FAIL | Hits API et feature dans `AdminGuard.tsx`, `B2B*Panel.tsx`, `EnterpriseCredentialsPanel.tsx`, `NatalInterpretation.tsx`, `Ops*Panel.tsx`, `PrivacyPanel.tsx`, auth forms, layout auth consumers, settings modal et dashboard hook. |
| E-004 | targeted_forbidden_symbol_scan | `rg -n 'TS_NOCHECK\|@ts-nocheck\|DIRECT_API\|apiFetch\|from.*\\.\\./api\|from.*@api' frontend/src/tests frontend/src/components -g '*.ts' -g '*.tsx'` | FAIL | `@ts-nocheck` appears in component files; existing page allowlists are empty and scoped to pages. |
| E-005 | size_and_responsibility_inventory | `Get-ChildItem -Recurse -File -Include *.tsx,*.ts frontend/src/components`, line count filter over 300 lines | FAIL | `NatalInterpretation.tsx` has 1131 lines and `AstroMoodBackground.tsx` has 502 lines. CSS count shows `NatalInterpretation.css` has 913 lines. |
| E-006 | no_legacy_style_scan | `rg -n 'style=\\{\|style="\|dangerouslySetInnerHTML' frontend/src/components` and `rg -n 'var\\([^,)]+,' frontend/src/components -g '*.css'` | PASS | Inline styles are the exact allowlisted dynamic cases. No CSS fallback literal was found inside component CSS. |
| E-007 | guard_execution | `npm run test -- components design-system inline-style legacy-style` from `frontend` | PASS | 15 test files and 157 tests passed, including design-system, inline-style, legacy-style and shared UI component tests. |
| E-008 | lint_execution | `npm run lint` from `frontend` | PASS | TypeScript lint build passed, but this does not cover files suppressed by `@ts-nocheck`. |
| E-009 | test_coverage_inventory | `rg --files frontend/src/components -g '*.test.ts' -g '*.test.tsx'` plus targeted test import scan | PASS | UI primitives have colocated tests; root/domain panels are mostly tested from `frontend/src/tests/**`; guard coverage is design-system oriented, not component architecture oriented. |
| E-010 | guardrail_registry | `_condamad/stories/regression-guardrails.md` | PASS | Applicable guardrails `RG-047` to `RG-050`, `RG-056`, `RG-057`, `RG-064`, `RG-067`, `RG-068` were consulted. |
| E-011 | runtime_usage_inventory | `_condamad/audits/frontend-components/2026-05-08-2303/06-component-usage-inventory.md` | FAIL | Reproducible static inventory found no external runtime hits for 14 component files and barrel-only usage for `FormField`. `DashboardIcons.tsx` is classified as `manual-review-required` because it exports named icons and has a `SettingsIcon` name collision in `AdminPage.tsx`. |
| E-012 | audit_contract_validation | `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py _condamad/audits/frontend-components/2026-05-08-2303 --explain-audit` and `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py _condamad/audits/frontend-components/2026-05-08-2303` | PASS | CONDAMAD audit validator and linter passed after the review fixes. |

## Limitations

- No browser runtime was launched because this is a read-only architecture audit and the observed issues are structural.
- The audit did not modify application code or create executable guards; story candidates define the required future guards.
- The component usage inventory is static and conservative; it must be confirmed with import-aware review before deleting any component.
