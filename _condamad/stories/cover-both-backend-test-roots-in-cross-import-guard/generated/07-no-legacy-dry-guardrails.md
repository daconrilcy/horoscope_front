# No Legacy / DRY Guardrails

## Canonical owner

- `backend/app/tests/unit/test_backend_test_helper_imports.py` remains the single guard owner for backend cross-test imports from executable `test_*.py` modules.

## Forbidden patterns

- Compatibility wrappers.
- Transitional aliases.
- Duplicate active guard implementations.
- Allowlists for cross-test imports.
- Imports from executable test modules:
  - `from app.tests.integration.test_`
  - `from app.tests.unit.test_`
  - `from app.tests.regression.test_`
  - `from tests.integration.test_`
  - `from tests.unit.test_`
  - `from tests.regression.test_`

## Required negative evidence

- AST guard: `pytest -q app/tests/unit/test_backend_test_helper_imports.py`.
- Static scan: `rg -n "from app\.tests\.(integration|unit|regression)\.test_|from tests\.(integration|unit|regression)\.test_" app/tests tests -g "test_*.py"` returns zero hits.

## Applicable regression guardrails

- `RG-013`: no imports between backend executable test modules.
- `RG-010`: guard roots remain aligned with backend test topology.

## Exceptions

No active exception is allowed for this story. The allowlist register remains zero-entry.

## Review checklist

- `BACKEND_ROOT` is `backend`, not `backend/app`.
- `TEST_ROOTS` contains exactly `app/tests` and `tests`.
- The AST scan did not become regex-only.
- No duplicate guard file was introduced.
