# Target Files - CS-185

## Fichiers applicatifs modifies

- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/domain/astrology/runtime/sign_runtime_data.py`
- `backend/app/domain/astrology/builders/sign_runtime_builder.py`
- `backend/app/services/reference_data_service.py`
- `backend/app/services/prediction/reference_seed_service.py`

## Tests et guards modifies

- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `backend/tests/factories/astrology_runtime_reference_factory.py`
- `backend/tests/unit/domain/astrology/test_sign_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_chart_signature.py`
- `backend/tests/unit/domain/astrology/test_sign_runtime_data.py`

## Artefacts CONDAMAD

- `_condamad/stories/CS-185-brancher-profils-signes-runtime-natal/evidence/sign-profile-runtime-before.json`
- `_condamad/stories/CS-185-brancher-profils-signes-runtime-natal/evidence/sign-profile-runtime-after.json`
- `_condamad/stories/CS-185-brancher-profils-signes-runtime-natal/evidence/openapi-impact.md`
- `_condamad/stories/CS-185-brancher-profils-signes-runtime-natal/evidence/guard-evidence.md`
