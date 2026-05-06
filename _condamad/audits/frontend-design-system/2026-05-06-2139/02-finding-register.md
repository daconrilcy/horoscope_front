<!-- Registre des constats de l'audit frontend design-system. -->

# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-guard | frontend-design-system | E-002, E-003, E-004, E-006, E-007, E-008, E-009, E-010, E-011 | The guard suite is active and covers the recently refactored design-system and compatibility surfaces. | Keep `RG-044` through `RG-057` mandatory for future frontend design-system stories. | no |
| F-002 | Medium | High | duplicate-responsibility | frontend-design-system | E-003, E-012 | 98 non-test application files still contain hardcoded visual or typography literals, so local style decisions continue to compete with token and typography ownership. | Continue bounded cluster migrations with before/after inventories and focused guard updates. | yes |
| F-003 | Info | High | legacy-surface | frontend-design-system | E-006, E-007, E-008, E-009, E-010, E-011 | Previously active CS-074 through CS-080 legacy or compatibility surfaces are closed or reduced to exact dynamic exceptions. | Preserve the current zero-hit scans and exact allowlists; no new story needed. | no |
| F-004 | Low | High | observability-gap | frontend-performance | E-005 | Build passes but bundle-size drift remains visible through Vite's chunk warning. | Track in a separate frontend performance audit/story if chunk size is a product concern. | no |

## Finding Details

### F-001 - Frontend design-system guardrails are active

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-002, E-003, E-004, E-006, E-007, E-008, E-009, E-010, E-011.
- Expected rule: Guardrails created by prior frontend stories remain executable and block reintroduction of forbidden surfaces.
- Actual state: Focused Vitest guard suite, TypeScript lint and production build pass. Page-scoped token isolation, compatibility vocabulary removal, admin redirect removal, CSS fallback and inline-style allowlists are all covered.
- Impact: The guard suite is active and covers the recently refactored design-system and compatibility surfaces.
- Recommended action: Keep `RG-044` through `RG-057` mandatory for future frontend design-system stories.
- Story candidate: no
- Suggested archetype: test-guard-coverage-audit

### F-002 - Hardcoded visual and typography literals remain broad

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-003, E-012.
- Expected rule: Repeated visual and typography decisions should converge to canonical design tokens, semantic component/page tokens or documented typography roles.
- Actual state: 98 non-test application files still match hardcoded visual/typography literal patterns outside `frontend/src/styles/**`.
- Impact: 98 non-test application files still contain hardcoded visual or typography literals, so local style decisions continue to compete with token and typography ownership.
- Recommended action: Continue bounded cluster migrations with before/after inventories and focused guard updates.
- Story candidate: yes
- Suggested archetype: design-system-token-convergence

### F-003 - Previously active legacy/compatibility surfaces are closed

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-006, E-007, E-008, E-009, E-010, E-011.
- Expected rule: Implemented refactors should not leave active wrappers, aliases, fallback paths, redirects or compatibility branches behind.
- Actual state: CS-074 through CS-080 target surfaces are no longer active in runtime/source scans. CSS fallback and inline style debt is bounded to exact dynamic exceptions.
- Impact: Previously active CS-074 through CS-080 legacy or compatibility surfaces are closed or reduced to exact dynamic exceptions.
- Recommended action: Preserve the current zero-hit scans and exact allowlists; no new story needed.
- Story candidate: no
- Suggested archetype: legacy-surface-audit

### F-004 - Production bundle warning remains visible

- Severity: Low
- Confidence: High
- Category: observability-gap
- Domain: frontend-performance
- Evidence: E-005.
- Expected rule: Build should provide a useful signal when frontend performance drifts.
- Actual state: Production build passes, but Vite reports a main JS chunk of 1,370.37 kB.
- Impact: Build passes but bundle-size drift remains visible through Vite's chunk warning.
- Recommended action: Track in a separate frontend performance audit/story if chunk size is a product concern.
- Story candidate: no
- Suggested archetype: observability-audit
