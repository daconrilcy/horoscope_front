# Target Files

## Must inspect

- `backend/app/prediction/public_projection.py`
- `backend/app/prediction/public_astro_daily_events.py`
- `backend/app/prediction/public_astro_vocabulary.py`
- `backend/tests/unit/prediction/test_public_astro_foundation.py`
- `backend/app/tests/unit/test_public_projection.py`
- `_condamad/stories/regression-guardrails.md`

## Searches run

- `rg -n "astro_foundation|detected_events|aspect_exact_to_angle|aspect_exact_to_luminary|aspect_exact_to_personal|event_type" backend\app\prediction backend\tests backend\app\tests`
- `rg -n "aspect_exact_to_angle|aspect_exact_to_luminary|aspect_exact_to_personal|detected_events" app/prediction`

## Modified files

- `backend/app/prediction/public_astro_daily_events.py`
- `backend/app/prediction/public_projection.py`
- `backend/tests/unit/prediction/test_public_astro_foundation.py`
- `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/00-story.md`
- `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/astro-foundation-before.md`
- `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/astro-foundation-after.md`
- `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/generated/*.md`
- `_condamad/stories/story-status.md`

## Forbidden unless justified

- `frontend/src`
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py`
- Any new dependency file
- Any public schema replacement for `astro_foundation`
