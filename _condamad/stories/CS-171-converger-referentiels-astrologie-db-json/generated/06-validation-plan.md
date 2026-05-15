# Validation Plan

## Commandes executees

Toutes les commandes Python ont ete executees apres activation du venv:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
```

## Validation ciblee

- `alembic upgrade head`
- `pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/integration/test_seed_31_prediction_v2.py app/tests/unit/test_prediction_reference_repository.py`
- `pytest -q app/tests/integration/test_reference_data_migrations.py tests/unit/domain/astrology/test_aspect_strength.py tests/unit/domain/astrology/test_aspect_runtime_builder.py tests/unit/domain/astrology/test_aspect_interpretation_builder.py tests/unit/domain/astrology/test_aspect_interpretation_facts.py app/tests/unit/test_astrology_prediction_boundary.py`
- `pytest -q app/tests/unit/test_ephemeris_provider.py app/tests/unit/test_houses_provider.py app/tests/unit/test_swisseph_observability.py app/tests/unit/test_aspect_orb_overrides.py`
- `pytest -q app/tests/unit/test_natal_tt.py app/tests/unit/test_user_natal_chart_service.py app/tests/unit/test_user_astro_profile_service.py app/tests/integration/test_consultations_router.py::test_generate_accepts_enriched_other_person_payload app/tests/integration/test_user_birth_profile_api.py`
- `pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/integration/test_seed_31_prediction_v2.py app/tests/unit/test_prediction_reference_repository.py app/tests/integration/test_reference_data_migrations.py tests/unit/domain/astrology/test_aspect_strength.py tests/unit/domain/astrology/test_aspect_runtime_builder.py tests/unit/domain/astrology/test_aspect_interpretation_builder.py tests/unit/domain/astrology/test_aspect_interpretation_facts.py app/tests/unit/test_astrology_prediction_boundary.py app/tests/unit/test_reference_data_service.py app/tests/unit/test_ephemeris_provider.py app/tests/unit/test_houses_provider.py app/tests/unit/test_swisseph_observability.py app/tests/unit/test_aspect_orb_overrides.py app/tests/unit/test_natal_tt.py app/tests/unit/test_user_natal_chart_service.py app/tests/unit/test_user_astro_profile_service.py app/tests/integration/test_consultations_router.py::test_generate_accepts_enriched_other_person_payload app/tests/integration/test_user_birth_profile_api.py`
- `pytest -q app/tests/integration/test_daily_prediction_qa.py app/tests/regression/test_engine_non_regression.py`
- `pytest -q --maxfail=1`
- `ruff format .`
- `ruff check .`

## Validation complete

`pytest -q --maxfail=1` est vert sur la suite backend complete: `3720 passed, 12 skipped, 7 warnings in 1268.96s`.

## Demarrage local

Commande exacte:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
uvicorn app.main:app --reload
```
