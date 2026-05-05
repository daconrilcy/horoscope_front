# Story Candidates - frontend-design-system

## SC-001 - Reduce classified CSS fallback debt

- Candidate ID: SC-001
- Source finding: F-002
- Suggested story title: Reduce classified CSS fallback debt
- Suggested archetype: css-fallback-debt-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-048`, `RG-050`, `frontend/src/styles/css-fallback-allowlist.md`, `frontend/src/tests/design-system-allowlist.ts`
- Draft objective: Remove a bounded batch of CSS fallback literals from the 19-file active fallback surface while preserving visual behavior and exact guard parity.
- Must include:
  - Pick one bounded batch from the file list in `00-audit-report.md`.
  - Replace migration-only `var(--token, literal)` usages with canonical `var(--token)` or a stronger semantic token.
  - Update `frontend/src/styles/css-fallback-allowlist.md`.
  - Update `frontend/src/tests/design-system-allowlist.ts`.
  - Keep `frontend/src/tests/css-fallback-policy.test.ts` passing.
- Validation hints:
  - `cd frontend && npm run test -- css-fallback design-system`
  - `cd frontend && npm run lint`
  - Before/after count from `rg -n "var\\([^)]*," frontend\\src -g "*.css"`.
- Blockers: None identified.

## SC-002 - Reduce inline style exceptions

- Candidate ID: SC-002
- Source finding: F-003
- Suggested story title: Reduce inline style exceptions
- Suggested archetype: inline-style-debt-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-047`, `RG-050`, `frontend/src/tests/inline-style-allowlist.ts`, `frontend/src/tests/design-system-allowlist.ts`
- Draft objective: Remove or reclassify a bounded batch of inline `style=` usages from the 10-file active inline-style surface.
- Must include:
  - Pick one bounded batch from the file list in `00-audit-report.md`.
  - Move static declarations to CSS files.
  - Prefer CSS custom properties/classes for runtime geometry when practical.
  - Keep only entries that are truly runtime-driven or component style-prop bridges.
  - Update inline-style allowlists and tests exactly.
- Validation hints:
  - `cd frontend && npm run test -- inline-style design-system`
  - `cd frontend && npm run lint`
  - Before/after count from `rg -n "style=" frontend\\src -g "*.tsx"`.
- Blockers: Decide whether the project-level "no inline style" rule permits documented dynamic CSS custom property bridges.

## SC-003 - Migrate next hardcoded visual and typography cluster

- Candidate ID: SC-003
- Source finding: F-004
- Suggested story title: Migrate next hardcoded visual and typography cluster
- Suggested archetype: hardcoded-design-value-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-044`, `RG-045`, `RG-046`, `RG-049`, `RG-050`, `frontend/src/styles/design-tokens.css`, `frontend/src/styles/token-namespace-registry.md`, `frontend/src/styles/typography-roles.md`
- Draft objective: Convert the next high-repeat CSS/TSX cluster to semantic tokens or shared utilities without broad visual churn.
- Must include:
  - Pick one cohesive cluster from the 109-file list in `00-audit-report.md`.
  - Capture before/after counts for color, typography, spacing, radius, and shadow declarations.
  - Add semantic tokens only when they remove repeated design decisions.
  - Update token namespace and typography registries if new token families or roles are introduced.
  - Preserve existing visual tests or update them only when the target visual contract intentionally changes.
- Validation hints:
  - `cd frontend && npm run test -- design-system theme-tokens`
  - `cd frontend && npm run lint`
  - `cd frontend && npm run build`
- Blockers: Choose the first cluster by product priority; highest measured density is currently `App.css`, `AdminPromptsPage.css`, `HelpPage.css`, `Settings.css`, and `AstrologerProfilePage.css`.
