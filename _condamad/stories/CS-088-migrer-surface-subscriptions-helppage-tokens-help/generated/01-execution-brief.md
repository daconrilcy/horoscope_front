# Execution Brief

## Story

- Key: `CS-088-migrer-surface-subscriptions-helppage-tokens-help`
- Source: `_condamad/stories/CS-088-migrer-surface-subscriptions-helppage-tokens-help/00-story.md`
- Objective: migrer la sous-surface subscriptions de `frontend/src/pages/HelpPage.css` vers des tokens globaux, roles typographiques ou owners `--help-*`.

## Boundaries

- Modifier uniquement la surface CSS Help subscriptions, les registres design-system necessaires, les guards et les artefacts de preuve de cette story.
- Ne pas modifier React, routes, API, stores, backend, dependances ou scripts.
- Ne pas introduire de fallback CSS, namespace tiers page-scoped, shim, alias ou compatibilite.

## Preflight

- Lire `AGENTS.md`, la story, le registre `_condamad/stories/regression-guardrails.md`, les registres tokens/typographie et les tests design-system.
- Capturer `git status --short`.
- Capturer `hardcoded-values-before.md` avant modification de `HelpPage.css`.

## Completion

- `HelpPage.css` route les valeurs subscriptions migrables via `--help-*`, tokens globaux ou roles typographiques.
- `design-system-guards.test.ts` bloque la reintroduction des literals subscriptions migres.
- Les artefacts before/after et `generated/10-final-evidence.md` sont complets.
- Les validations requises sont executees ou documentees avec risque.
