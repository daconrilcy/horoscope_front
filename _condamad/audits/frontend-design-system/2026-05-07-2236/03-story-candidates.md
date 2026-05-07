<!-- Candidats stories issus de l'audit frontend design-system apres refactors CS-080 a CS-086. -->

# Story Candidates - frontend-design-system

## Exhaustive Files To Modify

The exhaustive implementation files to modify for the remaining design-system debt found by this audit are:

- `frontend/src/App.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/components/prediction/DailyAdviceCard.css`
- `frontend/src/styles/backgrounds.css`
- `frontend/src/styles/glass.css`

The exhaustive governance/test files to inspect or update while implementing these candidates are:

- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/design-system-allowlist.ts`

## SC-001

- Candidate ID: SC-001
- Source finding: F-002
- Suggested story title: Converger les valeurs visuelles et typographiques restantes de `App.css`
- Suggested archetype: design-system-token-convergence
- Primary domain: frontend-design-system
- Required contracts:
  - `_condamad/stories/regression-guardrails.md`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/typography-roles.md`
  - `frontend/src/styles/css-fallback-allowlist.md`
  - `frontend/src/styles/legacy-style-surface-registry.md`
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
- Draft objective: close the remaining local visual and typography ownership in `App.css` by moving repeated values to documented `--app-*`, global, or typography tokens and adding exact anti-return guards.
- Must include:
  - migrate only `frontend/src/App.css` as the implementation surface;
  - classify each remaining App literal as global token, `--app-*` semantic token, typography role, animation/runtime value, or intentional one-off;
  - extend the existing `CS-082` guard so the broader App file is covered, not just selected App variables;
  - avoid inline styles and CSS fallbacks unless allowlisted;
  - preserve `RG-044` through `RG-060`.
- Validation hints:
  - `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`
  - `npm run lint`
  - `npm run build`
  - before/after scan for `frontend/src/App.css`.
- Blockers: decide whether very large App sections should remain app-scoped under `--app-*` or be split into more specific component/page CSS owners before migration.

## SC-002

- Candidate ID: SC-002
- Source finding: F-003
- Suggested story title: Migrer la surface subscriptions de `HelpPage.css` vers les tokens Help
- Suggested archetype: design-system-token-convergence
- Primary domain: frontend-design-system
- Required contracts:
  - `_condamad/stories/regression-guardrails.md`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/typography-roles.md`
  - `frontend/src/styles/css-fallback-allowlist.md`
  - `frontend/src/styles/legacy-style-surface-registry.md`
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/visual-smoke.test.tsx`
- Draft objective: close the Help subscriptions sub-surface that remains outside the earlier HelpPage guard window.
- Must include:
  - modify `frontend/src/pages/HelpPage.css`;
  - preserve the existing `--help-*` page-scoped owner model;
  - move repeated visual/type literals in the subscriptions section to `--help-*`, global, or typography roles;
  - extend the existing Help guard to cover the subscriptions section or add a specific `CS-087` guard block;
  - update visual smoke coverage if the rendered route coverage changes.
- Validation hints:
  - `npm run test -- design-system css-fallback inline-style legacy-style visual-smoke HelpPage`
  - `npm run lint`
  - before/after scan for the Help subscriptions section.
- Blockers: none, unless product wants the subscriptions page extracted into a dedicated CSS owner before token migration.

## SC-003

- Candidate ID: SC-003
- Source finding: F-004
- Suggested story title: Converger les surfaces premium partagees background, glass et daily advice
- Suggested archetype: design-system-token-convergence
- Primary domain: frontend-design-system
- Required contracts:
  - `_condamad/stories/regression-guardrails.md`
  - `frontend/src/styles/design-tokens.css`
  - `frontend/src/styles/premium-theme.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/typography-roles.md`
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/theme-tokens.test.ts`
  - `frontend/src/tests/visual-smoke.test.tsx`
- Draft objective: assign a single token ownership model to shared premium background/glass values and daily premium card overlays.
- Must include:
  - modify exactly these implementation files: `frontend/src/styles/backgrounds.css`, `frontend/src/styles/glass.css`, `frontend/src/pages/DailyHoroscopePage.css`, `frontend/src/components/prediction/DailyAdviceCard.css`;
  - decide whether values belong in global tokens, `premium-theme.css`, or local page/component semantic tokens;
  - remove local repeated rgba/gradient/shadow/radius literals where a semantic token is appropriate;
  - add exact guards to prevent reintroduction in these four files;
  - keep `DailyHoroscopePage.css` aligned with the existing `--glass-*` registry entries.
- Validation hints:
  - `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke DailyHoroscopePage`
  - `npm run lint`
  - `npm run build`
  - before/after scan for the four exact files.
- Blockers: choose the canonical owner for shared premium background/glass values: global `design-tokens.css`, product-level `premium-theme.css`, or page-scoped daily tokens.
