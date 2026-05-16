# Target Files

## Must read

- `backend/app/services/natal/calculation_service.py`
- `backend/app/domain/prediction/event_detector.py`
- `backend/app/domain/prediction/enriched_astro_events_builder.py`
- `backend/app/domain/prediction/public_astro_vocabulary.py`
- `backend/app/domain/prediction/transit_signal_builder.py`
- `backend/app/domain/prediction/intraday_activation_builder.py`
- `backend/app/services/prediction/engine_orchestrator.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/tests/unit/test_astrology_reference_catalog_guard.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`

## Must search

- `sign_rulerships\s*=\s*\{|payload\.setdefault\("sign_rulerships"|payload\["house_axes"\]\s*=|payload\["aspect_orb_rules"\]\s*=`
- `ASPECTS_V1|ASPECTS\s*=\s*\{|orb_max_fallback.*2\.0|_ASPECT_TONES|_STAR_DATA`
- `app\.domain\.prediction|app\.services\.prediction` under `backend/app/domain/astrology`

## Likely modified

- Backend prediction aspect consumers.
- Backend natal calculation service.
- Backend tests/guards.
- Story evidence files.

## Forbidden unless justified

- `frontend/**`
- `backend/requirements.txt`
- `backend/migrations/versions/**`
