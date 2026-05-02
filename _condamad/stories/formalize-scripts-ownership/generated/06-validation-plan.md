# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- Backend commands run from `backend/` after `.venv` activation.
- Python commands must use `.\\.venv\\Scripts\\Activate.ps1` first.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Inventory current scripts | `rg --files scripts` | repo root | yes | lists the same paths as both persisted snapshots |
| Stripe blocked decision scan | `rg -n "stripe-listen" scripts/ownership-index.md` | repo root | yes | `.sh` row has `needs-user-decision` and blocked decision |

## Unit tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Script ownership guard | `pytest -q app/tests/unit/test_scripts_ownership.py` | `backend/` after venv activation | yes | all tests pass |
| RG-015 related ownership registry | `pytest -q app/tests/unit/test_backend_quality_test_ownership.py` | `backend/` after venv activation | yes | all tests pass |

## Integration tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Script integration coverage | `pytest -q app/tests/integration/test_pipeline_scripts.py app/tests/integration/test_secrets_scan_script.py app/tests/integration/test_security_verification_script.py` | `backend/` after venv activation | yes | all tests pass or environment skip is explicit |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Capsule story validation | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/formalize-scripts-ownership/00-story.md` | repo root after venv activation | yes | validation passes |
| Capsule story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/formalize-scripts-ownership/00-story.md` | repo root after venv activation | yes | lint passes |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Single registry scan | `rg -n "ownership-index.md" . -g "!node_modules" -g "!backend/.tmp-pytest" -g "!artifacts" -g "!.codex-artifacts"` | repo root | yes | hits classify to story, tests, or docs only |
| Legacy wording scan | `rg -n "legacy|compat|shim|fallback|deprecated|alias" scripts backend/app/tests/unit/test_scripts_ownership.py` | repo root | yes | no active compatibility path introduced |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff format check | `ruff format --check app/tests/unit/test_scripts_ownership.py` | `backend/` after venv activation | yes | file is formatted |
| Ruff lint | `ruff check app/tests/unit/test_scripts_ownership.py` | `backend/` after venv activation | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Broader backend tests | `pytest -q` | `backend/` after venv activation | conditional | run if targeted/integration checks are green and time allows |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-related files changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no whitespace or conflict marker issues |
| Final status | `git status --short` | repo root | yes | expected files only |
