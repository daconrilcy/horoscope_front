<!-- Plan de validation CONDAMAD pour CS-194. -->

# Validation Plan

## Environment Assumptions

- PowerShell on Windows.
- All Python commands must run after `.\\.venv\\Scripts\\Activate.ps1`.
- Backend dependencies are managed by `backend/pyproject.toml`.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Dominance engine | `pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py` | repo root | yes | all pass |
| Natal contract | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` | repo root | yes | all pass |
| Public chart JSON and persistence | `pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` | repo root | yes | all pass |
| Runtime reference | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py` | repo root | yes | all pass |
| Migration schema | `pytest --long -q backend/app/tests/integration/test_reference_data_migrations.py` | repo root | yes | all pass |

## DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Domain boundary | `rg -n "Session\|select\\(\|from app\\.infra\|from app\\.services\|from app\\.api\|from app\\.domain\\.prediction\|from app\\.services\\.prediction" backend/app/domain/astrology/dominance -g "*.py"` | repo root | yes | zero hits |
| LLM/narrative boundary | `rg -n "OpenAI\|AIEngineAdapter\|chat\\.completions\|\\bprompt\\b\|narration\|micro_note" backend/app/domain/astrology/dominance -g "*.py"` | repo root | yes | zero hits |
| Local dominance weights | `rg -n "DOMINANCE_FACTORS\|DOMINANCE_WEIGHTS\|CHART_RULER_WEIGHT\|ANGULARITY_WEIGHT\|SIGN_RULERS\|PLANET_RULERS" backend/app backend/tests frontend/src -g "*.py" -g "*.ts" -g "*.tsx"` | repo root | yes | no active local weight map |
| Projection-only serializer | `rg -n "planet_dominance\|PlanetDominance" backend/app/services/chart/json_builder.py backend/app/domain/astrology/natal_calculation.py backend/app/domain/astrology/dominance -g "*.py"` | repo root | yes | integration/projection sites only |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | repo root | yes | no formatting failure |
| Lint | `ruff check .` | repo root | yes | no lint errors |

## Diff Review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff whitespace | `git diff --check` | repo root | yes | no conflict markers or whitespace errors |
| Scope summary | `git diff --stat` | repo root | yes | only story-scoped files changed |
| Worktree status | `git status --short` | repo root | yes | expected story files only |
