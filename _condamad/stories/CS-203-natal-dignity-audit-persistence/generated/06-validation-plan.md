<!-- Plan de validation CONDAMAD pour CS-203. -->

# Validation Plan

## Environment Assumptions

- OS: Windows / PowerShell.
- Python commands require `.\.venv\Scripts\Activate.ps1`.
- Backend dependencies come from `backend/pyproject.toml`.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Chart result service | `pytest -q backend/app/tests/unit/test_chart_result_service.py` | repo root | yes | all pass |
| Public JSON projection | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` | repo root | yes | all pass |
| Dignity scoring regression | `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` | repo root | yes | all pass |
| Golden cases | `pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | repo root | yes | all pass |
| Repository upsert | `pytest -q backend/app/tests/unit/test_dignity_reference_seed.py` | repo root | yes | all pass |

## Regression Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Sect calculator | `pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py` | repo root | yes | all pass |
| Advanced conditions | `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py` | repo root | yes | all pass |
| Natal contract | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` | repo root | yes | all pass |

## DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Forbidden calculators 1 | `rg -n "SectCalculator|PlanetSectConditionCalculator|PlanetDignityScoringService" backend/app/services/chart backend/app/infra/db/repositories -g "*.py"` | repo root | yes | no audit persistence hits |
| Forbidden calculators 2 | `rg -n "EssentialDignityCalculator|AccidentalDignityCalculator|AdvancedConditionEngine" backend/app/services/chart backend/app/infra/db/repositories -g "*.py"` | repo root | yes | no audit persistence hits |
| Forbidden calculators 3 | `rg -n "PlanetConditionProfileService|PlanetConditionSignalBuilder" backend/app/services/chart backend/app/infra/db/repositories -g "*.py"` | repo root | yes | no audit persistence hits |
| Forbidden calculators 4 | `rg -n "PlanetDominanceEngine|InterpretationAdapterEngine" backend/app/services/chart backend/app/infra/db/repositories -g "*.py"` | repo root | yes | no audit persistence hits |
| Legacy aliases | `rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code|planet_sect_code|planet_sect_legacy|sect_score_legacy|legacy_planet_sect" backend/app backend/tests -g "*.py"` | repo root | yes | no active hits |
| Doctrine constants | `rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|SECT_PLANETS|DAY_SECT_PLANETS|NIGHT_SECT_PLANETS|ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES|JOY_HOUSES|PLANETARY_JOYS|HAYZ_RULES" backend/app -g "*.py"` | repo root | yes | no audit persistence hits |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | repo root | yes | no formatting errors |
| Lint | `ruff check .` | repo root | yes | no lint errors |

## Diff Review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story files changed |
| Whitespace/conflicts | `git diff --check` | repo root | yes | no errors |
| Worktree status | `git status --short` | repo root | yes | expected files only |
