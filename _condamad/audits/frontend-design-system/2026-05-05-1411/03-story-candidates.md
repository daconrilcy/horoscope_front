# Story Candidates - frontend-design-system

## SC-001 - Reduire les valeurs visuelles et typographiques hardcodees restantes

- Candidate ID: SC-001
- Source finding: F-002
- Suggested story title: Reduire la dette de valeurs visuelles hardcodees hors premier lot migre
- Suggested archetype: hardcoded-design-value-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-044`, `RG-045`, `RG-046`, token namespace registry, typography roles
- Draft objective: Continue the design-token migration after the first governed batch by reducing repeated color, spacing, radius, shadow, and typography literals in the highest-impact CSS clusters.
- Must include: before/after static counts, explicit migrated file list, no expansion of unclassified token namespaces, and updates only to relevant registries when a new permanent semantic token is introduced.
- Validation hints: `npm run test -- design-system theme-tokens`; targeted `rg` counts for migrated files; `npm run lint`; visual smoke where a large page surface changes.
- Blockers: Product/design decision may be needed when near-equivalent literal values should converge to one semantic token.

## SC-002 - Convertir les styles inline statiques allowlistes vers CSS

- Candidate ID: SC-002
- Source finding: F-003
- Suggested story title: Supprimer un lot de styles inline statiques encore allowlistes
- Suggested archetype: inline-style-debt-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-047`, inline-style allowlist, CSS-only style rule
- Draft objective: Reduce the exact inline-style allowlist by moving static styles into CSS files while keeping dynamic runtime values as documented exceptions.
- Must include: classification of each touched inline style as static or dynamic, CSS extraction for static entries, allowlist reduction, and no new style attributes.
- Validation hints: `npm run test -- inline-style design-system`; scan `rg -n "style=" frontend/src --glob "*.tsx"` with before/after counts; component tests for touched surfaces.
- Blockers: None identified.

## SC-003 - Reduire les fallbacks CSS allowlistes

- Candidate ID: SC-003
- Source finding: F-004
- Suggested story title: Reduire les fallbacks `var(--token, value)` restants
- Suggested archetype: css-fallback-debt-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-048`, CSS fallback allowlist, token namespace registry
- Draft objective: Replace migration-only CSS fallback literals with required canonical tokens or documented imports so fallbacks stop acting as hidden alternate values.
- Must include: before/after fallback count, updated `css-fallback-allowlist.md`, no unclassified fallback, and component-level validation for changed CSS.
- Validation hints: `npm run test -- css-fallback design-system`; targeted `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*,"` on migrated files; `npm run lint`.
- Blockers: Some fallbacks may require a decision about whether isolated component CSS must work without global token imports.

## SC-004 - Stabiliser l'isolation de la suite Vitest frontend

- Candidate ID: SC-004
- Source finding: F-005
- Suggested story title: Stabiliser le test `HelpPage` en execution suite complete
- Suggested archetype: frontend-test-isolation-hardening
- Primary domain: frontend-tests
- Required contracts: reliable CI test signal, `RG-050`
- Draft objective: Make `npm run test` deterministic enough that design-system guard results are not obscured by full-suite-only failures.
- Must include: reproduction attempt for `HelpPage.test.tsx` in full-suite mode, audit of shared mocks/cache/timers/router state, and a focused fix with a repeatable validation command.
- Validation hints: `npm run test -- HelpPage`; `npm run test`; optionally repeat the full suite twice if the first investigation confirms flakiness.
- Blockers: None identified.
