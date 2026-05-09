<!-- Registre des constats du nouvel audit CONDAMAD frontend components. -->

# Finding Register - frontend-components

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | missing-canonical-owner | frontend-components | E-010, E-011, E-015, E-017 | The corrected auth and natal slices are closed, but shared components still own runtime API/feature orchestration for enterprise/admin/settings/layout/dashboard surfaces. This keeps `frontend/src/components/**` from reaching the expected API-free shared component boundary. | Execute a finite relocation map for the remaining exact API-owning component surfaces, preserving the existing no-wildcard allowlist until each slice is moved. | yes |
| F-002 | Info | High | legacy-surface | frontend-components | E-003, E-004, E-006, E-007, E-014, E-015 | Old auth and natal component import paths are absent; canonical feature owners are active and tested. | Keep `RG-069`, `RG-071`, `RG-073`, and the component architecture guard required for future moves. | no |
| F-003 | Info | High | legacy-surface | frontend-components | E-005, E-008, E-009, E-016 | Test-only B2B, ops, privacy, daily, and prediction UI surfaces from CS-119 are deleted with no active symbol/import/CSS hits and no stale allowlist rows. | Keep `RG-074` and the component usage guard required for future component changes. | no |
| F-004 | Info | High | missing-guard | frontend-components | E-012, E-013, E-015, E-016 | Component usage, architecture, No Legacy deletion, natal relocation, and `@ts-nocheck` guards are executable and currently passing. | Keep targeted guards in validation plans; do not broaden allowlists without exact owner, reason, and exit condition. | no |

## Finding Details

### F-001 - Remaining API-owning component surfaces are still active

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-components
- Evidence: E-010, E-011, E-015, E-017.
- Expected rule: `frontend/src/components/**` should not be the long-term owner for API or feature orchestration; retained exceptions must shrink to zero through feature/page owners or remain explicitly blocked by a user decision.
- Actual state: CS-117 and CS-118 removed the auth and natal exceptions, and CS-119 removed test-only API panels. Current scans still find API/feature imports in `AdminGuard`, `B2BReconciliationPanel`, `EnterpriseCredentialsPanel`, `SupportOpsPanel`, `dashboard/useDashboardAstroSummary`, `layout/BottomNav`, `layout/Header`, `layout/Sidebar`, `settings/DeleteAccountModal`, and a type-only test import in `ui/UpgradeCTA/UpgradeCTA.test.tsx`. The exception register is exact and guarded, but these runtime surfaces have not moved to feature/page owners.
- Impact: The corrected auth and natal slices are closed, but shared components still own runtime API/feature orchestration for enterprise/admin/settings/layout/dashboard surfaces. This keeps `frontend/src/components/**` from reaching the expected API-free shared component boundary.
- Recommended action: Execute a finite relocation map for the remaining exact API-owning component surfaces, preserving the existing no-wildcard allowlist until each slice is moved.
- Story candidate: yes
- Suggested archetype: ownership-routing-refactor
- Closure decision: phased-with-map.

### F-002 - Auth and natal relocations are closed

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: frontend-components
- Evidence: E-003, E-004, E-006, E-007, E-014, E-015.
- Expected rule: old component paths must not remain as wrapper, alias, fallback, re-export, or stale allowlist rows after relocation.
- Actual state: auth forms live under `features/auth`; natal interpretation lives under `features/natal-chart`; current scans show zero active old-path hits and tests pass.
- Impact: Old auth and natal component import paths are absent; canonical feature owners are active and tested.
- Recommended action: Keep `RG-069`, `RG-071`, `RG-073`, and the component architecture guard required for future moves.
- Story candidate: no
- Suggested archetype: legacy-facade-removal

### F-003 - Test-only component deletion is closed

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: frontend-components
- Evidence: E-005, E-008, E-009, E-016.
- Expected rule: deleted test-only UI surfaces must not remain as files, tests, imports, CSS selectors, or allowlist rows.
- Actual state: targeted scans for the deleted B2B, ops, privacy, daily, and prediction symbols return zero active hits; guards pass.
- Impact: Test-only B2B, ops, privacy, daily, and prediction UI surfaces from CS-119 are deleted with no active symbol/import/CSS hits and no stale allowlist rows.
- Recommended action: Keep `RG-074` and the component usage guard required for future component changes.
- Story candidate: no
- Suggested archetype: dead-code-removal

### F-004 - Current component guard suite is green

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-components
- Evidence: E-012, E-013, E-015, E-016.
- Expected rule: suppressions, deleted surfaces, public export exceptions, and component API exceptions must stay exact and executable.
- Actual state: no component `@ts-nocheck` exists; component usage/architecture/design/visual/natal tests pass.
- Impact: Component usage, architecture, No Legacy deletion, natal relocation, and `@ts-nocheck` guards are executable and currently passing.
- Recommended action: Keep targeted guards in validation plans; do not broaden allowlists without exact owner, reason, and exit condition.
- Story candidate: no
- Suggested archetype: test-guard-coverage-audit
