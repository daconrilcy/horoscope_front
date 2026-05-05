# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-canonical-owner | frontend-design-system | E-001, E-002, E-003, E-004, E-005, E-006, E-007, E-008 | Previous runtime guard drift is closed and governance remains executable. | Keep `RG-044` through `RG-050` active for future frontend stories. | no |
| F-002 | Medium | High | legacy-surface | frontend-design-system | E-003, E-009 | CSS fallback literals remain active alternate visual decisions. | Reduce fallbacks in bounded batches, starting with `NatalChartPage.css`, and keep registries exact. | yes |
| F-003 | Medium | High | legacy-surface | frontend-design-system | E-004, E-010 | Inline style exceptions keep styling decisions in TSX. | Convert removable bridges to CSS/custom properties and keep dynamic exceptions exact. | yes |
| F-004 | Medium | High | duplicate-responsibility | frontend-design-system | E-011 | Hardcoded values compete with semantic token ownership across broad surfaces. | Continue phased migration by coherent product surface with before/after counts. | yes |
| F-005 | Medium | High | legacy-surface | frontend-design-system | E-012 | No Legacy remains controlled but active through selector and token alias surfaces. | Retire chat/admin legacy selectors and compatibility aliases through exact registry updates. | yes |
| F-006 | Info | High | missing-guard | frontend-design-system | E-007 | Build is operational but the main chunk remains oversized. | Track under a separate frontend performance audit/story. | no |

## F-001 - Frontend design-system governance is green after refactor

- Severity: Info
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-design-system
- Evidence: E-001, E-002, E-003, E-004, E-005, E-006, E-007, E-008.
- Expected rule: frontend design-system ownership is governed by registries and executable guards.
- Actual state: targeted guards, full Vitest suite, lint, and build pass.
- Impact: Previous runtime guard drift is closed and governance remains executable.
- Recommended action: Keep `RG-044` through `RG-050` active for future frontend stories.
- Story candidate: no
- Suggested archetype: no-story-observation

Files to modify: see `00-audit-report.md`, section `F-001`.

## F-002 - CSS fallback debt remains active and concentrated

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-003, E-009.
- Expected rule: CSS fallback literals are rare, classified, and reduced over time.
- Actual state: 54 fallback exceptions remain across 10 CSS files plus two guard/registry files.
- Impact: CSS fallback literals remain active alternate visual decisions.
- Recommended action: Reduce fallbacks in bounded batches, starting with `NatalChartPage.css`, and keep registries exact.
- Story candidate: yes
- Suggested archetype: css-fallback-debt-reduction

Files to modify: see `00-audit-report.md`, section `F-002`.

## F-003 - Inline style exceptions remain dynamic but still bypass CSS ownership

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-004, E-010.
- Expected rule: static styling lives in CSS files; inline styles remain exact dynamic exceptions only.
- Actual state: 15 inline style attributes remain across 9 TSX files and two guard/registry files.
- Impact: Inline style exceptions keep styling decisions in TSX.
- Recommended action: Convert removable bridges to CSS/custom properties and keep dynamic exceptions exact.
- Story candidate: yes
- Suggested archetype: inline-style-debt-reduction

Files to modify: see `00-audit-report.md`, section `F-003`.

## F-004 - Hardcoded visual and typography decisions remain broad

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-011.
- Expected rule: repeated visual decisions converge toward semantic tokens or exact classified exceptions.
- Actual state: 106 application files contain color, dimension, spacing, radius, shadow, or typography literal signals.
- Impact: Hardcoded values compete with semantic token ownership across broad surfaces.
- Recommended action: Continue phased migration by coherent product surface with before/after counts.
- Story candidate: yes
- Suggested archetype: hardcoded-design-value-reduction

Files to modify: see `00-audit-report.md`, section `F-004`.

## F-005 - Legacy selector and compatibility token surfaces still need exit work

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-012.
- Expected rule: legacy selectors and compatibility token aliases are classified and shrink over time.
- Actual state: `App.css`, `AdminPromptsPage.css`, `theme.css`, and registries retain active migration-only or compatibility surfaces.
- Impact: No Legacy remains controlled but active through selector and token alias surfaces.
- Recommended action: Retire chat/admin legacy selectors and compatibility aliases through exact registry updates.
- Story candidate: yes
- Suggested archetype: legacy-style-surface-extinction

Files to modify: see `00-audit-report.md`, section `F-005`.

## F-006 - Build output remains oversized

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-007.
- Expected rule: build health and performance budgets should be tracked separately from design-system correctness.
- Actual state: build passes with Vite chunk-size warning.
- Impact: Build is operational but the main chunk remains oversized.
- Recommended action: Track under a separate frontend performance audit/story.
- Story candidate: no
- Suggested archetype: no-story-observation

Files to modify: see `00-audit-report.md`, section `F-006`.
