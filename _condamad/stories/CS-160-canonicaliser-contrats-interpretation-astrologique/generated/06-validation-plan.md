# Validation Plan CS-160

## Environment assumptions

- OS: Windows / PowerShell.
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Working directory for backend validations: `backend/`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Force maison typed contract | `pytest -q tests/unit/domain/astrology/test_house_strength.py` | `backend/` | yes | all tests pass |
| Runtime builder integration | `pytest -q tests/unit/domain/astrology/test_house_runtime_builder.py` | `backend/` | yes | all tests pass |
| JSON public compatibility | `pytest -q app/tests/unit/test_chart_json_builder.py` | `backend/` | yes | all tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| RG-095 astrology to prediction boundary | `pytest -q app/tests/unit/test_astrology_prediction_boundary.py` | `backend/` | yes | all tests pass |
| RG-096 no raw score thresholds in domain prediction | `rg -n "strength\\.score\\s*[<>]=?" app/domain/prediction -g "*.py"` | `backend/` | yes | no hit |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Raw reason append scan | `rg -n "reasons\\.append\\(\"" app/domain/astrology -g "*.py"` | `backend/` | yes | no hit |
| Reason assignment and constructor scan | `rg -n "reasons\\s*=\\s*\\[|HouseStrengthRuntimeData\\(" app/domain/astrology -g "*.py"` | `backend/` | yes | no unclassified active ad hoc reason hit |
| Astrology does not import prediction | `rg -n "app\\.domain\\.prediction|app\\.services\\.prediction|prediction_categories|house_category_weights|visibility_weight|base_priority|routing_role|DomainRouter|PublicAstroFoundationProjector" app/domain/astrology -g "*.py"` | `backend/` | yes | no hit |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Lint | `ruff check .` | `backend/` | yes | no lint errors |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-related files changed |
| Worktree status | `git status --short` | repo root | yes | expected dirty files only |
