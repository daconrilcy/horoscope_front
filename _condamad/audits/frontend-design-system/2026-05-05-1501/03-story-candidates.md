# Story Candidates - frontend-design-system

## SC-001 - Reduire les valeurs visuelles et typographiques hardcodees restantes

- Candidate ID: SC-001
- Source finding: F-002
- Suggested story title: Reduire la dette de valeurs visuelles hardcodees hors lots deja migres
- Suggested archetype: hardcoded-design-value-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-044`, `RG-045`, `RG-046`, token namespace registry, typography roles
- Draft objective: Continue the design-token migration by reducing repeated color, spacing, radius, shadow, and typography literals in the highest-impact CSS clusters that are not yet covered by the migrated batch.
- Must include: before/after static counts, explicit migrated file list, no expansion of unclassified token namespaces, and registry updates only when a permanent semantic token is introduced.
- Validation hints: `npm run test -- design-system theme-tokens`; targeted `rg` counts for migrated files; `npm run lint`; visual smoke for touched page-level surfaces.
- Blockers: Product/design decision may be needed when near-equivalent literal values should converge to one semantic token.

## SC-002 - Convertir le prochain lot de styles inline statiques vers CSS

- Candidate ID: SC-002
- Source finding: F-003
- Suggested story title: Supprimer les styles inline statiques restants de `TurningPointsList`
- Suggested archetype: inline-style-debt-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-047`, inline-style allowlist, CSS-only style rule
- Draft objective: Reduce the exact inline-style allowlist by moving static layout, typography, and color styles from `TurningPointsList.tsx` into a CSS module/file while preserving genuinely dynamic runtime values.
- Must include: classification of each touched inline style as static or dynamic, CSS extraction for static entries, allowlist reduction, and no new `style` attributes.
- Validation hints: `npm run test -- inline-style design-system TurningPointsEnriched`; scan `rg -n "style=\{" frontend/src/components/prediction/TurningPointsList.tsx`; `npm run lint`.
- Blockers: None identified.

## SC-003 - Reduire les fallbacks CSS allowlistes dans les composants UI partages

- Candidate ID: SC-003
- Source finding: F-004
- Suggested story title: Reduire les fallbacks `var(--token, value)` des composants UI partages
- Suggested archetype: css-fallback-debt-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-048`, CSS fallback allowlist, token namespace registry
- Draft objective: Replace migration-only CSS fallback literals in shared UI components with required canonical tokens or documented imports so component CSS stops carrying hidden alternate values.
- Must include: before/after fallback count, updated `css-fallback-allowlist.md`, no unclassified fallback, and component tests for changed UI primitives.
- Validation hints: `npm run test -- css-fallback design-system Button Card Field Modal Select UserAvatar Skeleton`; targeted `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," frontend/src/components/ui -g "*.css"`; `npm run lint`.
- Blockers: Some fallbacks may require a decision about whether isolated UI component tests must load global token CSS.
