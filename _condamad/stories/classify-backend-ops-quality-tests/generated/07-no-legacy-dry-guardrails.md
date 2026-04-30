# No Legacy / DRY Guardrails

## Canonical Surfaces

- Ownership registry: `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md`
- Reintroduction guard: `backend/app/tests/unit/test_backend_quality_test_ownership.py`
- Pytest collection source: `backend/pyproject.toml`

## Forbidden Patterns

- Unowned `test_*scripts*.py`
- Unowned `test_secret*.py`
- Unowned `test_security*.py`
- Unowned `test_ops_*.py`
- Pytest marker without documented command
- Hidden quality/ops command that is not listed in the ownership registry
- Duplicate registry for the same ownership decision
- Silent removal from backend pytest collection

## Required Evidence

- Filesystem inventory compared against registry rows.
- Runtime collect-only proving standard pytest collection still succeeds.
- Guard test failing on missing owner, missing command, unsupported owner, or registry/file mismatch.
- Classified legacy scan hits.

## Exceptions

- OS/subprocess dependencies are allowed only as exact rows in the registry.
