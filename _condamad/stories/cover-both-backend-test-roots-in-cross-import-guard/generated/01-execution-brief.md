# Execution Brief

## Story key

`cover-both-backend-test-roots-in-cross-import-guard`

## Objective

Durcir `backend/app/tests/unit/test_backend_test_helper_imports.py` pour que la garde AST anti imports croises scanne les deux racines collectables: `backend/app/tests` et `backend/tests`.

## Boundaries

- Modifier uniquement la garde existante et les artefacts de preuve de cette story.
- Ne pas deplacer de helpers de tests.
- Ne pas changer le harnais DB ni la topologie pytest.
- Ne pas ajouter d'allowlist ou de compatibilite.

## Preflight checks

- Lire `AGENTS.md`.
- Lire `_condamad/stories/regression-guardrails.md`.
- Lire la story source, l'audit F-103 et la garde existante.
- Capturer le baseline avant/apres.

## Done conditions

- `BACKEND_ROOT` pointe vers `backend`.
- `TEST_ROOTS` couvre explicitement `app/tests` et `tests`.
- La garde AST continue de bloquer les imports depuis `test_*.py`.
- Les commandes de validation de la story sont executees dans le venv.

## Halt conditions

- Un import croise actif est detecte et ne peut pas etre remplace dans le scope.
- Le venv est indisponible et ne peut pas etre cree/active.
- Une modification hors scope devient necessaire.
