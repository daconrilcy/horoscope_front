# CS-196 Validation Plan

- `pytest -q backend/tests/unit/domain/astrology/test_signal_builder.py backend/tests/unit/domain/astrology/test_theme_aggregator.py backend/tests/unit/domain/astrology/test_priority_ranker.py backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py`
- `pytest -q --long backend/app/tests/integration/test_reference_data_migrations.py`
- `ruff format .`
- `ruff check .`
- Guardrail `rg` scans sur mappings locaux, infra imports domaine et vocabulaire interdit.
- Smoke import FastAPI: `python -c "from app.main import app; print(app.title)"`.
