# Validation Plan

## Environment assumptions

- Python commands run after `.\.venv\Scripts\Activate.ps1`.
- Backend commands run from `backend/` unless noted.
- No frontend validation is required; story does not touch `frontend/**`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Runtime contracts and guards | `pytest -q tests/unit/domain/astrology/test_runtime_ref.py tests/unit/domain/astrology/test_natal_result_contract.py app/tests/unit/test_astrology_runtime_reference_repository.py app/tests/unit/test_astrology_runtime_reference_guard.py tests/unit/domain/astrology/test_aspect_strength.py tests/unit/domain/astrology/test_aspect_runtime_builder.py app/tests/unit/test_natal_calculation_service.py` | `backend` | yes | all pass |
| Domain astrology regression subset | `pytest -q tests/unit/domain/astrology app/tests/unit/test_natal_calculation_service.py app/tests/unit/test_reference_data_service.py app/tests/unit/test_scope_separation_imports.py app/tests/unit/test_astrology_runtime_reference_repository.py app/tests/unit/test_astrology_runtime_reference_guard.py` | `backend` | yes | 100 passed |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Legacy reference dict scan | `rg -n "ReferenceDataService\.get_active_reference_data|reference_data: dict" backend/app/domain/astrology backend/app/services/natal` | repo root | yes | zero hits |
| Forbidden DB-backed constants scan | `rg -n "PLANET_KEYWORDS|SIGN_RULERS|DEFAULT_ORB|ASPECT_WEIGHTS|HOUSE_MEANINGS" backend/app/domain/astrology backend/app/services/natal` | repo root | yes | zero hits |
| Forbidden sentinels/threshold names scan | `rg -n "UNKNOWN_SIGN|EXACT_ORB_DEG|TIGHT_RATIO|MODERATE_RATIO" backend/app/domain/astrology backend/app/services/natal` | repo root | yes | zero hits |
| Engine fallback scan | `rg -n "SwissEph.*simplified|simplified.*SwissEph|calculation_engine.*simplified" backend/app/domain/astrology backend/app/services/natal` | repo root | yes | zero hits |
| Astrology domain separation scan | `rg -n "domain\.prediction|app\.domain\.prediction|app\.services\.prediction|AIEngineAdapter|OpenAI|chat\.completions|llm" backend/app/domain/astrology` | repo root | yes | zero hits |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend` | yes | no remaining formatting changes |
| Lint | `ruff check .` | `backend` | yes | no errors |
| Backend startup smoke | `python -m uvicorn app.main:app --host 127.0.0.1 --port 8765` | `backend` | yes | process starts and is stopped after smoke window |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Full backend pytest | `pytest -q` | `backend` | yes | completed but failed; closure blocked until broader failures are triaged |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Whitespace/conflict check | `git diff --check` | repo root | yes | no errors |
| Diff summary | `git diff --stat` | repo root | yes | only story files changed |
| Worktree status | `git status --short` | repo root | yes | expected story files only |
