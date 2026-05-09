<!-- Brief d'execution CONDAMAD genere pour piloter la suppression CS-119. -->

# Execution Brief - CS-119

## Objective

Supprimer les composants `frontend/src/components/**` confirmes `test-only`
sans consommateur runtime, leurs CSS dedies devenus orphelins et les tests
focalises qui ne couvraient que ces surfaces.

## Boundaries

- Domaine unique: `frontend/src/components` et tests/guards frontend lies.
- Conserver les composants classes `used` ou `public-library-export`.
- Ne pas modifier `backend/**`, routes frontend, contrats API ou surfaces natal.
- Ne pas ajouter de wrapper, alias, fallback, barrel export ou re-export pour
  les surfaces supprimees.

## Required Preflight

- Lire `AGENTS.md`, la story `00-story.md` et
  `_condamad/stories/regression-guardrails.md`.
- Capturer l'etat initial du worktree.
- Produire l'inventaire avant suppression.
- Verifier les imports runtime, imports de tests, barrels et CSS des cibles.

## Write Rules

- Suppression physique uniquement apres preuve d'absence de consommateur runtime.
- Adapter les guards transverses sans affaiblir leurs invariants hors scope.
- Retirer les exceptions exactes devenues stale des allowlists.
- Garder les preuves dans les artefacts de story.

## Done Conditions

- AC1 a AC8 ont une preuve de code et de validation.
- Les commandes frontend ciblees et `npm run lint` passent.
- Les validations Python de story sont lancees apres activation du venv.
- Le statut de story est synchronise apres review propre.
