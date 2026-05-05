# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-canonical-owner | frontend-design-system | E-001, E-002, E-003, E-004, E-005, E-007 | The previous High ownership risk remains governed by registries and executable guardrails. | Keep `RG-044` through `RG-050` active and require future frontend stories to cite them. | no |
| F-002 | Medium | High | runtime-contract-drift | frontend-design-system | E-010, E-013, E-014 | Maintainers can read `css-fallback-allowlist.md` as the exact source of truth while the executable guard actually relies on `design-system-allowlist.ts`, so the documented exit conditions are incomplete. | Make the markdown registry and executable fallback allowlist a single exact contract, or generate one from the other; add a parity guard. | yes |
| F-003 | Medium | High | legacy-surface | frontend-design-system | E-008, E-009, E-003, E-004 | Inline-style debt is much smaller but still keeps static layout, color, and fieldset reset decisions in TSX allowlists. | Convert static entries to CSS by surface, keep only dynamic custom properties, runtime geometry, and component style-prop bridges. | yes |
| F-004 | Medium | High | legacy-surface | frontend-design-system | E-010, E-011, E-003, E-004 | CSS fallback debt is reduced but still lets literal values remain as compatibility or migration-only alternate values across 30 CSS files. | Reduce fallback exceptions by shared UI/layout components first, then page-level CSS, updating the exact allowlist and registry per batch. | yes |
| F-005 | Medium | High | duplicate-responsibility | frontend-design-system | E-012, E-015 | Hardcoded visual and typography decisions still compete with semantic token ownership outside the migrated batches. | Continue phased migration by highest-repeat clusters with before/after counts and no expansion of unclassified token namespaces. | yes |

## F-001 - Token ownership and anti-drift guardrails remain active

- Severity: Info
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-design-system
- Evidence: E-001, E-002, E-003, E-004, E-005, E-007.
- Expected rule: A canonical token owner and executable guards prevent unclassified token namespace drift.
- Actual state: `RG-044` through `RG-050` are active, registries remain present, targeted guard tests pass, lint passes, and the full Vitest suite passes.
- Impact: The previous High ownership risk remains governed by registries and executable guardrails.
- Recommended action: Keep `RG-044` through `RG-050` active and require future frontend stories to cite them.
- Story candidate: no
- Suggested archetype: no-story-observation

## F-002 - CSS fallback registry and executable allowlist have drifted

- Severity: Medium
- Confidence: High
- Category: runtime-contract-drift
- Domain: frontend-design-system
- Evidence: E-010, E-013, E-014.
- Expected rule: The documented fallback registry and the executable fallback guard describe the same exact exceptions.
- Actual state: `frontend/src/styles/css-fallback-allowlist.md` says the fallback allowlist is exact but documents only 7 rows, while `CSS_FALLBACK_EXCEPTIONS` in `frontend/src/tests/design-system-allowlist.ts` is the executable 165-entry source.
- Impact: Maintainers can read `css-fallback-allowlist.md` as the exact source of truth while the executable guard actually relies on `design-system-allowlist.ts`, so the documented exit conditions are incomplete.
- Recommended action: Make the markdown registry and executable fallback allowlist a single exact contract, or generate one from the other; add a parity guard.
- Story candidate: yes
- Suggested archetype: design-system-contract-parity

## F-003 - Inline-style debt is reduced but still active

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-008, E-009, E-003, E-004.
- Expected rule: Static styles live in CSS files; inline styles are limited to exact dynamic exceptions.
- Actual state: 30 `style` attributes remain across 17 TSX files. The guard allowlists them, but static entries remain in settings/profile/not-found/form/prediction/UI skeleton surfaces.
- Impact: Inline-style debt is much smaller but still keeps static layout, color, and fieldset reset decisions in TSX allowlists.
- Recommended action: Convert static entries to CSS by surface, keep only dynamic custom properties, runtime geometry, and component style-prop bridges.
- Story candidate: yes
- Suggested archetype: inline-style-debt-reduction

## F-004 - CSS fallback debt remains broad

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-010, E-011, E-003, E-004.
- Expected rule: Fallback literals are rare, classified, and attached to concrete exit conditions.
- Actual state: 165 CSS fallback usages remain across 30 CSS files. The current executable guard prevents unclassified growth, but active fallback literals still preserve alternate values.
- Impact: CSS fallback debt is reduced but still lets literal values remain as compatibility or migration-only alternate values across 30 CSS files.
- Recommended action: Reduce fallback exceptions by shared UI/layout components first, then page-level CSS, updating the exact allowlist and registry per batch.
- Story candidate: yes
- Suggested archetype: css-fallback-debt-reduction

## F-005 - Hardcoded visual and typography decisions remain broad

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-012, E-015.
- Expected rule: Repeated visual decisions migrate toward semantic tokens or exact classified exceptions.
- Actual state: Static scans still show 1671 color-like hits, 1570 typography declaration hits, and 2653 spacing/radius/shadow declaration hits in `frontend/src`. The CS-027 migrated literals remain guarded, but repo-wide debt is still broad.
- Impact: Hardcoded visual and typography decisions still compete with semantic token ownership outside the migrated batches.
- Recommended action: Continue phased migration by highest-repeat clusters with before/after counts and no expansion of unclassified token namespaces.
- Story candidate: yes
- Suggested archetype: hardcoded-design-value-reduction
