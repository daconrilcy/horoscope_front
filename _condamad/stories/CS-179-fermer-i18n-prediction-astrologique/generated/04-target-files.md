# Target Files

## Must Read

- `backend/app/domain/prediction/public_astro_vocabulary.py`
- `backend/app/domain/prediction/astrologer_prompt_builder.py`
- `backend/app/domain/prediction/public_projection.py`
- `backend/app/domain/prediction/public_astro_daily_events.py`
- `backend/app/services/reference_data/astrology_translation_resolver.py`
- `backend/app/tests/unit/test_astrology_localization_guardrails.py`
- `backend/tests/unit/prediction/test_astrologer_prompt_builder.py`
- `backend/app/tests/unit/test_public_projection.py`
- `backend/tests/unit/prediction/test_public_astro_daily_events.py`

## Likely Modified

- `backend/app/domain/prediction/public_astro_vocabulary.py`
- `backend/app/domain/prediction/astrologer_prompt_builder.py`
- `backend/app/domain/prediction/public_projection.py`
- `backend/app/domain/prediction/public_astro_daily_events.py`
- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/services/prediction/public_predictions.py`
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py`
- `backend/app/tests/unit/test_astrology_localization_guardrails.py`
- `backend/tests/unit/prediction/test_astrologer_prompt_builder.py`
- `backend/tests/unit/prediction/test_public_astro_daily_events.py`
- `backend/tests/unit/prediction/test_public_astro_foundation.py`

## Required Searches

- Forbidden symbols in `backend/app/domain/prediction`.
- `from app.services` imports in `backend/app/domain/prediction`.
- Direct consumers of the old local helpers.

## Forbidden Unless Justified

- `frontend/**`
- `backend/app/domain/astrology/**`
- New dependencies or new backend base folders.
