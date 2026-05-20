# Validation Plan

## Environment Assumptions

- OS/shell: Windows PowerShell.
- Python commands must run after `.\\.venv\\Scripts\\Activate.ps1`.
- Backend dependencies come from `backend/pyproject.toml`.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Golden suite | `pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | repo root | yes | all tests pass |
| Sect contract regression | `pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py` | repo root | yes | all tests pass |
| Dignity scoring regression | `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` | repo root | yes | all tests pass |
| Advanced sect regression | `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py` | repo root | yes | all tests pass |
| Hayz regression | `pytest -q backend/tests/unit/domain/astrology/test_hayz_calculator.py` | repo root | yes | all tests pass |
| Profile regression | `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py` | repo root | yes | all tests pass |
| Dominance regression | `pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py` | repo root | yes | all tests pass |
| Adapter regression | `pytest -q backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py` | repo root | yes | all tests pass |
| Natal contract regression | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` | repo root | yes | all tests pass |
| JSON projection regression | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` | repo root | yes | all tests pass |
| Chart result regression | `pytest -q backend/app/tests/unit/test_chart_result_service.py` | repo root | yes | all tests pass |

## DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Legacy sect names | `rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code|planet_sect_code|planet_sect_legacy|sect_score_legacy|legacy_planet_sect" backend/app backend/tests -g "*.py"` | repo root | yes | no active legacy hits |
| Forbidden local constants | `rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|SECT_PLANETS|DAY_SECT_PLANETS|NIGHT_SECT_PLANETS|ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES|JOY_HOUSES|PLANETARY_JOYS" backend/app backend/tests/unit/domain/astrology -g "*.py"` | repo root | yes | no active doctrine constants |
| Horizon tuple scan | `rg -n "\\b7,\\s*8,\\s*9,\\s*10,\\s*11,\\s*12\\b|\\b1,\\s*2,\\s*3,\\s*4,\\s*5,\\s*6\\b" backend/app/domain/astrology backend/app/services/chart backend/tests/unit/domain/astrology -g "*.py"` | repo root | yes | hits classified |
| Downstream calculator imports | `rg -n "SectCalculator" backend/app/domain/astrology/condition backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters backend/app/services/chart -g "*.py"` | repo root | yes | zero hits |
| Planet condition calculator imports | `rg -n "PlanetSectConditionCalculator|planet_sect_condition_calculator" backend/app/domain/astrology/condition backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters backend/app/services/chart -g "*.py"` | repo root | yes | zero hits |
| Forbidden domain dependencies | `$forbidden = "Session|select\\(|from app\\.infra|from app\\.services|from app\\.api|from app\\.domain\\.prediction|OpenAI|AIEngineAdapter|chat\\.completions|prompt"; rg -n $forbidden backend/app/domain/astrology/dignities backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/condition backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters -g "*.py"` | repo root | yes | hits classified |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | repo root | yes | no formatting errors |
| Lint | `ruff check .` | repo root | yes | no lint errors |

## Evidence Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Evidence files exist | `Test-Path _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-index.md; Test-Path _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-before.json; Test-Path _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-after.json; Test-Path _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-validation.md` | repo root | yes | all return `True` |
| Case IDs documented | `rg -n "G1|G2|G3|G4|G5|G6|G7|G8|G9|G10|G11|G12" _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-index.md` | repo root | yes | all IDs covered |
| Snapshot JSON before | `python -m json.tool _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-before.json` | repo root | yes | valid JSON |
| Snapshot JSON after | `python -m json.tool _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-after.json` | repo root | yes | valid JSON |

## Diff Review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-scoped files |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no errors |
| Worktree status | `git status --short` | repo root | yes | expected files only |
