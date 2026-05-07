# Execution Brief

## Story

- Story key: `CS-084-migrer-cluster-settings-valeurs-visuelles-typographiques`
- Source: `_condamad/stories/CS-084-migrer-cluster-settings-valeurs-visuelles-typographiques/00-story.md`
- Objective: migrer exclusivement `frontend/src/pages/settings/Settings.css` vers les tokens, roles typographiques et variables semantiques documentees du design-system.

## Boundaries

- Modifier uniquement le cluster Settings et les registres/tests frontend necessaires a la garde anti-retour.
- Ne pas modifier la logique React, les routes, les stores, les clients API, les contrats backend ou `frontend/src/App.css`.
- Conserver `--settings-*` comme namespace page-scoped documente et `--usage-progress` comme propriete runtime dynamique allowlistee.

## Non-goals

- Aucun nouveau package, script ou framework.
- Aucun namespace `legacy`, `compatibility`, `migration-only`, alias, shim ou fallback non classe.
- Aucune AC ne peut etre finalisee en `PASS_WITH_LIMITATIONS`.

## Required Preflight

- `git status --short`
- lecture de `AGENTS.md`
- lecture de `_condamad/stories/regression-guardrails.md`
- lecture de `Settings.css`, registres design-system et tests de garde existants

## Write Rules

- Utiliser le plus petit delta coherent.
- Reutiliser les tokens globaux, roles typographiques et le namespace `--settings-*` existant.
- Ajouter ou ajuster la garde anti-retour exacte des literals Settings migres.
- Documenter les decisions before/after dans les artefacts persistants de la story.

## Done Conditions

- AC1 a AC8 en `PASS`.
- Validation frontend, lint et build reussis.
- Validation story reussie apres activation du venv.
- Evidence finale complete, statut story synchronise.

## Halt Conditions

- Besoin d'une compatibilite, alias, fallback non classe ou limitation.
- Validation obligatoire impossible sans solution locale.
- Changement React ou hors cluster necessaire pour satisfaire une AC.
