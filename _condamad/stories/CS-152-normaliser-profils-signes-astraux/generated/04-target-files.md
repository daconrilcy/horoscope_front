# Target Files

## Must Read

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `backend/app/tests/unit/test_reference_data_service.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `backend/app/tests/integration/test_seed_31_prediction_v2.py`
- `docs/recherches astro/signs_keywords.json`

## Must Search

- `SignModel`, `SignRulershipModel`, `signs`, `sign_rulerships`
- `get_sign_rulerships(reference_version_id)`
- `AstroCharacteristicModel`, `astro_characteristics`

## Likely Modified

- Backend DB models, repositories, seed service, migration files and targeted backend tests.
- CONDAMAD generated evidence files and story status registry.

## Forbidden Unless Justified

- `frontend/**`
- Public API routers, unless tests prove payload adaptation is required.
