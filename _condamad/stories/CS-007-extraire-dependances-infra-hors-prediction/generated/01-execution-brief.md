# Execution brief - CS-007

## Story key

`CS-007-extraire-dependances-infra-hors-prediction`

## Objective

Extraire le chargement de contexte DB et la persistence prediction hors de `backend/app/prediction`, sans changement de comportement public.

## Boundaries

- Migrer les implementations SQLAlchemy/repositories vers `backend/app/services/prediction` ou `backend/app/infra`.
- Migrer tous les consommateurs vers les nouveaux owners canoniques.
- Supprimer les anciens modules `app.prediction.context_loader` et `app.prediction.persistence_service`; ne pas les remplacer par facade, alias ou re-export.
- Ne pas changer le schema DB, les contrats API, ni les invariants LLM.

## Preflight

- Lire `AGENTS.md`, `00-story.md`, le registre `_condamad/stories/regression-guardrails.md`.
- Capturer `git status --short`.
- Persister le scan baseline avant modification dans `infra-dependency-before.md`.

## Done conditions

- `backend/app/prediction` ne contient plus les imports infra interdits vises par la story, sauf hits classifies hors scope.
- Les tests de contexte/persistence/e2e prediction restent passants.
- Une garde AST bloque la reintroduction des imports interdits.
- Les preuves avant/apres, la traceabilite et l'evidence finale sont completees.

## Halt conditions

- Un consommateur externe actif impose de garder un ancien module importable.
- Une validation DB pertinente echoue sans correctif sur.
- Une modification du schema DB ou du contrat public devient necessaire.
