# Target Files

## Must read

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/services/reference_data_service.py`
- `backend/migrations/versions/*reference*.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `backend/app/tests/unit/test_reference_data_service.py`

## Must search

- `rg "astral_planet_sign_dignities|astral_aspect_orb_rules|seed_version_defaults|_seed" backend`
- `rg "chart_results|UniqueConstraint|JSON" backend/app/infra/db/models backend/migrations`

## Likely modified

- Backend DB models and repositories under `backend/app/infra/db/**`
- Alembic migration under `backend/migrations/versions/`
- Reference seed logic
- Backend tests

## Forbidden unless justified

- Frontend files
- Authentication/billing/LLM unrelated modules
