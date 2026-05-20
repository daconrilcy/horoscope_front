<!-- Fichiers cibles CONDAMAD pour CS-204. -->

# CS-204 Target Files

## Backend

- `backend/app/domain/astrology/advanced_conditions/contracts.py`
- `backend/app/domain/astrology/advanced_conditions/hayz_calculator.py`
- `backend/app/domain/astrology/advanced_conditions/traditional_condition_normalizer.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`

## Frontend

- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/features/natal-chart/NatalExpertPanel.tsx`

## Tests

- `backend/tests/unit/domain/astrology/test_traditional_condition_normalizer.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/tests/unit/domain/astrology/test_hayz_calculator.py`
- `backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py`
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`
- `frontend/src/tests/NatalExpertPanel.test.tsx`

## Evidence

- `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/evidence/*`
- `_condamad/stories/CS-204-hayz-rejoicing-explicit-condition-contracts/generated/*`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`
