# Final Evidence - CS-189

Status: done

## Summary

CS-189 brancher-etoiles-fixes-scoring-runtime est implementee. Les etoiles fixes
daily restent DB-backed, transportent magnitude/keywords/source, sont filtrees
par les parametres runtime, exposent des metadata structurees et peuvent
contribuer via `DomainRouter` + `ContributionCalculator`.

## Files changed

- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/services/prediction/context_loader.py`
- `backend/app/domain/prediction/enriched_astro_events_builder.py`
- `backend/app/domain/prediction/domain_router.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/tests/unit/prediction/test_enriched_astro_events_builder.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `backend/app/tests/unit/test_domain_router.py`
- `backend/app/tests/unit/test_contribution_calculator.py`
- `backend/app/tests/integration/test_seed_31_prediction_v2.py`

## Tests and checks

- `ruff format .`: PASS.
- `ruff check .`: PASS.
- `pytest -q tests/unit/prediction/test_enriched_astro_events_builder.py app/tests/unit/test_prediction_reference_repository.py tests/unit/prediction/test_public_astro_daily_events.py`: PASS, 44 passed.
- `pytest -q app/tests/unit/test_domain_router.py app/tests/unit/test_contribution_calculator.py`: PASS via combined targeted run, included in 70 passed.
- `pytest --long -q app/tests/integration/test_seed_31_prediction_v2.py`: PASS, 7 passed.
- `pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_localization_guardrails.py`: PASS, 11 passed.
- `python -B -c "from app.main import app; print(app.title)"`: PASS, `horoscope-backend`.
- Story validation and strict lint: PASS.

## Negative scans

- `_STAR_DATA|fixed_star_longitudes|fixed_star_display_name|FIXED_STAR_`: zero hit.
- `dist.*1\.0` in `enriched_astro_events_builder.py`: zero hit.
- `app\.domain\.prediction|app\.services\.prediction` in `app/domain/astrology`: zero hit.

## AC evidence

- AC1: `FixedStarData` includes `visual_magnitude`, `keywords`, `source_category`, `source_key`; repository and freezer preserve them.
- AC2: builder reads `fixed_star_orb_deg`; no hardcoded `dist <= 1.0` remains.
- AC3: builder filters by `fixed_star_max_visual_magnitude` and keeps missing magnitude.
- AC4: metadata includes `orb_max`, `star_key`, display name, magnitude, source and keywords; public projection still displays Regulus.
- AC5: retained events use positive `fixed_star_base_weight`; fixed-star routing uses `fixed_star_category_weights`; contribution test is non-zero.
- AC6: local fixed-star catalogs remain absent.
- AC7: required backend validations passed, including the integration seed test via `--long`.

## Risks

- Aucun risque restant identifie.
