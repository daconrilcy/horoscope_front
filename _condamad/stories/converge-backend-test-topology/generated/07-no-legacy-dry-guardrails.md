# No Legacy / DRY Guardrails

## Canonical topology

- Standard backend application tests: `backend/app/tests`
- Evaluation support suite: `backend/tests/evaluation`
- Backend integration support suite: `backend/tests/integration`
- LLM orchestration suite: `backend/tests/llm_orchestration`
- Backend unit support suite: `backend/tests/unit`

## Forbidden patterns for this story

- New active test files under `backend/app/**/tests` except `backend/app/tests/**`.
- Compatibility collection shim for the old embedded path.
- Opt-in exception for a test that can live under an approved root.
- Duplicate copy of `test_qualified_context.py`.
- Documentation that lists a pytest root absent from `backend/pyproject.toml`.

## Required evidence

- Static inventory before/after.
- Pytest collect-only.
- Topology guard test.
- Negative scan for the old active test path.

## Exceptions

- The non-test package `backend/app/domain/llm/prompting/tests/__init__.py` remains out of scope. This story removes active test files from that package; it does not refactor production-like registry code stored there.

## Review checklist

- The moved test assertions are preserved.
- The old test file path is gone.
- `backend/pyproject.toml` and `backend-test-topology.md` agree.
- No `requirements.txt` or dependency change was introduced.
