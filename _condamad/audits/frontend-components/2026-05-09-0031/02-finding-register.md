<!-- Registre des constats de l'audit CONDAMAD de continuite frontend components. -->

# Finding Register - frontend-components

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Low | High | missing-canonical-owner | frontend-components | E-001, E-003, E-006, E-009, E-013 | Exact component containers still own API/feature orchestration until future feature/page owners exist, but every current hit is owned, guarded, and has an exit condition. | No immediate component-domain story. Route future relocation through the relevant feature/page domain when that owner is scoped. | no |
| F-002 | Info | High | missing-guard | frontend-components | E-002, E-003, E-006, E-009 | Prior unguarded `@ts-nocheck` risk is closed; zero component suppressions remain and a guard blocks reintroduction. | Keep `RG-070` and `component-architecture` required for component changes. | no |
| F-003 | Info | High | duplicate-responsibility | frontend-components | E-004, E-006, E-009, E-010 | Prior `NatalInterpretation` monolith risk is closed; the container is narrower and presentational children are API-free by guard. | Keep `RG-071`; defer optional feature relocation to a natal feature story. | no |
| F-004 | Info | High | legacy-surface | frontend-components | E-005, E-006, E-008, E-009, E-010 | Prior unclassified component usage risk is closed; unused-looking or barrel-only files are classified and guarded, with remove-classified files deleted. | Keep `RG-072`; revisit test-only panels only when product/runtime ownership is scoped. | no |
| F-005 | Info | High | missing-test-coverage | frontend-components | E-006, E-007 | Targeted component tests and lint pass after the implemented stories. | Keep these commands in future component story validation plans. | no |

## Finding Details

### F-001 - Guarded API-owning components remain as convergence debt

- Severity: Low
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-components
- Evidence: E-001, E-003, E-006, E-009, E-013.
- Expected rule: components should not become implicit API/feature owners; any retained container must be exact, owned, tested, and guarded.
- Actual state: API/feature hits remain in the audited continuity surface, but `COMPONENT_API_IMPORT_EXCEPTIONS` classifies each exact file with owner, reason, and exit condition, and `component-architecture-guards.test.ts` rejects new or stale exceptions. The exception count is 20 runtime component or component-hook surfaces plus 1 test type-only exception.
- Impact: Exact component containers still own API/feature orchestration until future feature/page owners exist, but every current hit is owned, guarded, and has an exit condition.
- Recommended action: No immediate component-domain story. Route future relocation through the relevant feature/page domain when that owner is scoped.
- Story candidate: no
- Suggested archetype: dependency-direction-audit
- Closure decision: residual work is deferred non-domain context, not an active component-domain finding.

### F-002 - Component TypeScript suppressions are closed

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-components
- Evidence: E-002, E-003, E-006, E-009.
- Expected rule: no `@ts-nocheck` should exist under `frontend/src/components/**` unless exactly classified.
- Actual state: targeted scan returns zero hits; `COMPONENT_TS_NOCHECK_EXCEPTIONS` is empty; guard rejects new suppressions.
- Impact: Prior unguarded `@ts-nocheck` risk is closed; zero component suppressions remain and a guard blocks reintroduction.
- Recommended action: Keep `RG-070` and `component-architecture` required for component changes.
- Story candidate: no
- Suggested archetype: test-guard-coverage-audit

### F-003 - NatalInterpretation ownership is closed

- Severity: Info
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-components
- Evidence: E-004, E-006, E-009, E-010.
- Expected rule: `NatalInterpretation.tsx` should not own API orchestration, formatting helpers, modal internals, feature selection, and rendering in one unclassified component.
- Actual state: `NatalInterpretation.tsx` is a classified 458-line container; content, menus, evidence helpers, persona selector, and types live in focused files. The architecture guard checks presentational files are API-free.
- Impact: Prior `NatalInterpretation` monolith risk is closed; the container is narrower and presentational children are API-free by guard.
- Recommended action: Keep `RG-071`; defer optional feature relocation to a natal feature story.
- Story candidate: no
- Suggested archetype: duplicate-rule-removal

### F-004 - Component usage inventory is closed

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: frontend-components
- Evidence: E-005, E-006, E-008, E-009, E-010.
- Expected rule: every exported component file in the prior F-005 continuity surface must be runtime-used, an intentional public export, test-only, removed, or decision-blocked.
- Actual state: `COMPONENT_USAGE_EXCEPTIONS` classifies residual unused-looking files exactly and the guard rejects unclassified unreachable exported component files. Representative remove-classified prediction files are absent.
- Impact: Prior unclassified component usage risk is closed; unused-looking or barrel-only files are classified and guarded, with remove-classified files deleted.
- Recommended action: Keep `RG-072`; revisit test-only panels only when product/runtime ownership is scoped.
- Story candidate: no
- Suggested archetype: dead-code-removal

### F-005 - Validation suite is green

- Severity: Info
- Confidence: High
- Category: missing-test-coverage
- Domain: frontend-components
- Evidence: E-006, E-007.
- Expected rule: implemented component audit stories should have executable guard and lint evidence.
- Actual state: targeted component tests and frontend lint pass.
- Impact: Targeted component tests and lint pass after the implemented stories.
- Recommended action: Keep these commands in future component story validation plans.
- Story candidate: no
- Suggested archetype: test-guard-coverage-audit
