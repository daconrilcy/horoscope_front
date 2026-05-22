# Validation Plan

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Dignity runtime | `pytest -q backend/tests/unit/domain/astrology/test_chart_object_dignity_runtime.py` | repo root | yes | pass |
| Dominance runtime | `pytest -q backend/tests/unit/domain/astrology/test_chart_object_dominance_runtime.py` | repo root | yes | pass |
| Runtime/builder/natal/architecture | `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | repo root | yes | pass |
| Natal result contract | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` | repo root | yes | pass |
| Historical regression | `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | repo root | yes | pass |
| Dignities package | `pytest -q backend/tests/unit/domain/astrology/dignities` | repo root | yes | pass |
| Dominance integration | `pytest -q backend/tests/unit/domain/astrology/test_dominance_integration.py` | repo root | yes | pass |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `Push-Location backend; ruff format .; Pop-Location` | repo root | yes | no diff-required error |
| Lint | `Push-Location backend; ruff check .; Pop-Location` | repo root | yes | pass |
| Full tests | `pytest -q` | repo root | yes | pass |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Type eligibility | `rg -n "object_type ==|\\.object_type ==|ChartObjectType\\.PLANET|ChartObjectType\\.LUMINARY" backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance` | repo root | yes | zero active hits |
| Nominal-code/list eligibility | `rg -n "TRADITIONAL_PLANETS|planet_name ==|code in" backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance` | repo root | yes | only classified historical calculator hits, no CS-220 selector/projector eligibility hit |
| Direct historical collection | `rg -n "planet_positions" backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance` | repo root | yes | zero hits |
| Forbidden builders | `rg -n "PlanetDignityPayloadBuilder|MoonDignityPayloadBuilder|MarsDominancePayloadBuilder|AngleDominancePayloadBuilder" backend/app backend/tests` | repo root | yes | zero hits |
| Narrative payloads | `rg -n "interpretation|narrative|prompt|llm|meaning|psychological" backend/app/domain/astrology/runtime backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance` | repo root | yes | only pre-existing non-payload references classified |
