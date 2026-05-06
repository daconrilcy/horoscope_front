<!-- Registre des constats de l'audit frontend design-system apres CS-081. -->

# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-guard | frontend-design-system | E-002, E-005, E-006, E-008, E-009, E-010, E-011, E-012 | The frontend design-system guard suite is active and green after the CS-081 chat refactor. | Keep `RG-044` through `RG-058` mandatory for future frontend style and compatibility work. | no |
| F-002 | Medium | High | duplicate-responsibility | frontend-design-system | E-004, E-014, E-015 | 66 non-test application files still contain visual or typography literals outside `frontend/src/styles/**`, so local files continue to compete with token and typography ownership. | Continue bounded cluster migrations and update exact guards for each migrated cluster. | yes |
| F-003 | Medium | High | missing-guard | frontend-design-system | E-013 | A CSS comment still contains No Legacy vocabulary while the current legacy-style guard classifies selectors, not comment vocabulary. | Remove or rename the stale CSS comment and add a guard that scans CSS source comments/vocabulary for unclassified legacy wording. | yes |
| F-004 | Low | High | observability-gap | frontend-performance | E-007 | Build is green, but the main JS chunk remains above Vite's warning threshold. | Track code splitting in a separate frontend performance story if product performance is in scope. | no |

## Finding Details

### F-001 - Frontend design-system guardrails are active

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-002, E-005, E-006, E-008, E-009, E-010, E-011, E-012.
- Expected rule: Implemented frontend guardrails must remain executable and must block reintroduction of forbidden token, fallback, inline-style, page-scoped, route and runtime compatibility surfaces.
- Actual state: Focused guard suite, full Vitest suite, lint and targeted No Legacy scans pass for the known recent surfaces. Inline-style and CSS fallback debt is limited to exact dynamic allowlists.
- Impact: The frontend design-system guard suite is active and green after the CS-081 chat refactor.
- Recommended action: Keep `RG-044` through `RG-058` mandatory for future frontend style and compatibility work.
- Story candidate: no
- Suggested archetype: test-guard-coverage-audit

### F-002 - Hardcoded visual and typography literals remain broad

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-004, E-014, E-015.
- Expected rule: Repeated visual and typography decisions should be owned by canonical tokens, semantic page/component tokens or documented typography roles.
- Actual state: 66 non-test application files outside `frontend/src/styles/**` still match broad hardcoded visual/typography literal patterns.
- Impact: 66 non-test application files still contain visual or typography literals outside `frontend/src/styles/**`, so local files continue to compete with token and typography ownership.
- Recommended action: Continue bounded cluster migrations and update exact guards for each migrated cluster.
- Story candidate: yes
- Suggested archetype: design-system-token-convergence

### F-003 - CSS No Legacy vocabulary is not fully guarded

- Severity: Medium
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-013.
- Expected rule: No Legacy vocabulary in active frontend source should be removed, classified or guarded so stale compatibility labels do not survive outside explicit registries.
- Actual state: `frontend/src/pages/admin/AdminPromptsPage.css:1792` contains `Route legacy : investigation hors catalogue`. Existing legacy-style policy tests classify selectors and aliases, but do not fail on CSS comment vocabulary.
- Impact: A CSS comment still contains No Legacy vocabulary while the current legacy-style guard classifies selectors, not comment vocabulary.
- Recommended action: Remove or rename the stale CSS comment and add a guard that scans CSS source comments/vocabulary for unclassified legacy wording.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening

### F-004 - Production bundle warning remains visible

- Severity: Low
- Confidence: High
- Category: observability-gap
- Domain: frontend-performance
- Evidence: E-007.
- Expected rule: Build output should remain visible during audit so performance drift is not hidden by green design-system checks.
- Actual state: Production build passes, but Vite reports the main JS chunk at 1,370.37 kB after minification.
- Impact: Build is green, but the main JS chunk remains above Vite's warning threshold.
- Recommended action: Track code splitting in a separate frontend performance story if product performance is in scope.
- Story candidate: no
- Suggested archetype: observability-audit
