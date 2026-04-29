# Execution Brief

## Story key

`collect-retained-backend-tests`

## Primary objective

Faire en sorte que la commande standard `pytest` lancee depuis `backend/` collecte tous les tests backend conserves, avec une garde deterministe qui compare l'inventaire statique des fichiers de test a la collecte pytest effective.

## Boundaries

- Modifier uniquement la configuration pytest backend, la garde de collecte et les preuves de cette story.
- Ne pas reorganiser massivement la topologie des tests.
- Ne pas modifier les fixtures DB ni les assertions metier des tests.
- Ne pas ajouter de dependance.
- Ne pas creer de dossier racine sous `backend/`.

## Required preflight

- Lire `AGENTS.md`.
- Lire `_condamad/stories/regression-guardrails.md`.
- Capturer `git status --short`.
- Capturer les inventaires avant modification.
- Executer toute commande Python apres activation de `.\\.venv\\Scripts\\Activate.ps1`.

## Write rules

- Conserver `backend/pyproject.toml` comme source unique de configuration pytest.
- Supprimer de `testpaths` toute racine inexistante.
- Ajouter une garde pytest sous une racine deja collectee.
- Persister les preuves avant/apres dans le dossier de story.

## Done conditions

- `pytest --collect-only -q --ignore=.tmp-pytest` collecte les fichiers `test_*.py` et `*_test.py` retenus.
- Aucune racine `testpaths` inexistante ne reste configuree.
- La garde de collecte echoue si un fichier de test backend est hors collecte sans exception explicite.
- Lint, test cible et regression pytest sont executes ou documentes.

## Halt conditions

- Le venv est absent et ne peut pas etre cree/installe.
- La collecte pytest echoue pour une raison non liee a la story sans correctif sur.
- Une exception opt-in necessite une decision CI externe non documentee.
