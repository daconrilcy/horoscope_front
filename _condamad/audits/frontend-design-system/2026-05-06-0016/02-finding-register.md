# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-guard | frontend-design-system | E-001, E-002, E-003, E-004, E-005, E-006, E-007, E-008 | Design-system governance is executable and green. | Keep guards mandatory for future frontend style stories. | no |
| F-002 | Medium | High | legacy-surface | frontend-design-system | E-003, E-009 | CSS fallback literals still preserve alternate visual decisions beside canonical tokens. | Reduce fallbacks in bounded batches and update both fallback registries in the same change. | yes |
| F-003 | Medium | High | legacy-surface | frontend-design-system | E-004, E-010 | Styling decisions still exist in TSX for dynamic bridges and style-prop pass-throughs. | Convert removable bridges to CSS custom properties/classes; keep only runtime geometry and explicit pass-throughs. | yes |
| F-004 | Medium | High | duplicate-responsibility | frontend-design-system | E-011 | Local literals still compete with semantic tokens across many product surfaces. | Migrate by coherent product surface with before/after counts and registry updates when durable tokens are introduced. | yes |
| F-005 | Medium | High | legacy-surface | frontend-design-system | E-012 | No Legacy is controlled but active through migration-only selectors and compatibility token aliases. | Retire chat/admin legacy selectors and compatibility aliases through scoped stories. | yes |
| F-006 | Info | High | missing-guard | frontend-design-system | E-007 | Build remains operational but main JS chunk is oversized. | Track separately under frontend performance, not this design-system cleanup batch. | no |

## F-001 - Frontend design-system governance remains green

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-001, E-002, E-003, E-004, E-005, E-006, E-007, E-008.
- Expected rule: token namespaces, typography roles, inline styles, CSS fallbacks, and legacy surfaces are governed by registries and executable tests.
- Actual state: all targeted and full frontend validation commands passed.
- Impact: Design-system governance is executable and green.
- Recommended action: Keep guards mandatory for future frontend style stories.
- Story candidate: no
- Suggested archetype: no-story-observation

Files to modify: see `00-audit-report.md`, section `F-001`.

## F-002 - CSS fallback debt remains active but much smaller

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-003, E-009.
- Expected rule: CSS fallbacks are exact, classified, and reduced when canonical tokens are guaranteed.
- Actual state: 24 allowlisted fallback exceptions remain across 10 CSS files.
- Impact: CSS fallback literals still preserve alternate visual decisions beside canonical tokens.
- Recommended action: Reduce fallbacks in bounded batches and update both fallback registries in the same change.
- Story candidate: yes
- Suggested archetype: css-fallback-debt-reduction

Files to modify: see `00-audit-report.md`, section `F-002`.

## F-003 - Inline style exceptions remain dynamic but still bypass CSS ownership

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-004, E-010.
- Expected rule: static styling lives in CSS, with inline style only for exact dynamic exceptions.
- Actual state: 14 inline style attributes remain across 9 TSX files.
- Impact: Styling decisions still exist in TSX for dynamic bridges and style-prop pass-throughs.
- Recommended action: Convert removable bridges to CSS custom properties/classes; keep only runtime geometry and explicit pass-throughs.
- Story candidate: yes
- Suggested archetype: inline-style-debt-reduction

Files to modify: see `00-audit-report.md`, section `F-003`.

## F-004 - Hardcoded visual and typography decisions remain broad

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-011.
- Expected rule: repeated visual decisions converge toward tokens, roles, and utilities.
- Actual state: 116 files still contain hardcoded visual or typography signals.
- Impact: Local literals still compete with semantic tokens across many product surfaces.
- Recommended action: Migrate by coherent product surface with before/after counts and registry updates when durable tokens are introduced.
- Story candidate: yes
- Suggested archetype: hardcoded-design-value-reduction

Files to modify: see `00-audit-report.md`, section `F-004`.

## F-005 - Legacy selector and compatibility token surfaces still need exit work

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-012.
- Expected rule: legacy selectors and compatibility token aliases are temporary and classified.
- Actual state: 17 registry rows remain active.
- Impact: No Legacy is controlled but active through migration-only selectors and compatibility token aliases.
- Recommended action: Retire chat/admin legacy selectors and compatibility aliases through scoped stories.
- Story candidate: yes
- Suggested archetype: legacy-style-surface-extinction

Files to modify: see `00-audit-report.md`, section `F-005`.

## F-006 - Build output remains oversized

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-007.
- Expected rule: production build remains operational.
- Actual state: build passes with chunk-size warning.
- Impact: Build remains operational but main JS chunk is oversized.
- Recommended action: Track separately under frontend performance, not this design-system cleanup batch.
- Story candidate: no
- Suggested archetype: no-story-observation

Files to modify: see `00-audit-report.md`, section `F-006`.
