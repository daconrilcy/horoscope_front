# Target Files

## Modified / added backend files

- `backend/app/infra/db/models/theme_natal_reading_slot.py`
- `backend/app/infra/db/models/llm_generation_run.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/services/llm_generation/natal/theme_natal_reading_slots.py`
- `backend/migrations/versions/20260601_0142_create_theme_natal_reading_slots.py`
- `backend/tests/integration/test_theme_natal_reading_slots.py`
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`

## Capsule / evidence files

- `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs/generated/*`
- `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs/evidence/schema-before.txt`
- `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs/evidence/schema-after.txt`
- `_condamad/stories/story-status.md`

## Out of scope / intentionally untouched

- Frontend files.
- Provider gateway call code.
- Prompt builders and prompt registry content.
- Physical deletion of `UserNatalInterpretationModel` or historical rows.
- Mass migration or backfill of legacy interpretations.
