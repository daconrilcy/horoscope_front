# Validation Plan

## Environment assumptions

- PowerShell Windows.
- Toutes les commandes Python s'exécutent après `.\.venv\Scripts\Activate.ps1`.

## Commands

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend` | yes | no format failure |
| Lint | `ruff check .` | `backend` | yes | no lint error |
| Natal targeted tests | `pytest -q app/tests/unit/test_natal_calculation_service.py app/tests/unit/test_astrology_runtime_reference_repository.py` | `backend` | yes | pass |
| Guards | `pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_runtime_reference_guard.py` | `backend` | yes | pass |
| Boundary | `pytest -q app/tests/unit/test_astrology_prediction_boundary.py` | `backend` | yes | pass |
| Prediction tests | `pytest -q tests/unit/prediction/test_public_astro_daily_events.py tests/unit/prediction/test_enriched_astro_events_builder.py app/tests/unit/test_transit_signal_v3.py` | `backend` | yes | pass |
| Local regression | `pytest -q app/tests/unit/test_event_detector.py app/tests/unit/test_intraday_activation_v3.py app/tests/unit/test_impulse_signal_v3.py app/tests/unit/test_engine_orchestrator.py` | `backend` | yes | pass |
| Natal scan | `rg -n 'sign_rulerships\s*=\s*\{|payload\.setdefault\("sign_rulerships"|payload\["house_axes"\]\s*=|payload\["aspect_orb_rules"\]\s*=' app/services/natal -g '*.py'` | `backend` | yes | zero hits |
| Aspect scan | `rg -n 'ASPECTS_V1|ASPECTS\s*=\s*\{|orb_max_fallback.*2\.0|_ASPECT_TONES|_STAR_DATA' app/domain/astrology app/domain/prediction -g '*.py'` | `backend` | yes | only classified exceptions |
| Boundary scan | `rg -n 'app\.domain\.prediction|app\.services\.prediction' app/domain/astrology -g '*.py'` | `backend` | yes | zero hits |
| Diff review | `git diff --stat` and `git diff --check` | repo root | yes | expected scope |
