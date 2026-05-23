# Target Files

## Must Inspect Before Implementation

- `AGENTS.md` files in scope
- Files and directories named by `../00-story.md`
- Existing tests near the affected code

## Modified Files

- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/domain/astrology/runtime/sign_runtime_data.py`
- `backend/app/domain/astrology/builders/sign_runtime_builder.py`
- `backend/app/services/chart/json_builder.py`
- `backend/tests/factories/astrology_runtime_reference_factory.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`
- `backend/tests/unit/domain/astrology/test_sign_runtime_builder.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `backend/tests/unit/domain/astrology/test_chart_signature.py`
- `backend/tests/unit/domain/astrology/test_sign_runtime_data.py`
- `_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/generated/**`
- `_condamad/stories/CS-235-brancher-attributs-structurels-signes-runtime-natal/evidence/**`
- `_condamad/stories/story-status.md`

## Forbidden Or High-Risk Files

- `frontend/**`: unchanged, out of scope.
- `backend/migrations/versions/**`: unchanged by this story; CS-234 owns schema.
- `backend/app/services/prediction/reference_seed_service.py`: unchanged by this story; existing dirty work belongs to prior CS-234 state.
