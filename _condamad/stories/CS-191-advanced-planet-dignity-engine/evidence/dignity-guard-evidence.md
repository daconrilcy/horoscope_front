# Dignity Guard Evidence

Validation date: 2026-05-19.

Commands run from repository root after `.\.venv\Scripts\Activate.ps1`:

- `pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py backend/tests/unit/domain/astrology/test_dignity_contracts.py backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` - PASS, 51 passed.
- `Set-Location backend; pytest -q` - PASS, 2686 passed, 1 skipped, 1177 deselected.
- `Set-Location backend; ruff format --check .; ruff check .` - PASS.
- `rg -n "Session|select\(|from app\.infra|from app\.services|from app\.api" backend/app/domain/astrology/dignities -g "*.py"` - ZERO_HIT.
- `rg -n "DIGNITY_SCORES|DOMICILE_SCORE|ACCIDENTAL_DIGNITY_SCORES|score_value\s*=\s*[-0-9]" backend/app/domain/astrology/dignities -g "*.py"` - ZERO_HIT.
- `rg -n "OpenAI|AIEngineAdapter|chat\.completions|prompt|interpretation|micro_note" backend/app/domain/astrology/dignities -g "*.py"` - ZERO_HIT.
- Snapshot invariant check with venv Python: PASS, only `dignities` is added.
