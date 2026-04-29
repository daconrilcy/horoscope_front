# Execution Brief - replace-seed-validation-facade-test

## Primary objective

Replace the no-op seed validation test with executable behavior and add a deterministic guard against collected backend tests that pass through `pass` or `assert True`.

## Boundaries

- Scope is limited to seed contract validation and backend test-quality guardrails.
- Do not change frontend code, DB schema, API routes, or global test topology.
- Do not add dependencies.
- Do not add a root directory under `backend/`.

## Implementation decision

The rule is active. Required persona seed contracts must fail explicitly when the required placeholder contract is empty. Implement this in the canonical seed bootstrap module and prove current canonical contracts remain valid.

## Done conditions

- `backend/app/tests/unit/test_seed_validation.py` contains executable assertions.
- `backend/app/tests/unit/test_backend_noop_tests.py` blocks direct empty test bodies and executable `assert True`.
- The existing `assert True` test is converted to a real assertion.
- Required CONDAMAD evidence files are complete.
- Venv-backed lint, targeted tests, collection, story validation, app import, and full pytest pass.
