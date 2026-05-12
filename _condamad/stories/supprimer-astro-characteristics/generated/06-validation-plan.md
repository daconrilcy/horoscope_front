# Validation Plan

## Environment assumptions

- PowerShell sur Windows.
- Toute commande Python est executee apres `.\.venv\Scripts\Activate.ps1`.
- Backend Python sous `backend/`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Tests reference data | `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest app/tests/unit/test_reference_data_service.py app/tests/integration/test_reference_data_migrations.py -q` | repo root | yes | all pass |
| Tests aspect orbs non-regression | `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest app/tests/unit/test_aspect_orb_overrides.py app/tests/unit/test_aspects_calculator.py -q` | repo root | yes | all pass |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Removed table/model scan | `rg -n "AstroCharacteristicModel|astro_characteristics" backend/app backend/tests` | repo root | yes | no active hits except intentional guards if any |
| Payload key scan | `rg -n "\"characteristics\"|\\['characteristics'\\]" backend/app backend/tests` | repo root | yes | no active API/test dependency on removed payload |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff format .` | repo root | yes | no formatting errors |
| Lint | `.\\.venv\\Scripts\\Activate.ps1; cd backend; ruff check .` | repo root | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend suite | `.\\.venv\\Scripts\\Activate.ps1; cd backend; pytest -q` | repo root | yes | all pass |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Whitespace/conflicts | `git diff --check` | repo root | yes | no issues |
| Diff summary | `git diff --stat` | repo root | yes | only story files changed |
| Worktree status | `git status --short` | repo root | yes | expected files only |

## Commands that may be skipped only with justification

- Backend full suite or app startup may be skipped only if time/environment blocks execution; record exact reason and compensating evidence.
