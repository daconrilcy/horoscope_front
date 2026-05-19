# Validation Plan

## Environment assumptions

- Run every Python command after `.\.venv\Scripts\Activate.ps1`.
- Work from repository root unless command states otherwise.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Mutual reception | `pytest -q backend/tests/unit/domain/astrology/test_mutual_reception_calculator.py` | repo root | yes | all pass |
| Hayz and sect | `pytest -q backend/tests/unit/domain/astrology/test_hayz_calculator.py` | repo root | yes | all pass |
| Aspect conditions | `pytest -q backend/tests/unit/domain/astrology/test_besiegement_detector.py` | repo root | yes | all pass |
| Heliacal/orientation | `pytest -q backend/tests/unit/domain/astrology/test_heliacal_conditions.py` | repo root | yes | all pass |
| Speed classifier | `pytest -q backend/tests/unit/domain/astrology/test_speed_classifier.py` | repo root | yes | all pass |
| Advanced engine | `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py` | repo root | yes | all pass |
| Natal contract | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` | repo root | yes | all pass |
| Dominance integration | `pytest -q backend/tests/unit/domain/astrology/test_dominance_integration.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py` | repo root | yes | all pass |
| JSON projection and chart persistence | `pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` | repo root | yes | all pass |
| Runtime repository and guards | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py` | repo root | yes | all pass |
| Migration integration | `pytest -q backend/app/tests/integration/test_reference_data_migrations.py` | repo root | yes | all pass |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Pure domain boundary | `rg -n "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|from app\.services\.prediction" backend/app/domain/astrology/advanced_conditions -g "*.py"` | repo root | yes | zero hits |
| No narration/LLM | `rg -n "OpenAI|AIEngineAdapter|chat\.completions|\bprompt\b|narration|micro_note" backend/app/domain/astrology/advanced_conditions -g "*.py"` | repo root | yes | zero hits |
| No local advanced maps | `rg -n "ADVANCED_CONDITION_TYPES|ADVANCED_CONDITION_WEIGHTS|HAYZ_RULES|MUTUAL_RECEPTION_RULES|PLANET_SPEED_THRESHOLDS|HELIACAL_PHASES|BENEFIC_PLANETS|MALEFIC_PLANETS" backend/app backend/tests frontend/src -g "*.py" -g "*.ts" -g "*.tsx"` | repo root | yes | zero hits |
| Deferred techniques absent | `rg -n "translation[_ ]of[_ ]light|collection[_ ]of[_ ]light|planetary[_ ]war|antiscia|contra[_ -]antiscia|primary[_ ]directions|zodiacal[_ ]releasing|firdaria|annual[_ ]profections" backend/app/domain/astrology/advanced_conditions backend/app/services/chart/json_builder.py -g "*.py"` | repo root | yes | zero hits |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | repo root | yes | no formatting errors |
| Lint | `ruff check .` | repo root | yes | no lint errors |
| Diff check | `git diff --check` | repo root | yes | no whitespace/conflict errors |

Skipped commands must be recorded in `10-final-evidence.md` with reason, risk
and compensating evidence.
