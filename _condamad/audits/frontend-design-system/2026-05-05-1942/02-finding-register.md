# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-canonical-owner | frontend-design-system | E-001, E-002, E-003, E-004, E-005, E-006 | Previous High governance risk remains controlled. | Keep `RG-044` through `RG-050` active for future frontend stories. | no |
| F-002 | Medium | High | runtime-contract-drift | frontend-design-system | E-007, E-008 | Full Vitest suite is red and the guard encourages reintroducing literals. | Update `visual-smoke.test.tsx` to assert tokenized typography or resolved token values. | yes |
| F-003 | Medium | High | legacy-surface | frontend-design-system | E-003, E-004, E-010 | CSS fallbacks remain as alternate literal visual decisions. | Reduce fallback exceptions by bounded batches and keep registries exact. | yes |
| F-004 | Medium | High | legacy-surface | frontend-design-system | E-003, E-004, E-009 | Inline style exceptions keep visual decisions in TSX. | Move removable entries to CSS/custom properties and keep dynamic bridges only. | yes |
| F-005 | Medium | High | duplicate-responsibility | frontend-design-system | E-011 | Hardcoded values compete with semantic token ownership across broad surfaces. | Continue phased migration by product surface and highest-repeat clusters. | yes |
| F-006 | Medium | High | legacy-surface | frontend-design-system | E-002, E-003, E-012 | No Legacy remains a controlled but active frontend style debt surface. | Retire legacy selectors and compatibility token aliases through exact registry updates. | yes |

## F-001 - Frontend design-system governance remains active

- Severity: Info
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-design-system
- Evidence: E-001, E-002, E-003, E-004, E-005, E-006.
- Expected rule: frontend design-system ownership is governed by registries and executable guards.
- Actual state: `RG-044` through `RG-050` are active, targeted guard tests pass, lint passes, and build passes.
- Impact: Previous High governance risk remains controlled.
- Recommended action: Keep `RG-044` through `RG-050` active for future frontend stories.
- Story candidate: no
- Suggested archetype: no-story-observation

## F-002 - Visual smoke guard still expects pre-token typography literals

- Severity: Medium
- Confidence: High
- Category: runtime-contract-drift
- Domain: frontend-design-system
- Evidence: E-007, E-008.
- Expected rule: regression guards assert the post-refactor tokenized design-system contract.
- Actual state: `visual-smoke.test.tsx` expects `18px`, `12px`, and `500` while `App.css` uses typography tokens.
- Impact: Full Vitest suite is red and the guard encourages reintroducing literals.
- Recommended action: Update `visual-smoke.test.tsx` to assert tokenized typography or resolved token values.
- Story candidate: yes
- Suggested archetype: design-system-guard-contract-realignment

Files to modify: see `00-audit-report.md`, section `F-002`.

## F-003 - CSS fallback debt remains active but bounded

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-003, E-004, E-010.
- Expected rule: CSS fallback literals are rare, classified, and reduced over time.
- Actual state: 68 fallback exceptions remain across 14 CSS files and two guard/registry files.
- Impact: CSS fallbacks remain as alternate literal visual decisions.
- Recommended action: Reduce fallback exceptions by bounded batches and keep registries exact.
- Story candidate: yes
- Suggested archetype: css-fallback-debt-reduction

Files to modify: see `00-audit-report.md`, section `F-003`.

## F-004 - Inline style exceptions remain active

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-003, E-004, E-009.
- Expected rule: static styling lives in CSS files; inline styles remain exact dynamic exceptions only.
- Actual state: 16 inline style exceptions remain across 10 TSX files and two guard/registry files.
- Impact: Inline style exceptions keep visual decisions in TSX.
- Recommended action: Move removable entries to CSS/custom properties and keep dynamic bridges only.
- Story candidate: yes
- Suggested archetype: inline-style-debt-reduction

Files to modify: see `00-audit-report.md`, section `F-004`.

## F-005 - Hardcoded visual and typography decisions remain broad

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-011.
- Expected rule: repeated visual decisions converge toward semantic tokens or exact classified exceptions.
- Actual state: 107 application files contain color, dimension, spacing, radius, shadow, or typography literal signals.
- Impact: Hardcoded values compete with semantic token ownership across broad surfaces.
- Recommended action: Continue phased migration by product surface and highest-repeat clusters.
- Story candidate: yes
- Suggested archetype: hardcoded-design-value-reduction

Files to modify: see `00-audit-report.md`, section `F-005`.

## F-006 - Legacy selector and compatibility token surfaces still need exit work

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-002, E-003, E-012.
- Expected rule: legacy selectors and compatibility token aliases are classified and shrink over time.
- Actual state: 6 files contain active classified legacy or compatibility surfaces.
- Impact: No Legacy remains a controlled but active frontend style debt surface.
- Recommended action: Retire legacy selectors and compatibility token aliases through exact registry updates.
- Story candidate: yes
- Suggested archetype: legacy-style-surface-extinction

Files to modify: see `00-audit-report.md`, section `F-006`.
