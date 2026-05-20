<!-- Carte des fichiers cibles pour CS-203. -->

# Target Files

## Read First

- `backend/app/services/chart/result_service.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/infra/db/models/chart_result.py`
- `backend/app/infra/db/models/dignity_reference.py`
- `backend/app/infra/db/repositories/chart_result_repository.py`
- `backend/app/infra/db/repositories/dignity_reference_repository.py`
- `backend/app/tests/unit/test_chart_result_service.py`
- `backend/app/tests/unit/test_dignity_reference_seed.py`

## Expected Writes

- `backend/app/services/chart/result_service.py`
- `backend/app/services/chart/dignity_audit_mapper.py`
- `backend/app/tests/unit/test_chart_result_service.py`
- `_condamad/stories/CS-203-natal-dignity-audit-persistence/evidence/*`
- `_condamad/stories/CS-203-natal-dignity-audit-persistence/generated/*`
- `_condamad/stories/story-status.md`

## Forbidden Writes Unless Blocker Approved

- `frontend/**`
- `backend/app/api/**`
- `backend/app/domain/astrology/dignities/sect_calculator.py`
- `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py`
- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/condition/**`
- `backend/app/domain/astrology/dominance/**`
- `backend/app/domain/astrology/interpretation_adapters/**`
- `backend/app/domain/prediction/**`
- `docs/db_seeder/**`
- `backend/migrations/**`
