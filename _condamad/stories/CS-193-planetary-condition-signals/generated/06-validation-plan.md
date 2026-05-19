# Validation Plan

## Environment Assumptions

- Run Python commands from repository root after `.\\.venv\\Scripts\\Activate.ps1`.
- No frontend validation is required because CS-193 does not touch `frontend/**`.

## Commands

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Builder unit tests | `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_signal_builder.py` | repo root | yes | all pass |
| Natal contract tests | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` | repo root | yes | all pass |
| Chart JSON and persistence tests | `pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` | repo root | yes | all pass |
| Runtime repository guards | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py` | repo root | yes | all pass |
| Migration tests | `pytest -q backend/app/tests/integration/test_reference_data_migrations.py` | repo root | yes | all pass |
| Format | `ruff format .` | repo root | yes | no formatting errors |
| Lint | `ruff check .` | repo root | yes | no lint errors |
| Condition boundary scan | `rg -n "Session\|select\\(\|from app\\.infra\|from app\\.services\|from app\\.api\|from app\\.domain\\.prediction\|from app\\.services\\.prediction" backend/app/domain/astrology/condition -g "*.py"` | repo root | yes | zero hits |
| LLM/narration scan | `rg -n "OpenAI\|AIEngineAdapter\|chat\\.completions\|\\bprompt\\b\|narration\|micro_note" backend/app/domain/astrology/condition -g "*.py"` | repo root | yes | zero hits |
| Local signal threshold scan | `rg -n "SIGNAL_THRESHOLDS\|CONDITION_SIGNAL_RULES\|CONDITION_SIGNAL_PROFILES\|FUNCTIONAL_STRENGTH_THRESHOLDS\|VISIBILITY_SIGNAL_LEVELS" backend/app backend/tests frontend/src -g "*.py" -g "*.ts" -g "*.tsx"` | repo root | yes | zero active hits |
| Integration/projection scan | `rg -n "planet_condition_signals\|condition_signals" backend/app/services/chart/json_builder.py backend/app/domain/astrology/natal_calculation.py backend/app/domain/astrology/condition -g "*.py"` | repo root | yes | projection/integration only |

