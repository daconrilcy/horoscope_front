# Target Files - CS-189

## Modifies

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

## Evidence

- `_condamad/stories/CS-189-brancher-etoiles-fixes-scoring-runtime/evidence/fixed-stars-runtime-before.md`
- `_condamad/stories/CS-189-brancher-etoiles-fixes-scoring-runtime/evidence/fixed-stars-runtime-after.md`
- `_condamad/stories/CS-189-brancher-etoiles-fixes-scoring-runtime/evidence/guard-evidence.md`

## Explicit non-targets

- `frontend/**`
- `backend/app/domain/astrology/**`
- `backend/migrations/versions/**`
