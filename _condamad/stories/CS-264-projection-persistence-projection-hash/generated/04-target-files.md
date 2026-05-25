# Target Files

## Inspected Before Implementation

- `AGENTS.md`
- `_story_briefs/cs-264-implement-projection-persistence-and-projection-hash.md`
- `_condamad/stories/CS-264-projection-persistence-projection-hash/00-story.md`
- `_condamad/stories/story-status.md`
- `backend/app/infra/db/models/chart_result.py`
- `backend/app/infra/db/repositories/chart_result_repository.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py`
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py`
- `backend/app/infra/db/base.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/migrations/env.py`

## Modified Application Files

- `backend/app/domain/astrology/projections/__init__.py`
- `backend/app/domain/astrology/projections/projection_hash.py`
- `backend/app/infra/db/models/projection_persistence.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/infra/db/repositories/projection_repository.py`
- `backend/app/services/projection_persistence_service.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
- `backend/migrations/versions/20260524_0138_create_persisted_projections.py`

## Modified Tests And Guards

- `backend/tests/unit/projections/test_projection_hash.py`
- `backend/tests/unit/projections/test_projection_persistence.py`
- `backend/tests/unit/projections/test_projection_access.py`
- `backend/tests/unit/projections/test_projection_builder_gate.py`
- `backend/tests/integration/test_projection_persistence_schema.py`
- `backend/tests/unit/domain/astrology/interpretation/test_ai_narrative_input_contract.py`
- `backend/app/tests/unit/test_backend_db_test_harness.py`
- `backend/app/tests/unit/test_backend_services_structure_guard.py`

## Evidence And Status Files

- `_condamad/stories/CS-264-projection-persistence-projection-hash/evidence/*`
- `_condamad/stories/CS-264-projection-persistence-projection-hash/generated/*`
- `_condamad/stories/story-status.md`

## Forbidden Or High-Risk Files

- `frontend/src/**`: not touched.
- `backend/app/api/**`: not touched.
- Generated OpenAPI clients: not touched.
- Prompt/provider implementation: not touched.
- Source brief: not touched.
