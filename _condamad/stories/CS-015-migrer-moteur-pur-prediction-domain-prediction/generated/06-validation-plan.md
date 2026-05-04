# Validation Plan

## Environment assumptions

- OS: Windows / PowerShell.
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Working directory for Python checks: `backend`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Moteur prediction | `pytest -q app/tests/unit/test_engine_orchestrator.py app/tests/unit/test_transit_signal_v3.py` | `backend` | yes | all tests pass |
| Astro foundation non-regression | `pytest -q tests/unit/prediction/test_public_astro_foundation.py` | `backend` | yes | all tests pass |
| Architecture prediction guardrails | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` | `backend` | yes | all tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Namespace domaine present | `rg --files app/domain/prediction` | `backend` | yes | files are listed |
| Services sans import legacy | `rg -n "from app\.prediction" app/services/prediction -g "*.py"` | `backend` | yes | zero hit |
| Domaine sans dependances interdites | `rg -n "fastapi\|sqlalchemy\|Session\|settings\|AIEngineAdapter\|from app\.infra\|from app\.api\|from app\.services" app/domain/prediction -g "*.py"` | `backend` | yes | zero hit |
| Legacy imports actifs absents | `rg -n "from app\.prediction\|import app\.prediction" app tests -g "*.py"` | `backend` | yes | zero active hit; test guard string hits only if broader scan is used |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Surfaces compat sous prediction cible | `rg -n "legacy\|compat\|shim\|fallback\|deprecated\|alias" app/domain/prediction app/services/prediction app/tests/unit/test_daily_prediction_guardrails.py -g "*.py"` | `backend` | yes | hits classified |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff cible | `ruff check app/domain/prediction app/services/prediction app/tests/unit/test_daily_prediction_guardrails.py` | `backend` | yes | no lint errors |

## Regression checks

Full `pytest -q` is desirable but not mandatory for this story if targeted engine, guardrail, and related public projection checks pass. If skipped, record the risk and compensating evidence.

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff stat | `git diff --stat` | repo root | yes | only expected files changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no errors |
| Final status | `git status --short` | repo root | yes | expected files only |

## Commands that may be skipped only with justification

- Full backend suite: `pytest -q`, if targeted scope is sufficient or runtime cost is high.
- Local app startup, because this story changes no runtime launch path or frontend surface.
