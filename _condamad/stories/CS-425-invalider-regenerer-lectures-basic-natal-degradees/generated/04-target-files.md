# Target Files - CS-425

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/00-story.md`
- `_condamad/stories/regression-guardrails.md` scoped IDs
- Backend Basic cache, contract, quota and public-boundary tests named by the story

## Modified files

- `backend/app/domain/astrology/reading/basic_natal_contracts.py`
- `backend/app/domain/astrology/reading/__init__.py`
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py`
- `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`
- `backend/tests/integration/test_basic_natal_v2_cache_invalidation.py`
- `backend/tests/unit/test_basic_natal_reading_contracts.py`
- `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/evidence/**`
- `_condamad/stories/CS-425-invalider-regenerer-lectures-basic-natal-degradees/generated/**`
- `_condamad/stories/story-status.md`

## Forbidden or high-risk files

- `backend/alembic/**` remained untouched and is absent in this checkout.
- `frontend/src/**` remained untouched.
- No brief source file was modified.
