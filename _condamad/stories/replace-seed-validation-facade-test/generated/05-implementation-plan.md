# Implementation Plan

## Repository findings

- The facade test was `backend/app/tests/unit/test_seed_validation.py` and its executable body was `pass`.
- Canonical seed behavior is owned by `backend/app/ops/llm/bootstrap/use_cases_seed.py`.
- `SeedValidationError` already existed, but no contract validation ran before `seed_use_cases`.
- The repository had one executable `assert True` in `test_pricing_experiment_service.py`.

## Changes

- Add `validate_use_case_seed_contracts` to validate seed contracts before DB writes.
- Replace the facade seed test with two executable tests: invalid required persona contract raises, current canonical contracts pass.
- Add `test_backend_noop_tests.py` as an AST guard for direct empty test bodies and executable `assert True`.
- Convert the pricing test to `pytest.raises`.
- Persist before/after scans and the seed validation decision.

## No Legacy stance

- No compatibility shim or alias added.
- The no-op test is replaced, not skipped.
- The guard accepts explicit `pytest.skip` with reason but rejects silent no-op tests.

## Rollback strategy

- Revert the seed validator and its tests together if the product rule is rejected.
- Keep the no-op guard unless a reviewer explicitly accepts a tracked exception.
