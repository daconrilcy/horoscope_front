# No Legacy / DRY Guardrails

## Forbidden unless explicitly required by the story

- Compatibility wrappers
- Transitional aliases
- Legacy import paths
- Duplicate active implementations
- Re-export modules preserving old imports
- Silent fallback behavior
- Tests that preserve legacy paths as nominal behavior

## Required when relevant

- One canonical path per responsibility
- Negative search evidence for removed symbols or imports
- Tests or architecture guards that fail if a legacy path is reintroduced
- Explicit errors instead of silent fallback for missing canonical configuration

## Story-specific canonical paths

- Topology registry: `_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md`
- Pytest runtime source: `backend/pyproject.toml`
- Guard owner: `backend/app/tests/unit/test_backend_test_topology.py`

## Required negative evidence

- No backend test file outside documented roots.
- No `backend/app/**/tests/test_*.py` or `*_test.py` outside `backend/app/tests`.
- No duplicate topology guard file introduced.

## Reviewer questions

- Did we delete the legacy path or only move the problem?
- Did we preserve an old path “temporarily”?
- Did any test import the old namespace?
- Did any doc, registry, or config still reference the old path?
