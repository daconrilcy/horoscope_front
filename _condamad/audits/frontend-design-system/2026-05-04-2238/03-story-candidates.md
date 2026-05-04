# Story Candidates - frontend-design-system

## SC-001 - Canonicaliser la propriete des tokens frontend

- Source finding: F-001
- Suggested story title: Canonicaliser la source de verite des tokens de design frontend
- Suggested archetype: design-token-ownership-convergence
- Primary domain: frontend-design-system
- Required contracts: single-source token contract, compatibility alias registry, regression guardrails consultation
- Draft objective: Establish `frontend/src/styles/design-tokens.css` as the canonical token source and classify every other token layer as semantic extension, compatibility alias, or migration debt.
- Must include: token namespace map, allowed compatibility aliases, import order decision, undefined token scan, and explicit migration status for `theme.css`, `premium-theme.css`, `LandingLayout.css`, `Settings.css`, and `DailyHoroscopePage.css`.
- Validation hints: Static test that verifies canonical tokens exist, compatibility aliases point to canonical tokens, and no new unclassified token namespace appears.
- Blockers: Product/design decision needed for whether `premium-*` remains a first-class semantic layer or is folded into canonical tokens.

## SC-002 - Centraliser les valeurs visuelles hardcodees repetees

- Source finding: F-002
- Suggested story title: Remplacer les couleurs, surfaces, espacements et rayons repetes par des tokens semantiques
- Suggested archetype: hardcoded-design-value-convergence
- Primary domain: frontend-design-system
- Required contracts: design token scale, DRY style policy, No Legacy migration allowlist
- Draft objective: Convert repeated hardcoded design values into named semantic tokens and migrate the highest-repeat surfaces first.
- Must include: repeated value inventory, token candidates for glass surfaces and borders, status colors, focus rings, shadows, spacing, radius, and a first migration batch covering large or shared CSS.
- Validation hints: Before/after static count for hardcoded colors and numeric spacing in migrated files; visual smoke test for migrated pages.
- Blockers: User/design approval needed for approximate values that are close but not identical, especially white glass alpha variants.

## SC-003 - Formaliser la hierarchie typographique

- Source finding: F-003
- Suggested story title: Creer une echelle typographique semantique pour les pages et composants
- Suggested archetype: typography-scale-convergence
- Primary domain: frontend-design-system
- Required contracts: typography token contract, component text-role policy
- Draft objective: Replace local font-size, font-weight, line-height, and letter-spacing decisions with semantic text roles.
- Must include: role list for page title, section title, card title, body, muted body, metadata, label, eyebrow, CTA, and numeric/mono text; migration of repeated weights and common font sizes.
- Validation hints: Static scan for typography literals in migrated files and component tests proving expected classes are applied for shared UI components.
- Blockers: Design decision needed for px-to-rem normalization and whether marketing landing typography keeps a separate role scale.

## SC-004 - Encadrer les styles inline

- Source finding: F-004
- Suggested story title: Supprimer les styles inline statiques et definir une allowlist dynamique
- Suggested archetype: inline-style-policy-guard
- Primary domain: frontend-design-system
- Required contracts: no-inline-static-style policy, CSS-only project rule
- Draft objective: Move static inline styles to CSS and keep only dynamic values that cannot be represented cleanly without CSS variables.
- Must include: allowlist for dynamic width/progress/position/custom-property cases, migration of static examples, and a failing guard for new static inline declarations.
- Validation hints: Static TSX scan with an allowlist file and focused tests for dynamic style cases such as progress widths.
- Blockers: None identified.

## SC-005 - Durcir les fallbacks de variables CSS

- Source finding: F-005
- Suggested story title: Classer et reduire les fallbacks `var(--token, value)` dans le frontend
- Suggested archetype: token-fallback-hardening
- Primary domain: frontend-design-system
- Required contracts: token fallback policy, compatibility alias registry
- Draft objective: Prevent CSS fallbacks from acting as hidden alternate tokens.
- Must include: inventory of fallback usages, removal of fallbacks for required canonical tokens, exact allowlist for external or transitional tokens, and guard against new unclassified fallbacks.
- Validation hints: Static CSS scan that allows only documented fallback tokens.
- Blockers: Requires SC-001 token classification for final allowlist.

## SC-006 - Classer les surfaces CSS legacy

- Source finding: F-006
- Suggested story title: Inventorier et converger les surfaces CSS legacy et les alias de compatibilite
- Suggested archetype: legacy-style-surface-classification
- Primary domain: frontend-design-system
- Required contracts: No Legacy, DRY, selector ownership registry
- Draft objective: Make active legacy selectors and compatibility aliases explicit, then remove or rename them in controlled batches.
- Must include: selector inventory for `*-legacy`, compatibility aliases in `theme.css`, local aliases in feature/page CSS, canonical replacements, and removal blockers.
- Validation hints: Negative scan for new legacy selectors and exact allowlist for remaining migration-only selectors.
- Blockers: Some selectors may still be coupled to older components and need per-component migration decisions.

## SC-007 - Ajouter les guards anti-drift du design system

- Source finding: F-007
- Suggested story title: Ajouter des tests statiques anti-regression pour la consommation des tokens
- Suggested archetype: design-system-regression-guard
- Primary domain: frontend-design-system
- Required contracts: token consumption guard, inline style guard, hardcoded value allowlist
- Draft objective: Make design-system drift detectable in CI after the first convergence pass.
- Must include: tests or scripts for hardcoded colors, spacing, radius, typography, CSS var fallbacks, inline styles, and new token namespace detection.
- Validation hints: `npm run test -- theme-tokens` plus new static tests; a snapshot of allowed exceptions.
- Blockers: Should follow SC-001 through SC-005 so guards start with a realistic allowlist.
