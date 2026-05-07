<!-- Rapport d'audit CONDAMAD du domaine frontend design-system apres refactors CS-080 a CS-086. -->

# Audit Report - frontend-design-system

## Scope

- Domain key: `frontend-design-system`
- Audit date: `2026-05-07-2236`
- Archetype: `test-guard-coverage-audit` plus `legacy-surface-audit` and `dependency-direction-audit` for CSS ownership.
- Mode: read-only for application code; audit artifacts written under `_condamad/audits/**`.
- Audited surface: CSS design tokens, theme layers, page-scoped token owners, CSS fallback policy, inline style policy, legacy style policy, visual smoke guards.

## Context

The previous frontend design-system audits from `2026-05-04-2238` through `2026-05-07-1730` produced successive refactor stories. The current implementation includes completed guardrails for `CS-080` through `CS-086`, including runtime compatibility closure, chat, app, settings, landing, admin, and residual CSS token clusters.

Relevant regression guardrails consulted: `RG-044` through `RG-060`.

## Executive Finding Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 1 |
| Medium | 2 |
| Low | 1 |
| Info | 2 |

## Main Conclusion

The recent refactors materially improved the frontend design-system posture: targeted Vitest guards, lint, and production build pass. The former exhaustive 50-file residual list is no longer the current modification list.

Remaining design-system work is now concentrated in six implementation files plus shared governance/test files. The exact application files to modify are:

- `frontend/src/App.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/components/prediction/DailyAdviceCard.css`
- `frontend/src/styles/backgrounds.css`
- `frontend/src/styles/glass.css`

The governance/test files that must be inspected or updated when implementing the candidates are:

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

## Findings

See `02-finding-register.md` for full details.

Top risks:

1. `F-002`: `App.css` still contains broad local visual/typography ownership outside the partial `CS-082` guard.
2. `F-003`: Help subscriptions remain a large page sub-surface with local visual literals outside the earlier HelpPage guard window.
3. `F-004`: shared glass/background and daily premium CSS still carry repeated literal decisions without a focused anti-return guard.

## Validation

Executed successfully:

- `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`
- `npm run lint`
- `npm run build`

Build limitation:

- Vite still warns that `assets/index-CRyuM-rd.js` is larger than 500 kB after minification. This is tracked as frontend performance context, not a design-system blocker.

