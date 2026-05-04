# Execution Brief - CS-014

## Primary objective

Supprimer physiquement le namespace runtime `backend/app/prediction` et migrer les consommateurs internes vers un owner canonique sans shim, alias, fallback, wrapper ni re-export.

## Boundaries

- In scope: inventaires avant/apres, migration des imports, suppression du dossier legacy, garde d'extinction, evidence CONDAMAD.
- Out of scope: changement de contrat HTTP, modification frontend, nouvelle dependance, refonte metier du moteur.
- Owner retenu dans cette implementation: `backend/app/domain/prediction`, car aucun owner plus fin n'existe encore dans le depot au moment de CS-014.

## Preflight

- `git status --short` lu avant modification.
- `AGENTS.md` racine lu.
- `_condamad/stories/regression-guardrails.md` lu; RG-026 a RG-038 applicables.

## Done conditions

- `backend/app/prediction` absent.
- `app.prediction` non importable.
- Zero import actif `from app.prediction` ou `import app.prediction` sous `backend/app` et `backend/tests`.
- Tests ciblés, lint et format passent, ou limitation documentee.
- `generated/10-final-evidence.md` et `story-status.md` synchronises.
