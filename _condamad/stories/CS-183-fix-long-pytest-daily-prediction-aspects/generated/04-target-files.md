# Target Files

## Cibles initiales

- `backend/app/domain/prediction/aspect_reference.py`
- `backend/app/domain/prediction/event_detector.py`
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py`
- `backend/app/services/prediction/engine_orchestrator.py`
- `backend/app/services/prediction/public_predictions.py`
- `backend/app/domain/prediction/public_projection.py`
- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/api/v1/routers/internal/llm/qa.py`
- `backend/app/tests/unit/test_natal_structural_v3.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `backend/app/tests/regression/fixtures/*.json`

## Recherches

- `rg "aspect_orbs_by_code|load_public_projection_aspect_profiles|aspect_profiles" backend/app`
- `rg "20260516_0119|20260516_0126" backend`
