<!-- Journal des preuves de l'audit CONDAMAD des pages React du frontend. -->

# Evidence Log - frontend-react-pages

| ID | Evidence type | Command / Source | Inspected path | Result | Notes |
|---|---|---|---|---|---|
| E-001 | skill_contract | `Get-Content .agents/skills/condamad-domain-auditor/SKILL.md` and required references | `.agents/skills/condamad-domain-auditor/**` | PASS | Skill contract loaded; application code stayed read-only. |
| E-002 | guardrail_registry | `Get-Content _condamad/stories/regression-guardrails.md` | `_condamad/stories/regression-guardrails.md` | PASS | Frontend design-system guardrails exist, but no page-architecture guardrail covers page size, direct API calls, barrels, or route aliases. |
| E-003 | source_inventory | `Get-ChildItem frontend/src/pages -Recurse -Filter *.tsx` with line counts | `frontend/src/pages/**/*.tsx` | FAIL | Largest pages: `AdminPromptsPage.tsx` 3035 lines, `AstrologerProfilePage.tsx` 865, `SubscriptionSettings.tsx` 820, `BirthProfilePage.tsx` 773, `AdminSamplePayloadsAdmin.tsx` 740, `AdminLogsPage.tsx` 698. |
| E-004 | source_inventory | `Get-ChildItem frontend/src/pages -Recurse -Filter *.css` with line counts | `frontend/src/pages/**/*.css` | FAIL | Largest page CSS files: `AdminPromptsPage.css` 2154 lines, `HelpPage.css` 1809, `Settings.css` 1406, `AstrologerProfilePage.css` 1310, `LandingPage.css` 864. |
| E-005 | route_table_inventory | `Get-Content frontend/src/app/routes.tsx` | `frontend/src/app/routes.tsx` | FAIL | Canonical routes and compatibility aliases coexist: `/today`, `/natal-chart`, and `/birth-profile`; admin prompts uses route slots rendered by one page. |
| E-006 | duplicate_responsibility_scan | `rg -n "^(function\|const\|type\|interface) ..."` and helper scans | `frontend/src/pages/**/*.tsx` | FAIL | Page files define many local helpers/components; duplicate helper names include `formatDate`, `formatPrice`, `shouldLogSupportForApiError`, and local path/error builders. |
| E-007 | dependency_direction_scan | `rg -n 'apiFetch\\(' frontend/src/pages -g "*.tsx"` and API import scan | `frontend/src/pages/**/*.tsx` | FAIL | 20 direct `apiFetch` call sites in admin pages; multiple pages import API hooks/functions directly. |
| E-008 | legacy_surface_scan | `rg -n 'export \\* from' frontend/src/pages frontend/src/features frontend/src/components` | `frontend/src/pages/**/index.ts` | FAIL | `frontend/src/pages/admin/index.ts` duplicates exports and exposes `PricingAdmin`/`MonitoringAdmin`; `frontend/src/pages/index.ts` exports broad page barrels. |
| E-009 | no_legacy_scan | `rg -n "PricingAdmin\|MonitoringAdmin\|PersonasAdmin\|/admin/(pricing\|monitoring\|personas)" frontend/src` | `frontend/src` | FAIL | Removed admin route paths are not active, but old admin page modules remain exportable and some are wrapped by newer pages. |
| E-010 | type_guard_scan | `rg -n "@ts-nocheck\|@ts-ignore\|@ts-expect-error" frontend/src/pages -g "*.tsx"` | `frontend/src/pages/**/*.tsx` | FAIL | `@ts-nocheck` remains in `AstrologerProfilePage.tsx`, `ConsultationResultPage.tsx`, `AdminPromptsPage.tsx`, and `NotFoundPage.tsx`. |
| E-011 | test_coverage_inventory | `rg -n "AdminPage\|routes\|pages/admin\|page" frontend/src/tests -g "*.test.*"` | `frontend/src/tests` | LIMITATION | Many behavior/design tests exist, including admin route tests, but no deterministic page-architecture guard was found for direct API calls, page barrels, page size, or `@ts-nocheck`. |
| E-012 | package_script_inventory | `Get-Content frontend/package.json` | `frontend/package.json` | PASS | Standard validation commands exist: `npm run lint`, `npm run test`, `npm run build`. |
| E-013 | audit_validation | Python validation and lint commands from the skill | `_condamad/audits/frontend-react-pages/2026-05-08-0123` | PASS | Audit artifact validation executed after report creation from an activated `.venv`. |

## Evidence Details

### E-003

Largest TSX pages by line count:

- `frontend/src/pages/admin/AdminPromptsPage.tsx`: 3035
- `frontend/src/pages/AstrologerProfilePage.tsx`: 865
- `frontend/src/pages/settings/SubscriptionSettings.tsx`: 820
- `frontend/src/pages/BirthProfilePage.tsx`: 773
- `frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx`: 740
- `frontend/src/pages/admin/AdminLogsPage.tsx`: 698

### E-007

Direct admin API ownership in pages includes:

- `AdminDashboardPage.tsx`: KPI snapshot/flux/billing queries.
- `AdminLogsPage.tsx`: quota alerts, audit logs, LLM logs, Stripe logs, replay, export.
- `AdminEntitlementsPage.tsx`, `AdminUserDetailPage.tsx`, `AdminUsersPage.tsx`, `AdminSupportPage.tsx`, `AdminSettingsPage.tsx`, `AdminAiGenerationsPage.tsx`.

### E-011

Existing tests are useful but mostly behavioral. Examples:

- `AdminPage.test.tsx` covers canonical admin route behavior and removed admin redirects.
- `AdminPromptsRouting.test.tsx` covers prompts subroutes.
- `design-system-guards.test.ts` protects CSS/design-system policy.

Missing guard class: no test or script was found that blocks new direct `apiFetch` calls from pages, duplicate page barrel exports, new `@ts-nocheck` in pages, or large page-owned feature implementations.
