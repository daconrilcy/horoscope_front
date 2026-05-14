# Target Files

## Must read

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `backend/migrations/versions/20260513_0095_create_astral_house_systems.py`

## Must search

- `rg -n "house_interpretation|HouseInterpretation" backend _condamad docs`
- `rg -n "astro_characteristics|__tablename__ = \"astral_houses\"|reference_version_id" backend/app backend/tests`

## Likely modified

- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/migrations/versions/20260514_0096_create_house_interpretation_profiles.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `_condamad/stories/story-status.md`

## Forbidden unless justified

- `backend/app/domain/astrology/**`
- `backend/app/domain/prediction/**`
- `frontend/**`
- `docs/recherches astro/house_interpretation_vocabulary.json`
