<!-- Carte des fichiers cibles CONDAMAD pour CS-205. -->

# CS-205 Target Files

## Must read

- `backend/app/domain/astrology/dignities/essential_dignity_calculator.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py`
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`
- `backend/tests/unit/domain/astrology/test_dignity_contracts.py`
- `backend/tests/unit/domain/astrology/fixtures/traditional_golden_cases.py`
- `backend/tests/unit/domain/astrology/fixtures/triplicity_seed_cases.py`
- `docs/db_seeder/astrology/astral_triplicity_ruler_assignments.json`

## Must search

- `rg -n "AstrologyRuntimeReference|dignity_reference|triplicity" backend/tests backend/app -g "*.py"`
- `rg -n "TRIPLICITY_RULERS|DAY_TRIPLICITY_RULERS|NIGHT_TRIPLICITY_RULERS|PARTICIPATING_TRIPLICITY_RULERS|FIRE_TRIPLICITY|EARTH_TRIPLICITY|AIR_TRIPLICITY|WATER_TRIPLICITY" backend/app -g "*.py"`
- `rg -n "if .*chart_sect.*day|if .*chart_sect.*night|planet_code\\s+in|element\\s*==\\s*['\\\"]fire|element\\s*==\\s*['\\\"]earth|element\\s*==\\s*['\\\"]air|element\\s*==\\s*['\\\"]water" backend/app/domain/astrology/dignities -g "*.py"`

## Likely modified

- `backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py`
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
- `backend/tests/unit/domain/astrology/fixtures/triplicity_seed_cases.py`
- `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/*`
- `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/generated/*`
- `_condamad/stories/story-status.md`

## Forbidden unless justified

- `backend/app/domain/astrology/dignities/**`
- `backend/app/services/chart/json_builder.py`
- `backend/app/api/**`
- `backend/app/infra/**`
- `backend/app/domain/prediction/**`
- `backend/migrations/**`
- `docs/db_seeder/**`
- `frontend/**`
