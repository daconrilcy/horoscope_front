# CS-221 Validation Plan

## Environment Assumptions

- Repository root: `C:\dev\horoscope_front`
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend quality commands run from `backend/` after activation.

## Required Checks

| Purpose | Command | Working directory | Required | Result |
|---|---|---|---:|---|
| Targeted CS-221/runtime tests | `pytest -q backend/tests/unit/domain/astrology/test_chart_object_house_position_rulership_runtime.py backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | repo root | yes | PASS |
| Rulers/dominance/golden regression | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | repo root | yes | PASS |
| Format | `ruff format .` | `backend/` | yes | PASS |
| Lint | `ruff check .` | `backend/` | yes | PASS after import order fix |
| Backend regression | `pytest -q` | `backend/` | yes | PASS |
| Object type scan | `rg -n "object_type ==|\.object_type ==|ChartObjectType\.PLANET|ChartObjectType\.LUMINARY" backend/app/domain/astrology/builders backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance -g "*.py"` | repo root | yes | PASS with classified existing builder construction hit |
| Rulership resolver/table scan | `rg -n "HouseRulershipPayloadBuilder|MarsRulershipPayloadBuilder|new.*HouseRulerResolver|SIGN_RULERS|sign_rulers\s*=\s*\{" backend/app/domain/astrology -g "*.py"` | repo root | yes | PASS zero active hits |
| House modality local constants scan | `rg -n "\{1, 4, 7, 10\}|\{2, 5, 8, 11\}|angular.*succedent.*cadent" backend/app/domain/astrology/builders backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance -g "*.py"` | repo root | yes | PASS zero hits |
| Anti-narrative scan | `rg -n "interpretation|narrative|prompt|llm|meaning|psychological" backend/app/domain/astrology/runtime backend/app/domain/astrology/builders -g "*.py"` | repo root | yes | PASS with pre-existing/domain-governed hits classified |
| Guardrail lookup | `rg -n "RG-148" _condamad/stories/regression-guardrails.md` | repo root | yes | PASS |
| Final evidence lookup | `rg -n "CS-221 Final Evidence" _condamad/stories/CS-221-chart-object-house-position-rulership-runtime/evidence/validation.md` | repo root | yes | PASS after evidence update |
| Adjacent diff | `git diff -- backend/app/domain/astrology/planetary_conditions backend/app/domain/astrology/interpretation backend/app/services/chart/json_builder.py backend/app/api backend/app/infra backend/migrations frontend/src` | repo root | yes | PASS empty |
| Whitespace diff | `git diff --check` | repo root | yes | PASS, line-ending warnings only |

## Skipped Checks

- None.
