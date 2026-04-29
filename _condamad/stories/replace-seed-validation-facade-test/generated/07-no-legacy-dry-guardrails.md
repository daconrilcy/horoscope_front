# No Legacy / DRY Guardrails

## Forbidden for this story

- Keeping `backend/app/tests/unit/test_seed_validation.py` as a no-op facade.
- Replacing `pass` with `assert True`.
- Adding a skip without explicit reason.
- Adding a parallel seed validation module outside the canonical seed bootstrap surface.
- Adding compatibility aliases, wrappers, or fallbacks for invalid seed contracts.

## Canonical owners

- Seed validation behavior: `backend/app/ops/llm/bootstrap/use_cases_seed.py`.
- Use case contract shape: `backend/app/domain/llm/configuration/canonical_use_case_registry.py`.
- Backend no-op test policy: `backend/app/tests/unit/test_backend_noop_tests.py`.

## Regression guardrails

- Applicable: `RG-014` added by this story for backend no-op collected tests.
- Consulted and non-applicable: `RG-001` through `RG-013`, except their existing test topology constraints informed placement under `backend/app/tests/unit`.

## Search evidence

| Pattern | Status |
|---|---|
| `seed_validation_required_persona_empty_allowed` | Absent after replacement. |
| `assert True` | No executable assertion remains; only guard documentation/self-reference hits. |
| `pass$` in tests | Remaining hits are nested control-flow statements, not direct empty collected test bodies; AST guard passes. |

## Review checklist

- Confirm seed validation stays in the canonical seed bootstrap module.
- Confirm the no-op guard would fail on a direct `pass` test.
- Confirm no API, frontend, DB migration, or unrelated test topology change was introduced.
