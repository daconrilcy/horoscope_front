<!-- Registre des constats de l'audit frontend design-system apres refactors. -->

# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-guard | frontend-design-system | E-001, E-002, E-003, E-004, E-005, E-006 | Positive invariant: guardrails remain active after refactors. | Keep the guard suite mandatory. | no |
| F-002 | Medium | High | duplicate-responsibility | frontend-design-system | E-003, E-007, E-008 | 50 unclosed CSS files can still own visual and typography decisions locally. | Migrate the remaining files by bounded clusters and update exact guards. | yes |
| F-003 | Info | High | legacy-surface | frontend-design-system | E-002, E-003, E-004, E-009, E-010 | No new No Legacy defect found; removed or classified surfaces remain protected. | Preserve exact allowlists and No Legacy guards. | no |
| F-004 | Low | High | observability-gap | frontend-performance | E-006 | Production bundle remains large; performance risk is outside design-system ownership. | Track separately in a frontend performance audit/story if needed. | no |

## Finding Details

### F-001 - Frontend design-system guardrails remain active

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-001, E-002, E-003, E-004, E-005, E-006.
- Expected rule: design-system constraints must remain executable after refactors.
- Actual state: targeted and full frontend validation passed.
- Impact: Positive invariant: guardrails remain active after refactors.
- Recommended action: Keep the guard suite mandatory.
- Story candidate: no
- Suggested archetype: test-guard-coverage-audit

### F-002 - Residual hardcoded visual and typography ownership remains in 50 CSS files

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-003, E-007, E-008.
- Expected rule: repeated visual and typography values should have canonical ownership.
- Actual state: 50 residual CSS files remain after subtracting closed clusters from the raw scan.
- Impact: 50 unclosed CSS files can still own visual and typography decisions locally.
- Recommended action: Migrate the remaining files by bounded clusters and update exact guards.
- Story candidate: yes
- Suggested archetype: design-system-token-convergence

### F-003 - Previously active frontend legacy and compatibility surfaces are closed or classified

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-002, E-003, E-004, E-009, E-010.
- Expected rule: removed compatibility and legacy design-system surfaces must not return.
- Actual state: current guards pass and exact allowlists remain constrained.
- Impact: No new No Legacy defect found; removed or classified surfaces remain protected.
- Recommended action: Preserve exact allowlists and No Legacy guards.
- Story candidate: no
- Suggested archetype: legacy-surface-audit

### F-004 - Production bundle warning remains visible

- Severity: Low
- Confidence: High
- Category: observability-gap
- Domain: frontend-performance
- Evidence: E-006.
- Expected rule: build must pass, and bundle-size risk should be tracked in the correct domain.
- Actual state: build passes with Vite chunk warning.
- Impact: Production bundle remains large; performance risk is outside design-system ownership.
- Recommended action: Track separately in a frontend performance audit/story if needed.
- Story candidate: no
- Suggested archetype: observability-audit
