# Target Files - CS-209

## Inspected before implementation

- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/app/domain/astrology/planetary_conditions/__init__.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
- `backend/app/domain/astrology/advanced_conditions/contracts.py`
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `AGENTS.md`

## Modified production files

- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
- `backend/app/domain/astrology/planetary_conditions/__init__.py`

## Modified test files

- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py`

## Story evidence files

- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/generated/05-implementation-plan.md`
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/generated/09-dev-log.md`
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/generated/10-final-evidence.md`
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/generated/11-code-review.md`
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/evidence/validation.md`

## Forbidden adjacent surfaces checked

- `backend/app/domain/astrology/advanced_conditions`
- `backend/app/domain/astrology/dignities`
- `backend/app/domain/astrology/condition`
- `backend/app/domain/astrology/dominance`
- `backend/app/domain/astrology/interpretation_adapters`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/api`
- `backend/app/infra`
- `backend/migrations`
- `frontend/src`
