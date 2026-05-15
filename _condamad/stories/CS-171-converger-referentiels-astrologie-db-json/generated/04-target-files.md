# Target Files

## Backend application

- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/repositories/astrology_reference_sources.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/domain/astrology/celestial_runtime_catalog.py`
- `backend/app/domain/astrology/swisseph_runtime.py`
- `backend/app/domain/astrology/interpretation/profile_fields.py`
- `backend/app/domain/astrology/**`
- `backend/app/domain/prediction/natal_sensitivity.py`
- `backend/app/domain/llm/runtime/output_validator.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/services/llm_generation/**`
- `backend/app/services/natal/pdf_export_service.py`

## Migrations et tests

- `backend/migrations/versions/20260514_0107_repair_astral_aspect_families_seed.py`
- `backend/migrations/versions/20260226_0027_add_default_orb_deg_to_aspects.py`
- `backend/app/tests/unit/test_astrology_reference_catalog_guard.py`
- Tests existants adaptes sous `backend/app/tests` et `backend/tests`.

## Documentation et donnees

- `docs/recherches astro/astral_aspect_families.json`
- `docs/recherches astro/structural_reference_catalog.json`
- `docs/recherches astro/astral_aspect_family.json` supprime
- Documentation astro ajustee pour ne plus referencer l'ancien nom singulier ni les symboles retires.
