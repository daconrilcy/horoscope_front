# Validation Plan

## Environment assumptions

- Run from repository root on Windows PowerShell.
- Activate Python venv before every Python command: `.\.venv\Scripts\Activate.ps1`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Advanced sect integration | `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py backend/tests/unit/domain/astrology/test_hayz_calculator.py backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py` | repo root | yes | all tests pass |
| Dignity and public projection regression | `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` | repo root | yes | all tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Block chart sect calculator in downstream layers | `rg -n "SectCalculator" backend/app/domain/astrology/condition backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters backend/app/services/chart -g "*.py"` | repo root | yes | zero hits |
| Block planet sect calculator in downstream layers | `rg -n "PlanetSectConditionCalculator|planet_sect_condition_calculator" backend/app/domain/astrology/condition backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters backend/app/services/chart -g "*.py"` | repo root | yes | zero hits |
| Block local sect constants | `rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|SECT_PLANETS|DAY_SECT_PLANETS|NIGHT_SECT_PLANETS|ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES" backend/app -g "*.py"` | repo root | yes | zero hits |
| Block local horizon tuples | `rg -n "\b7,\s*8,\s*9,\s*10,\s*11,\s*12\b|\b1,\s*2,\s*3,\s*4,\s*5,\s*6\b" backend/app/domain/astrology backend/app/services/chart -g "*.py"` | repo root | yes | zero hits |
| Classify legacy sect names | `rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code|planet_sect_code|planet_sect_legacy|sect_score_legacy|legacy_planet_sect" backend/app backend/tests -g "*.py"` | repo root | yes | only runtime/reference/test terminology, classified in evidence |
| Classify forbidden pure-domain dependencies | `$forbidden = "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|OpenAI|AIEngineAdapter|chat\.completions|prompt"; rg -n $forbidden backend/app/domain/astrology/dignities backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/condition backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters -g "*.py"` | repo root | yes | no new forbidden dependency; existing `prompt_hint` classified |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | repo root | yes | no formatting errors |
| Lint | `ruff check .` | repo root | yes | no lint errors |

## Evidence checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Before snapshot JSON | `python -m json.tool _condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/advanced-sect-scoring-before.json` | repo root | yes | valid JSON |
| After snapshot JSON | `python -m json.tool _condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/advanced-sect-scoring-after.json` | repo root | yes | valid JSON |
| Evidence keywords | `rg -n "hayz|out_of_sect|PlanetSectCondition|ChartSectResult|score delta|public shape" _condamad/stories/CS-199-advanced-sect-scoring-integration/evidence` | repo root | yes | required terms present |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only CS-199 files changed |
| Worktree status | `git status --short` | repo root | yes | expected story files only |

## Commands that may be skipped only with justification

- Full `pytest -q` may be skipped only for time/environment constraints after targeted and regression subsets pass.
