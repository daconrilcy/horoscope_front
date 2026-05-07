# Execution Brief - CS-086

## Objective

Migrer uniquement le cluster CSS admin vers les tokens design-system, roles typographiques et variables semantiques admin documentees, sans modifier le comportement React, les routes, les donnees affichees, les clients API ou les contrats backend.

## Boundaries

- Scope CSS: `frontend/src/layouts/AdminLayout.css` et `frontend/src/pages/admin/*.css`.
- Scope gouvernance: registres design-system et guards frontend strictement necessaires.
- Evidence scope: artefacts before/after, traceability, validation et review de cette story.
- Non-goal: ne pas migrer les autres fichiers de l'audit F-002.

## Required Preflight

- Lire `AGENTS.md`, `00-story.md` et `_condamad/stories/regression-guardrails.md`.
- Preserver les changements preexistants: `_condamad/stories/story-status.md`, `_condamad/audits/frontend-design-system/2026-05-07-1730/`, capsule `CS-086`.
- Capturer le baseline admin avant migration dans `hardcoded-values-before.md`.
- Utiliser `condamad-frontend-dev` pour toute modification `frontend/**`.

## Write Rules

- Aucun style inline.
- Aucun namespace page-scoped non admin dans le cluster admin.
- Aucun fallback CSS literal `var(--token, value)` non allowliste.
- Aucun namespace `legacy`, `compatibility`, `migration-only`, alias, shim ou re-export.
- Toute variable admin durable doit etre documentee dans `token-namespace-registry.md`.

## Done Conditions

- AC1 a AC8 sont `PASS`, sans `PASS with limitation`.
- `hardcoded-values-before.md` et `hardcoded-values-after.md` existent et classent les decisions.
- Les guards frontend et scans cibles de la story passent.
- `generated/10-final-evidence.md` et `generated/11-code-review.md` sont complets.
