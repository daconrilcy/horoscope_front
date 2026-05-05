# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-canonical-owner | frontend-design-system | E-001, E-003, E-004, E-005, E-006 | The previous High ownership risk remains governed by registries and executable guardrails. | Keep `RG-044` through `RG-050` active and require future frontend stories to cite them. | no |
| F-002 | Medium | High | legacy-surface | frontend-design-system | E-004, E-009 | CSS fallback debt is now exactly classified, but literal fallback values still remain active as compatibility or migration-only alternate values. | Reduce fallback exceptions by bounded batches, updating `css-fallback-allowlist.md` and `design-system-allowlist.ts` with every removal. | yes |
| F-003 | Medium | High | legacy-surface | frontend-design-system | E-004, E-008 | Inline style usage is small and guarded, but it still bypasses the project-level stylesheet rule unless each exception remains justified as runtime geometry or a style-prop bridge. | Move removable inline styles to CSS/custom properties and keep only explicitly dynamic exceptions with exact tests. | yes |
| F-004 | Medium | High | duplicate-responsibility | frontend-design-system | E-010, E-004 | Hardcoded colors, spacing, radius, shadow, and typography declarations still compete with semantic token ownership across a broad frontend surface. | Continue phased migration by highest-repeat clusters, with before/after counts and guard updates per batch. | yes |

## F-001 - Token ownership and anti-drift guardrails remain active

- Severity: Info
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-design-system
- Evidence: E-001, E-003, E-004, E-005, E-006.
- Expected rule: A canonical token owner and executable guards prevent unclassified token namespace, fallback, inline-style, and legacy-style drift.
- Actual state: `RG-044` through `RG-050` are active, registries exist, targeted design-system tests pass, lint passes, and the full Vitest suite passes.
- Impact: The previous High ownership risk remains governed by registries and executable guardrails.
- Recommended action: Keep `RG-044` through `RG-050` active and require future frontend stories to cite them.
- Story candidate: no
- Suggested archetype: no-story-observation

## F-002 - CSS fallback debt remains active but exactly classified

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-004, E-009.
- Expected rule: Fallback literals are rare, classified, and removed when the canonical token is guaranteed.
- Actual state: 117 CSS fallback usages remain across 19 files. The guard now validates them against exact registries, so this is controlled debt rather than unclassified drift.
- Impact: CSS fallback debt is now exactly classified, but literal fallback values still remain active as compatibility or migration-only alternate values.
- Recommended action: Reduce fallback exceptions by bounded batches, updating `css-fallback-allowlist.md` and `design-system-allowlist.ts` with every removal.
- Story candidate: yes
- Suggested archetype: css-fallback-debt-reduction

Files to modify: see `00-audit-report.md`, section `F-002 - CSS Fallback Debt: 19 Files`.

## F-003 - Inline style exceptions remain active

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-004, E-008.
- Expected rule: Static styling lives in CSS files; inline style usage is limited to exact dynamic exceptions or a documented technical bridge.
- Actual state: 16 inline `style=` attributes remain across 10 TSX files. Targeted tests prove the current entries are allowlisted, but the surface remains an exception to the strict no-inline-style project rule.
- Impact: Inline style usage is small and guarded, but it still bypasses the project-level stylesheet rule unless each exception remains justified as runtime geometry or a style-prop bridge.
- Recommended action: Move removable inline styles to CSS/custom properties and keep only explicitly dynamic exceptions with exact tests.
- Story candidate: yes
- Suggested archetype: inline-style-debt-reduction

Files to modify: see `00-audit-report.md`, section `F-003 - Inline Style Debt: 10 Files`.

## F-004 - Hardcoded visual and typography decisions remain broad

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-010, E-004.
- Expected rule: Repeated visual decisions migrate toward semantic tokens, shared utilities, or exact classified exceptions.
- Actual state: Static scans find hardcoded visual or typography declarations across 109 CSS/TSX files. The design-system guard suite is active, but it currently guards migrated literals and exact exceptions rather than eliminating the whole repo-wide debt.
- Impact: Hardcoded colors, spacing, radius, shadow, and typography declarations still compete with semantic token ownership across a broad frontend surface.
- Recommended action: Continue phased migration by highest-repeat clusters, with before/after counts and guard updates per batch.
- Story candidate: yes
- Suggested archetype: hardcoded-design-value-reduction

Files to modify: see `00-audit-report.md`, section `F-004 - Hardcoded Visual And Typography Debt: 109 Files`.
