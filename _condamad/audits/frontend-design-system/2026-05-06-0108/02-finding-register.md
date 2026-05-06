# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-guard | frontend-design-system | E-001, E-002, E-003, E-004, E-005, E-006, E-007, E-008 | Refactors are protected by executable checks. | Keep guards mandatory for future frontend style stories. | no |
| F-002 | Medium | High | legacy-surface | frontend-design-system | E-003, E-009, E-012, E-014 | Fallback literals still preserve alternate visual decisions beside canonical tokens. | Reduce non-decision fallbacks, then resolve premium token ownership. | yes |
| F-003 | Medium | High | legacy-surface | frontend-design-system | E-004, E-010, E-012 | Dynamic style decisions still live in TSX and must not grow silently. | Convert removable bridges to CSS custom properties/classes and keep allowlists exact. | yes |
| F-004 | Medium | High | duplicate-responsibility | frontend-design-system | E-011 | Semantic tokens still compete with local literals across many product surfaces. | Continue phased token/typography migration by coherent product cluster. | yes |
| F-005 | Medium | High | legacy-surface | frontend-design-system | E-005, E-012, E-013 | No Legacy is controlled but active through admin prompt selectors and compatibility aliases. | Split admin prompt legacy extinction from token alias retirement. | yes |
| F-006 | Info | High | observability-gap | frontend-performance | E-006 | Build passes, but bundle growth remains visible as a Vite warning. | Track under a separate frontend performance audit/story. | no |

## Finding Details

### F-001

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-001, E-002, E-003, E-004, E-005, E-006, E-007, E-008.
- Expected rule: frontend design-system governance remains executable.
- Actual state: targeted tests, full tests, lint, and build pass.
- Impact: Refactors are protected by executable checks.
- Recommended action: Keep guards mandatory for future frontend style stories.
- Story candidate: no
- Suggested archetype: no-story-observation.

### F-002

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-003, E-009, E-012, E-014.
- Expected rule: CSS fallbacks are classified and shrink when canonical tokens are guaranteed.
- Actual state: 10 exact fallback exceptions remain; premium token ownership is unresolved for two consumed tokens.
- Impact: Fallback literals still preserve alternate visual decisions beside canonical tokens.
- Recommended action: Reduce non-decision fallbacks, then resolve premium token ownership.
- Story candidate: yes
- Suggested archetype: css-fallback-debt-reduction.

### F-003

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-004, E-010, E-012.
- Expected rule: inline styles are restricted to dynamic exceptions or component style-prop bridges.
- Actual state: 9 exact inline style exceptions remain.
- Impact: Dynamic style decisions still live in TSX and must not grow silently.
- Recommended action: Convert removable bridges to CSS custom properties/classes and keep allowlists exact.
- Story candidate: yes
- Suggested archetype: inline-style-debt-reduction.

### F-004

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-011.
- Expected rule: visual decisions converge toward tokens and semantic typography roles.
- Actual state: 110 files still match broad literal visual or typography signals outside main token source files.
- Impact: Semantic tokens still compete with local literals across many product surfaces.
- Recommended action: Continue phased token/typography migration by coherent product cluster.
- Story candidate: yes
- Suggested archetype: hardcoded-design-value-reduction.

### F-005

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-005, E-012, E-013.
- Expected rule: legacy selectors and compatibility aliases stay classified and shrink over time.
- Actual state: 5 registry rows remain active.
- Impact: No Legacy is controlled but active through admin prompt selectors and compatibility aliases.
- Recommended action: Split admin prompt legacy extinction from token alias retirement.
- Story candidate: yes
- Suggested archetype: legacy-style-surface-extinction.

### F-006

- Severity: Info
- Confidence: High
- Category: observability-gap
- Domain: frontend-performance
- Evidence: E-006.
- Expected rule: build remains operational and performance warnings are tracked in the correct domain.
- Actual state: build passes with a Vite chunk warning.
- Impact: Build passes, but bundle growth remains visible as a Vite warning.
- Recommended action: Track under a separate frontend performance audit/story.
- Story candidate: no
- Suggested archetype: no-story-observation.
