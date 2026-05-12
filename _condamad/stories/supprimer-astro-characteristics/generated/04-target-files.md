# Target Files

## Must Read

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/services/reference_data_service.py`
- `backend/migrations/versions/20260218_0001_create_reference_tables.py`
- `backend/app/tests/unit/test_reference_data_service.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`

## Must Search

- `rg -n "astro_characteristics|AstroCharacteristicModel|characteristics|orb_luminaries|orb_pair_overrides" backend`
- `rg -n "legacy|compat|shim|fallback|deprecated|alias" backend/app/infra/db backend/app/tests/unit/test_reference_data_service.py backend/app/tests/integration/test_reference_data_migrations.py`

## Likely Modified

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/tests/unit/test_reference_data_service.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `backend/migrations/versions/<new>_drop_astro_characteristics.py`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`

## Forbidden Unless Directly Justified

- `frontend/**`
- Moteur natal et calculateurs d'aspects, sauf correction strictement necessaire.
- `requirements.txt` ou nouvelle dependance.
