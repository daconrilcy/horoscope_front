# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-canonical-owner | frontend-design-system | E-001, E-002, E-003, E-004, E-005 | The prior High ownership risk is now governed by registries and executable guardrails. | Keep `RG-044` through `RG-050` active and require future frontend stories to cite them. | no |
| F-002 | Medium | High | duplicate-responsibility | frontend-design-system | E-008, E-009, E-010, E-014 | Hardcoded colors, spacing, radius, shadow, and typography declarations still duplicate token responsibilities outside the first migrated batch. | Continue phased token migration by high-repeat component/page clusters and track before/after counts per batch. | yes |
| F-003 | Medium | High | legacy-surface | frontend-design-system | E-004, E-011, E-015 | The inline-style guard prevents unclassified growth, but static style debt remains preserved in exact allowlists. | Convert allowlisted static styles to CSS by surface, keeping only dynamic custom properties, geometry, and runtime colors. | yes |
| F-004 | Medium | High | legacy-surface | frontend-design-system | E-004, E-012 | CSS fallback growth is guarded, but 329 fallback usages remain active as migration-only or compatibility debt. | Reduce fallback exceptions by moving required tokens to canonical imports and replacing local literal fallbacks with canonical tokens. | yes |
| F-005 | Low | Medium | missing-test-coverage | frontend-design-system | E-013 | Whole-suite validation is not fully deterministic, which can hide or misattribute frontend regressions during CI triage. | Investigate the full-run-only `HelpPage.test.tsx` failure and isolate shared mocks, timers, DOM state, or test order leakage. | yes |

## F-001 - Token ownership risk is materially remediated

- Severity: Info
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-design-system
- Evidence: E-001, E-002, E-003, E-004, E-005.
- Expected rule: A canonical token owner and executable guards prevent unclassified token namespace drift.
- Actual state: `frontend/src/styles/token-namespace-registry.md`, `typography-roles.md`, `css-fallback-allowlist.md`, `legacy-style-surface-registry.md`, and guard tests exist. `RG-044` through `RG-050` encode the same durable invariants.
- Impact: The prior High ownership risk is now governed by registries and executable guardrails.
- Recommended action: Keep `RG-044` through `RG-050` active and require future frontend stories to cite them.
- Story candidate: no
- Suggested archetype: no-story-observation

## F-002 - Hardcoded visual and typography values remain broad

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-008, E-009, E-010, E-014.
- Expected rule: Repeated visual and typography decisions migrate toward semantic tokens or classified exceptions.
- Actual state: Scans still show 1890 color-like hits, 2627 spacing/radius/shadow hits, and 1533 typography hits outside tokenized declarations. The first migrated batch is guarded, but the repo-wide debt remains large.
- Impact: Hardcoded colors, spacing, radius, shadow, and typography declarations still duplicate token responsibilities outside the first migrated batch.
- Recommended action: Continue phased token migration by high-repeat component/page clusters and track before/after counts per batch.
- Story candidate: yes
- Suggested archetype: hardcoded-design-value-reduction

## F-003 - Inline-style allowlist still preserves static style debt

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-004, E-011, E-015.
- Expected rule: Static styles live in CSS; inline styles are limited to runtime values that are not practical as static CSS.
- Actual state: The guard verifies no unclassified inline style exists, and three audited files now have zero inline styles. However, 85 inline style attributes remain, including static style entries in the allowlist.
- Impact: The inline-style guard prevents unclassified growth, but static style debt remains preserved in exact allowlists.
- Recommended action: Convert allowlisted static styles to CSS by surface, keeping only dynamic custom properties, geometry, and runtime colors.
- Story candidate: yes
- Suggested archetype: inline-style-debt-reduction

## F-004 - CSS fallback allowlist remains large

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-004, E-012.
- Expected rule: Fallback literals are rare, classified, and either permanent dynamic bridges or migration-only exceptions with exit conditions.
- Actual state: The guard blocks unclassified fallback growth, but 329 fallback usages remain active.
- Impact: CSS fallback growth is guarded, but 329 fallback usages remain active as migration-only or compatibility debt.
- Recommended action: Reduce fallback exceptions by moving required tokens to canonical imports and replacing local literal fallbacks with canonical tokens.
- Story candidate: yes
- Suggested archetype: css-fallback-debt-reduction

## F-005 - Full frontend test suite is not deterministic enough

- Severity: Low
- Confidence: Medium
- Category: missing-test-coverage
- Domain: frontend-design-system
- Evidence: E-013.
- Expected rule: Whole-suite frontend validation should be repeatable enough to trust as a regression signal.
- Actual state: `npm run test` failed once in `HelpPage.test.tsx`, but `npm run test -- HelpPage` passed immediately after.
- Impact: Whole-suite validation is not fully deterministic, which can hide or misattribute frontend regressions during CI triage.
- Recommended action: Investigate the full-run-only `HelpPage.test.tsx` failure and isolate shared mocks, timers, DOM state, or test order leakage.
- Story candidate: yes
- Suggested archetype: frontend-test-isolation-hardening
