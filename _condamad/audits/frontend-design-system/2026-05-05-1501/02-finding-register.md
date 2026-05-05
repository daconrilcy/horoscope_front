# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-canonical-owner | frontend-design-system | E-001, E-003, E-004, E-005 | The previous canonical-token ownership risk remains governed by registries and executable guardrails. | Keep `RG-044` through `RG-050` active and require future frontend stories to cite them. | no |
| F-002 | Medium | High | duplicate-responsibility | frontend-design-system | E-013, E-014, E-015 | Hardcoded visual and typography decisions still compete with semantic token ownership outside the already guarded migrated batches. | Continue phased migration by highest-repeat component/page clusters, with before/after counts and no expansion of unclassified token namespaces. | yes |
| F-003 | Medium | High | legacy-surface | frontend-design-system | E-009, E-010, E-004, E-005 | Inline-style debt is smaller but still keeps static layout, color, and typography decisions in TSX allowlists. | Convert the next batch of static inline styles to CSS, prioritizing `TurningPointsList.tsx`, then settings/profile/not-found surfaces. | yes |
| F-004 | Medium | High | legacy-surface | frontend-design-system | E-011, E-012, E-004, E-005 | CSS fallback debt is smaller but still lets literal values remain as compatibility or migration-only alternate values. | Reduce fallback exceptions by shared UI component first, then page-level CSS, updating `css-fallback-allowlist.md` and tests per batch. | yes |
| F-005 | Info | Medium | missing-test-coverage | frontend-design-system | E-008 | The previously observed full-suite HelpPage failure was not reproduced, so it is no longer an active blocker in this audit. | Keep normal full-suite execution in validation; reopen a focused story only if the failure recurs. | no |

## F-001 - Token ownership and design-system guardrails remain active

- Severity: Info
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-design-system
- Evidence: E-001, E-003, E-004, E-005.
- Expected rule: A canonical token owner and executable guards prevent unclassified token namespace drift.
- Actual state: `RG-044` through `RG-050` are active, registries remain present, and targeted design-system tests pass.
- Impact: The previous canonical-token ownership risk remains governed by registries and executable guardrails.
- Recommended action: Keep `RG-044` through `RG-050` active and require future frontend stories to cite them.
- Story candidate: no
- Suggested archetype: no-story-observation

## F-002 - Hardcoded visual and typography decisions remain broad outside migrated batches

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-013, E-014, E-015.
- Expected rule: Repeated visual decisions migrate toward semantic tokens or exact classified exceptions.
- Actual state: Static scans still show 1899 color-like hits and 4172 visual or typography declarations across frontend CSS/TSX surfaces. The CS-027 exact migrated literals remain guarded with no reintroduction in the checked files.
- Impact: Hardcoded visual and typography decisions still compete with semantic token ownership outside the already guarded migrated batches.
- Recommended action: Continue phased migration by highest-repeat component/page clusters, with before/after counts and no expansion of unclassified token namespaces.
- Story candidate: yes
- Suggested archetype: hardcoded-design-value-reduction

## F-003 - Inline-style debt is reduced but still preserves static CSS decisions

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-009, E-010, E-004, E-005.
- Expected rule: Static styles live in CSS files; inline styles are limited to exact dynamic exceptions.
- Actual state: TSX `style` attributes dropped from 85 to 68, and all remaining entries are guarded by the central allowlist. Static entries remain in `TurningPointsList.tsx`, `AccountSettings.tsx`, `AstrologerProfilePage.tsx`, and `NotFoundPage.tsx`.
- Impact: Inline-style debt is smaller but still keeps static layout, color, and typography decisions in TSX allowlists.
- Recommended action: Convert the next batch of static inline styles to CSS, prioritizing `TurningPointsList.tsx`, then settings/profile/not-found surfaces.
- Story candidate: yes
- Suggested archetype: inline-style-debt-reduction

## F-004 - CSS fallback allowlist is smaller but remains broad

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-011, E-012, E-004, E-005.
- Expected rule: Fallback literals are rare, classified, and attached to a concrete exit condition.
- Actual state: CSS fallback usages dropped from 329 to 262, and guard tests validate the exact allowlist. Fallbacks remain in shared UI component CSS and page CSS, including `Select`, `Modal`, `Card`, `Field`, `Button`, `UserAvatar`, `LockedSection`, `EmptyState`, `Skeleton`, `HelpPage.css`, and `App.css`.
- Impact: CSS fallback debt is smaller but still lets literal values remain as compatibility or migration-only alternate values.
- Recommended action: Reduce fallback exceptions by shared UI component first, then page-level CSS, updating `css-fallback-allowlist.md` and tests per batch.
- Story candidate: yes
- Suggested archetype: css-fallback-debt-reduction

## F-005 - Previous HelpPage full-suite flake is not reproduced

- Severity: Info
- Confidence: Medium
- Category: missing-test-coverage
- Domain: frontend-design-system
- Evidence: E-008.
- Expected rule: Whole-suite frontend validation should be repeatable enough to trust as a regression signal.
- Actual state: The full `npm run test` run passed with 113 test files and 1234 passing tests. The `HelpPage.test.tsx` failure from `_condamad/audits/frontend-design-system/2026-05-05-1411/` did not recur.
- Impact: The previously observed full-suite HelpPage failure was not reproduced, so it is no longer an active blocker in this audit.
- Recommended action: Keep normal full-suite execution in validation; reopen a focused story only if the failure recurs.
- Story candidate: no
- Suggested archetype: no-story-observation
