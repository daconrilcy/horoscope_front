<!-- Plan de validation genere pour CS-217. -->

# Validation Plan

## Environment Assumptions

- Repository root: `c:\dev\horoscope_front`
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Builder tests | `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py` | repo root | yes | pass |
| Natal integration tests | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py` | repo root | yes | pass |
| Architecture guard | `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | repo root | yes | pass |
| Existing internal-field guard | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py` | repo root | yes | pass |
| Existing astral point guard | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contains_configured_points.py` | repo root | yes | pass |
| Existing natal contract guard | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` | repo root | yes | pass |

## DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Forbidden dependencies in new modules | `rg -n "from app\\.api|from app\\.infra|from app\\.infrastructure|from app\\.services|sqlalchemy|fastapi|pydantic|FastAPI|SQLAlchemy|Session|repository" backend/app/domain/astrology/runtime/chart_object_runtime_data.py backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | repo root | yes | zero hits |
| Forbidden public surfaces in new modules | `rg -n "json_builder|frontend|migrations|router" backend/app/domain/astrology/runtime/chart_object_runtime_data.py backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | repo root | yes | zero hits |
| Forbidden terminology | `rg -n "calculability" backend/app/domain/astrology/runtime backend/app/domain/astrology/builders backend/tests/unit/domain/astrology` | repo root | yes | zero hits |
| Runtime symbol inventory | `rg -n "ChartObjectRuntimeData|ChartObjectCapabilities|ChartObjectPayloads|chart_objects" backend/app/domain/astrology backend/tests -g "*.py"` | repo root | yes | expected scoped hits |
| Object type branches outside builders/tests | `rg -n "if object_type ==|if .*\\.object_type ==|match object_type|match .*\\.object_type" backend/app/domain/astrology/calculators backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/planetary_conditions backend/app/domain/astrology/interpretation backend/app/domain/astrology/interpretation_adapters -g "*.py"` | repo root | yes | zero hits |
| Public surface leak | `rg -n "chart_objects|ChartObjectRuntimeData" backend/app/services/chart backend/app/api backend/app/infra frontend/src` | repo root | yes | zero hits |
| Guardrail registry | `Select-String "RG-144" _condamad/stories/regression-guardrails.md` | repo root | yes | hit present |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format backend` | repo root | yes | pass |
| Lint | `ruff check backend` | repo root | yes | pass |
| Regression | `pytest -q` | repo root | yes | pass |

## Diff Review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Whitespace/conflict check | `git diff --check` | repo root | yes | pass |
| Diff summary | `git diff --stat` | repo root | yes | scoped changes only |
| Final status | `git status --short` | repo root | yes | expected story files plus pre-existing dirty file |
