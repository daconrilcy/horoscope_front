<!-- Brief d'execution CONDAMAD pour cadrer la convergence des containers API components. -->

# Execution Brief - CS-120

## Objective

Converger toutes les surfaces exactes de `frontend/src/components/**` qui
restent owners d'orchestration API/feature vers leurs owners canoniques
feature, page, layout ou app. Supprimer les anciens chemins sans wrapper,
alias, fallback, re-export ou exception large.

## Boundaries

- Scope applicatif: `frontend/**`.
- Scope evidence: dossier de story CS-120 et registre `story-status.md`.
- Aucun changement backend, contrat API, payload, endpoint ou dependance.
- Aucun changement design system hors validation des guards existants.

## Required Preflight

- Lire `AGENTS.md`, la story, le registre de guardrails et les audits source.
- Capturer l'inventaire before des hits E-010.
- Inspecter les fichiers cibles et leurs consommateurs avant toute suppression.
- Utiliser le contrat `condamad-frontend-dev` pour le slice frontend.

## Write Rules

- Repointer les consommateurs first-party vers les owners canoniques.
- Supprimer les anciens fichiers component owners quand ils ne sont plus
  consommes.
- Supprimer les entrees exactes stale de `COMPONENT_API_IMPORT_EXCEPTIONS`.
- Ne pas creer de namespace fourre-tout ni de re-export de compatibilite.

## Completion Definition

- Les sept batches ont une decision finale exacte.
- Les guards component architecture/usage passent.
- Les scans old-path et stale allowlist retournent zero hit.
- Les artefacts before, after, migration map et final evidence existent.
- Le statut de story est synchronise apres revue.

## Halt Conditions

- Import externe hors `frontend/src/**` d'un ancien chemin component.
- Absence d'owner canonique precis pour un batch.
- Besoin de conserver un chemin legacy sans decision utilisateur.
- Validation deterministe impossible sans blocker documente.
