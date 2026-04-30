# Implementation Plan

## Constats

- `backend/pyproject.toml` expose deja les racines pytest standard.
- `backend/app/tests/unit/test_backend_test_topology.py` porte deja la garde de topologie, mais elle lisait le registre de la story precedente.
- La story courante demande un registre persiste dans `_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md`.
- Aucun fichier de test backend n'est actuellement hors des racines documentees.

## Changements prevus

- Ajouter le registre de topologie de la story courante avec owners, racines standard et exception exacte.
- Capturer les inventaires avant/apres des fichiers de tests backend.
- Faire pointer la garde existante vers le registre courant.
- Ajouter une verification d'exception exacte et une preuve qu'une exception ne contient pas de fichier `test_*.py` ou `*_test.py`.

## Validation

- `ruff format .`
- `ruff check .`
- `pytest -q app/tests/unit/test_backend_test_topology.py`
- `pytest --collect-only -q --ignore=.tmp-pytest`
- `rg --files backend -g 'test_*.py' -g '*_test.py'`

## No Legacy

Aucun shim, alias, fallback ou seconde garde concurrente ne sera ajoute. La
garde existante reste l'unique proprietaire du controle de topologie backend.
