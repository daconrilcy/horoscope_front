<!-- Registre des constats du nouvel audit frontend design-system. -->

# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-guard | frontend-design-system | E-002, E-005, E-006, E-009, E-010, E-011, E-012 | The frontend design-system guard suite is active and green after the implemented refactors. | Keep `RG-044` through `RG-060` mandatory for future frontend style and compatibility work. | no |
| F-002 | Medium | High | duplicate-responsibility | frontend-design-system | E-004, E-005, E-013 | 70 CSS application files still contain visual or typography literals outside `frontend/src/styles/**`; local style files still compete with token and typography ownership until each cluster is classified or migrated. | Continue bounded cluster migrations and update exact anti-regression guards for each migrated cluster. | yes |
| F-003 | Info | High | legacy-surface | frontend-design-system | E-005, E-009, E-010, E-011, E-012 | Previously active legacy/compatibility surfaces remain closed or classified by current guards. | Preserve the current zero-hit and allowlist guards; no implementation story is required for this finding. | no |
| F-004 | Low | High | observability-gap | frontend-performance | E-007 | Build passes, but the main JS chunk remains above Vite's warning threshold. | Track code splitting in a separate frontend performance audit/story if product performance is in scope. | no |

## Finding Details

### F-001 - Frontend design-system guardrails are active

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-002, E-005, E-006, E-009, E-010, E-011, E-012.
- Expected rule: token namespaces, typography roles, CSS fallback exceptions, inline-style exceptions, legacy style surfaces and No Legacy vocabulary must be guarded.
- Actual state: targeted design-system tests pass; lint passes; inline styles and CSS fallbacks match exact allowlists.
- Impact: The frontend design-system guard suite is active and green after the implemented refactors.
- Recommended action: Keep `RG-044` through `RG-060` mandatory for future frontend style and compatibility work.
- Story candidate: no
- Suggested archetype: test-guard-coverage-audit

### F-002 - Hardcoded visual and typography literals remain broad

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-004, E-005, E-013.
- Expected rule: repeated visual and typography decisions should have a canonical owner in `frontend/src/styles/**`, documented semantic token namespaces, or typography roles.
- Actual state: 70 CSS application files still match broad literal patterns for colors, gradients, shadows, radii, font sizes, weights, line heights or letter spacing.
- Impact: 70 CSS application files still contain visual or typography literals outside `frontend/src/styles/**`; local style files still compete with token and typography ownership until each cluster is classified or migrated.
- Recommended action: Continue bounded cluster migrations and update exact anti-regression guards for each migrated cluster.
- Story candidate: yes
- Suggested archetype: design-system-token-convergence

### F-003 - Legacy and compatibility surfaces are guarded

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-005, E-009, E-010, E-011, E-012.
- Expected rule: removed legacy/compatibility surfaces must not return as aliases, shims, fallback paths, stale comments, page-scoped token leaks or static inline styles.
- Actual state: current guards pass and remaining exceptions are exact or domain-functional rather than unclassified design-system compatibility.
- Impact: Previously active legacy/compatibility surfaces remain closed or classified by current guards.
- Recommended action: Preserve the current zero-hit and allowlist guards; no implementation story is required for this finding.
- Story candidate: no
- Suggested archetype: legacy-surface-audit

### F-004 - Production bundle warning remains visible

- Severity: Low
- Confidence: High
- Category: observability-gap
- Domain: frontend-performance
- Evidence: E-007.
- Expected rule: production build should remain green; performance warnings should be tracked separately when in scope.
- Actual state: Vite build passes and reports a main JS chunk above 500 kB.
- Impact: Build passes, but the main JS chunk remains above Vite's warning threshold.
- Recommended action: Track code splitting in a separate frontend performance audit/story if product performance is in scope.
- Story candidate: no
- Suggested archetype: observability-audit
