# Execution Brief - CS-186

## Objective

Fix failing backend tests by replacing partial sign fixtures with explicit complete sign fixture payloads.

## Boundaries

- Modify only test fixture helpers and directly affected tests.
- Keep production runtime, repositories, migrations and seed JSON untouched.
- Preserve `runtime_reference_from_mapping()` strict rejection of incomplete signs.

## Completion Definition

- Targeted failing test files pass.
- `test_astrology_runtime_reference_guard.py` passes.
- Ruff format/check pass.
- Final evidence records commands, dirty preflight files, diff review and remaining risks.

## Halt Conditions

- A fix requires weakening CS-185 runtime strictness.
- A fix requires editing unrelated user changes.
- Validation failure points outside this story scope and cannot be safely classified.
