# Validation Plan

Commands:

```powershell
.\.venv\Scripts\Activate.ps1; Set-Location backend; ruff check .
.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest app/tests/unit/test_reference_data_service.py -q
.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_context_loader.py app/tests/unit/test_engine_orchestrator.py::test_build_natal_chart_uses_contextual_aspect_profiles -q
.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest app/tests/integration/test_seed_31_prediction_v2.py -q --long
.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest app/tests/integration/test_daily_prediction_api.py -q --long
.\.venv\Scripts\Activate.ps1; Set-Location backend; pytest app/tests/integration/test_daily_prediction_qa.py::test_categories_all_present -q --long
```

Full `pytest -q --long` is optional because the targeted failing clusters are covered and the full suite takes about 15 minutes locally.
