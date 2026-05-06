<!-- Propositions de stories issues de l'audit frontend design-system. -->

# Story Candidates - frontend-design-system

## SC-001

- Candidate ID: SC-001
- Source finding: F-002
- Suggested story title: Migrer un prochain cluster coherent de valeurs visuelles hardcodees frontend
- Suggested archetype: design-system-token-convergence
- Primary domain: frontend-design-system
- Required contracts:
  - `_condamad/stories/regression-guardrails.md` (`RG-044`, `RG-045`, `RG-046`, `RG-050`, plus `RG-055` or `RG-056` if the selected cluster touches prediction premium or shared UI)
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/typography-roles.md`
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
- Draft objective: reduce duplicate visual and typography ownership by migrating one bounded file cluster from local literals to existing tokens, typography roles, or documented semantic extensions.
- Must include:
  - Select one coherent cluster from the 98-file inventory in `00-audit-report.md`.
  - Capture before/after literal inventory for the selected cluster.
  - Reuse existing tokens and roles before creating new semantic variables.
  - If a new semantic namespace is necessary, classify it in `token-namespace-registry.md`.
  - Update or add exact guard coverage for literals removed by the story.
  - Keep CSS in CSS files; do not introduce static inline styles.
- Validation hints:
  - `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`
  - Add cluster-specific Vitest or static guard assertions for migrated literals.
  - `npm run lint`
  - `npm run build`
- Blockers:
  - The user or implementer must choose the next cluster. Recommended candidates are admin pages, chat surfaces, or non-migrated prediction support components. Avoid mixing unrelated page, layout and shared component surfaces in one story.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - token namespace ownership applies to any CSS token migration.
  - `RG-045` - hardcoded visual values are the source finding.
  - `RG-046` - typography roles apply to font-size, font-weight, line-height and letter-spacing migrations.
  - `RG-047` - static inline styles must not be introduced while moving values.
  - `RG-048` - CSS fallback literals must not be introduced as a substitute for tokens.
  - `RG-050` - anti-drift guard suite must remain executable.
  - `RG-055` - applies if the chosen cluster touches prediction premium files.
  - `RG-056` - applies if the chosen cluster touches shared UI primitives.
- Non-applicable invariants:
  - `RG-051` - only applies if the selected story touches page-scoped token consumption.
  - `RG-052` - no active migration-only namespace remains, but keep the guard command if namespace registry changes.
  - `RG-053`, `RG-057` - runtime compatibility surfaces are not part of this candidate unless the chosen cluster touches those modules.
  - `RG-054` - admin legacy redirects are closed and not part of visual literal migration.
- Required regression evidence:
  - Focused static scan of selected files before and after migration.
  - `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`.
  - `npm run lint`.
- Allowed differences:
  - Only intended visual-token substitutions in selected files; no route, runtime payload or compatibility behavior changes.
