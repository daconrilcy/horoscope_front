# Dev Log

## Preflight

- Initial `git status --short` showed untracked CONDAMAD story directories, including this story.
- `AGENTS.md` was read.
- `_condamad/stories/regression-guardrails.md` was read; RG-001 through RG-009 are non-regression constraints because this story changes backend test ownership and collection.

## Repository findings

- `backend/pyproject.toml` already includes `app/tests`, `tests/evaluation`, `tests/integration`, `tests/llm_orchestration`, and `tests/unit`.
- `backend/app/tests/unit/test_backend_pytest_collection.py` still allowed `app/domain/llm/prompting/tests/test_qualified_context.py` as an opt-in exception.
- Static inventory before implementation had one active test file under `backend/app/domain/llm/prompting/tests`.

## Implementation

- Added `backend-test-topology.md` as the topology register.
- Moved `test_qualified_context.py` to `backend/tests/llm_orchestration`.
- Removed the obsolete opt-in exception from `test_backend_pytest_collection.py`.
- Added `test_backend_test_topology.py` to guard doc/config drift and embedded test roots.
- Added RG-010 to `_condamad/stories/regression-guardrails.md`.

## Validation

- `ruff format .` reformatted one file.
- `ruff check .` passed.
- Targeted guards and moved test passed.
- `pytest --collect-only -q --ignore=.tmp-pytest` passed with 3475 collected tests.
- `pytest -q` passed with 3463 passed, 12 skipped, 7 warnings.
