# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-guard | frontend-design-system | E-001, E-002, E-003, E-004, E-005, E-006, E-007, E-012 | Refactors are currently protected by executable checks. | Keep guards mandatory for future frontend style stories. | no |
| F-002 | Medium | High | legacy-surface | frontend-design-system | E-009, E-012 | Three CSS fallback literals remain active beside canonical tokens/dynamic values. | Remove the one migration-only fallback and preserve the two runtime `--usage-progress` bridges as classified exceptions. | yes |
| F-003 | Medium | High | legacy-surface | frontend-design-system | E-010, E-012 | Inline visual/runtime decisions still live in TSX and must not grow silently. | Convert removable inline styles to CSS custom-property bridges, classes or variants; keep `Skeleton` API exceptions deliberate. | yes |
| F-004 | Medium | High | duplicate-responsibility | frontend-design-system | E-011, E-012 | Semantic tokens still compete with local literals across many product and test surfaces. | Continue phased token/typography migration by coherent product cluster, starting with high-signal CSS surfaces. | yes |
| F-005 | Medium | High | legacy-surface | frontend-design-system | E-013, E-012 | No Legacy is controlled but active through admin prompt selectors and compatibility aliases. | Split admin prompt legacy extinction from global compatibility alias retirement. | yes |
| F-006 | Info | High | observability-gap | frontend-performance | E-006 | Build passes, but bundle growth remains visible as a Vite warning. | Track under a separate frontend performance audit/story. | no |
| F-007 | Info | High | missing-canonical-owner | frontend-design-system | E-014 | Premium natal token ownership issue from the previous audit is resolved. | Keep premium token declarations in `premium-theme.css` and guard via theme-token tests. | no |

## Finding Details

### F-001

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-001, E-002, E-003, E-004, E-005, E-006, E-007, E-012.
- Expected rule: frontend design-system governance remains executable.
- Actual state: targeted tests, full tests, lint, and build pass.
- Impact: Refactors are currently protected by executable checks.
- Recommended action: Keep guards mandatory for future frontend style stories.
- Story candidate: no
- Suggested archetype: no-story-observation.

### F-002

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-009, E-012.
- Expected rule: CSS fallbacks are classified and shrink when canonical tokens are guaranteed.
- Actual state: 3 exact fallback exceptions remain; 2 are dynamic progress bridges and 1 is migration-only.
- Impact: Three CSS fallback literals remain active beside canonical tokens/dynamic values.
- Recommended action: Remove the one migration-only fallback and preserve the two runtime `--usage-progress` bridges as classified exceptions.
- Story candidate: yes
- Suggested archetype: css-fallback-debt-reduction.

### F-003

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-010, E-012.
- Expected rule: inline styles are restricted to dynamic exceptions or component style-prop bridges.
- Actual state: 6 exact inline style exceptions remain.
- Impact: Inline visual/runtime decisions still live in TSX and must not grow silently.
- Recommended action: Convert removable inline styles to CSS custom-property bridges, classes or variants; keep `Skeleton` API exceptions deliberate.
- Story candidate: yes
- Suggested archetype: inline-style-debt-reduction.

### F-004

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-011, E-012.
- Expected rule: visual decisions converge toward tokens and semantic typography roles.
- Actual state: 113 files match broad literal visual or typography signals outside main token source files.
- Impact: Semantic tokens still compete with local literals across many product and test surfaces.
- Recommended action: Continue phased token/typography migration by coherent product cluster, starting with high-signal CSS surfaces.
- Story candidate: yes
- Suggested archetype: hardcoded-design-value-reduction.

### F-005

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-013, E-012.
- Expected rule: legacy selectors and compatibility aliases stay classified and shrink over time.
- Actual state: 5 registry rows remain active and `AdminPromptsPage.tsx` still consumes `.admin-prompts-legacy*`.
- Impact: No Legacy is controlled but active through admin prompt selectors and compatibility aliases.
- Recommended action: Split admin prompt legacy extinction from global compatibility alias retirement.
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

### F-007

- Severity: Info
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-design-system
- Evidence: E-014.
- Expected rule: premium token consumers resolve to declared premium theme tokens.
- Actual state: `--premium-text-muted`, `--premium-glass-border-soft`, and `--premium-radius-pill` are declared in `premium-theme.css`.
- Impact: Premium natal token ownership issue from the previous audit is resolved.
- Recommended action: Keep premium token declarations in `premium-theme.css` and guard via theme-token tests.
- Story candidate: no
- Suggested archetype: no-story-observation.
