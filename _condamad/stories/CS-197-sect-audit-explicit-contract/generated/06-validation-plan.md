# Validation Plan

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Sect calculator contract | `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py` | repo root | yes | pass |
| Dignity scoring and contracts | `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_dignity_contracts.py backend/tests/unit/domain/astrology/test_natal_result_contract.py` | repo root | yes | pass |
| Public projection and persistence | `.\.venv\Scripts\Activate.ps1; pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` | repo root | yes | pass |
| Combined targeted story suite | `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_dignity_contracts.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` | repo root | yes | pass |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| No projection recalculation | `rg -n "SectCalculator" backend/app/services/chart/json_builder.py` | repo root | yes | zero hits |
| No local horizon constants | `rg -n "\b7,\s*8,\s*9,\s*10,\s*11,\s*12\b|\b1,\s*2,\s*3,\s*4,\s*5,\s*6\b" backend/app/domain/astrology/dignities backend/app/services/chart -g "*.py"` | repo root | yes | zero hits |
| No per-planet sect condition contract | `rg -n "PlanetSectCondition|planet_sect_condition" backend/app backend/tests -g "*.py"` | repo root | yes | zero hits |
| No public legacy sect alias | `rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code" backend/app backend/tests -g "*.py"` | repo root | yes | only classified runtime reference hits |
| Dignity domain boundary | `$forbidden = "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|OpenAI|AIEngineAdapter|chat\.completions|prompt"; rg -n $forbidden backend/app/domain/astrology/dignities -g "*.py"` | repo root | yes | zero hits |

## Quality and regression

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `.\.venv\Scripts\Activate.ps1; ruff format .` | repo root | yes | pass |
| Lint | `.\.venv\Scripts\Activate.ps1; ruff check .` | repo root | yes | pass |
| Backend regression suite | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | repo root | yes | pass |
| Diff whitespace | `git diff --check` | repo root | yes | pass |
