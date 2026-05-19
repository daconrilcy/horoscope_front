# Validation Plan CS-191

Commands, run from repository root after `.\.venv\Scripts\Activate.ps1`:

- `pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py`
- `pytest -q backend/tests/unit/domain/astrology/test_dignity_contracts.py`
- `pytest -q backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py`
- `pytest -q backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py`
- `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
- `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py`
- `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `pytest -q backend/app/tests/unit/test_chart_json_builder.py`
- `pytest -q backend/app/tests/unit/test_chart_result_service.py`
- `Set-Location backend; ruff format --check .; ruff check .`
- `rg -n "Session|select\(|from app\.infra|from app\.services|from app\.api" backend/app/domain/astrology/dignities -g "*.py"`
- `rg -n "DIGNITY_SCORES|DOMICILE_SCORE|ACCIDENTAL_DIGNITY_SCORES|score_value\s*=\s*[-0-9]" backend/app/domain/astrology/dignities -g "*.py"`
- `rg -n "OpenAI|AIEngineAdapter|chat\.completions|prompt|interpretation|micro_note" backend/app/domain/astrology/dignities -g "*.py"`
