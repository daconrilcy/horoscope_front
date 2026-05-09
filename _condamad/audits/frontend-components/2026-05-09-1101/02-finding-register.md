<!-- Registre des constats de l'audit CONDAMAD frontend components apres CS-120. -->

# Finding Register - frontend-components

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-canonical-owner | frontend-components | E-003, E-007, E-008, E-009, E-010, E-011, E-012, E-014 | Prior High API-owner debt is closed: no API/feature orchestration remains under `frontend/src/components/**` by current scan and guard evidence. | Keep `RG-069` and `component-architecture` mandatory for component changes. | no |
| F-002 | Info | High | missing-guard | frontend-components | E-004, E-005, E-006, E-009, E-015, E-016 | Prior unguarded component TS/API/legacy risks remain guarded by executable tests and empty exception registers. | Keep exact no-wildcard allowlists; any new exception must have owner, reason, and exit condition. | no |
| F-003 | Info | High | legacy-surface | frontend-components | E-003, E-008, E-017 | Prior old component owners, auth/natal paths, test-only deletions, and CS-120 stale docs/config paths remain absent or point only to canonical owners. | Keep No Legacy scans in future component story validation plans. | no |

## Finding Details

### F-001 - API-owning component debt is closed

- Severity: Info
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-components
- Evidence: E-003, E-007, E-008, E-009, E-010, E-011, E-012, E-014.
- Expected rule: `frontend/src/components/**` should not own runtime API/feature orchestration.
- Actual state: `COMPONENT_API_IMPORT_EXCEPTIONS` is empty; the component API/feature scan returns zero hits; component architecture/usage tests pass; CS-120 route, dashboard, settings, layout, panel, and UI tests pass.
- Impact: Prior High API-owner debt is closed: no API/feature orchestration remains under `frontend/src/components/**` by current scan and guard evidence.
- Recommended action: Keep `RG-069` and `component-architecture` mandatory for component changes.
- Story candidate: no
- Suggested archetype: dependency-direction-audit
- Closure decision: closed.

### F-002 - Component architecture guard suite remains active

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-components
- Evidence: E-004, E-005, E-006, E-009, E-015, E-016.
- Expected rule: API/feature imports, TS suppressions, stale legacy component paths, and stale allowlist rows must be blocked by executable guards.
- Actual state: component architecture guard tests pass; `COMPONENT_API_IMPORT_EXCEPTIONS` and `COMPONENT_TS_NOCHECK_EXCEPTIONS` are empty; `@ts-nocheck` and former `UpgradeHint` API type imports are absent.
- Impact: Prior unguarded component TS/API/legacy risks remain guarded by executable tests and empty exception registers.
- Recommended action: Keep exact no-wildcard allowlists; any new exception must have owner, reason, and exit condition.
- Story candidate: no
- Suggested archetype: test-guard-coverage-audit
- Closure decision: closed.

### F-003 - Legacy component owner paths remain absent

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: frontend-components
- Evidence: E-003, E-008, E-017.
- Expected rule: old component owners removed by CS-117 to CS-120 must not return as wrappers, aliases, fallbacks, re-exports, stale docs, stale coverage config, or imports.
- Actual state: targeted scans for old CS-120 component owners return zero hits; the broader config scan has one hit only for canonical `src/features/enterprise/EnterpriseCredentialsPanel.tsx` in `frontend/vitest.b2b.config.ts`.
- Impact: Prior old component owners, auth/natal paths, test-only deletions, and CS-120 stale docs/config paths remain absent or point only to canonical owners.
- Recommended action: Keep No Legacy scans in future component story validation plans.
- Story candidate: no
- Suggested archetype: legacy-surface-audit
- Closure decision: closed.
