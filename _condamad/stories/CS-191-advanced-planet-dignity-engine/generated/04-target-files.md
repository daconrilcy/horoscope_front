# Target Files CS-191

Modified implementation files:

- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`

New implementation files:

- `backend/app/domain/astrology/dignities/__init__.py`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/sect_calculator.py`
- `backend/app/domain/astrology/dignities/essential_dignity_calculator.py`
- `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`

Tests and evidence:

- `backend/tests/unit/domain/astrology/test_dignity_contracts.py`
- `backend/tests/unit/domain/astrology/test_sect_calculator.py`
- `backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py`
- `backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py`
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `_condamad/stories/CS-191-advanced-planet-dignity-engine/evidence/**`
