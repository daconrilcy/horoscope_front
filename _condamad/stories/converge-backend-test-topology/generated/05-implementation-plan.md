# Implementation Plan

## Findings

- `backend/pyproject.toml` already declares the retained backend roots: `app/tests`, `tests/evaluation`, `tests/integration`, `tests/llm_orchestration`, and `tests/unit`.
- One active test file remains embedded under `backend/app/domain/llm/prompting/tests`.
- `test_backend_pytest_collection.py` still contains an opt-in exception for that embedded test.

## Approach

1. Persist the before inventory from the current static file layout.
2. Move `test_qualified_context.py` into `backend/tests/llm_orchestration`.
3. Remove the exact opt-in exception from `test_backend_pytest_collection.py`.
4. Add a topology document that lists the approved pytest roots.
5. Add a guard that fails on undocumented roots, embedded domain tests, and doc/config drift.
6. Persist the after inventory and final evidence.

## No Legacy stance

- No compatibility re-export or duplicate test path.
- The old embedded test file path must disappear from active test inventory.
- The residual non-test package under `app/domain/llm/prompting/tests` is documented as out of scope for this test-topology story and is not a collected test root.

## Rollback

Revert the moved test, restored opt-in exception, topology guard, and CONDAMAD artifacts for this story only.
