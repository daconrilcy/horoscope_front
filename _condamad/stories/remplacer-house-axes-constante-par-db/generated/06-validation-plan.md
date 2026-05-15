# Validation Plan

## Environment assumptions

- Backend Python, commandes apres activation du venv.
- Pytest et Ruff disponibles via `backend/pyproject.toml`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Tests builder runtime | `pytest tests/unit/domain/astrology/test_house_runtime_builder.py -q` | `backend/` | yes | all pass |
| Tests repository reference | `pytest app/tests/unit/test_prediction_reference_repository.py -q` | `backend/` | yes | all pass |

## Unit tests

Les tests ajoutes ou adaptes doivent couvrir le mapping DB, le builder et l'erreur d'axes incomplets.

## Integration tests

Non requis; les migrations des tables existent deja et ne sont pas modifiees.

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Frontiere astrology | `rg -n "app\\.domain\\.prediction|app\\.services\\.prediction" app/domain/astrology -g "*.py"` | `backend/` | yes | zero hit |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ancienne constante | `rg -n "resolve_house_axis|HOUSE_AXES|house_axes" app tests ../docs` | `backend/` | yes | aucun hit actif hors preuves historiques classees |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff fichiers touches | `ruff check app/domain/astrology/builders/house_runtime_builder.py app/domain/astrology/natal_calculation.py app/infra/db/repositories/reference_repository.py app/infra/db/repositories/prediction_schemas.py tests/unit/domain/astrology/test_house_runtime_builder.py app/tests/unit/test_prediction_reference_repository.py` | `backend/` | yes | no lint errors |

## Regression checks

Pas de suite globale par instruction utilisateur.

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Whitespace/conflicts | `git diff --check` | repo root | yes | no issues |
| Diff summary | `git diff --stat` | repo root | yes | only story files changed |
| Worktree status | `git status --short` | repo root | yes | expected files only |

## Commands that may be skipped only with justification

- `pytest -q`: explicitement exclu par l'utilisateur.
- Tests frontend: hors scope.

