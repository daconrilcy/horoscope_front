# Implementation Plan

## Initial repository findings

- The natal service already had a mutable reference payload flow.
- Existing tests passed partial business dictionaries into domain helpers.
- House systems existed as canonical DB seed data but were not called by the reference seeding path.
- Aspect strength still exposed forbidden threshold constants and the aspect runtime builder emitted `phase="unknown"`.

## Proposed changes

- Introduce one immutable `AstrologyRuntimeReference` contract family under `domain/astrology/runtime`.
- Add infra mapper/repository to load DB rows and JSON-backed reference payloads into typed contracts.
- Switch `NatalCalculationService` and `build_natal_result` to the runtime reference contract.
- Seed canonical house systems during reference seeding so runtime integrity can be blocking.
- Remove forbidden sentinel/constant names from the natal runtime path.
- Migrate tests and fixtures to a typed runtime reference factory.

## Files to modify

- `backend/app/domain/astrology/**`
- `backend/app/services/natal/calculation_service.py`
- `backend/app/services/reference_data_service.py`
- `backend/app/infra/db/repositories/**`
- `backend/app/tests/unit/**`
- `backend/tests/unit/domain/astrology/**`
- `_condamad/stories/CS-172-big-bang-reference-runtime-astrology/**`

## Files to delete

- None.

## Tests to add or update

- Add runtime contract tests.
- Add repository integrity tests.
- Add architecture guard tests.
- Update natal and aspect tests to consume runtime references.

## Risk assessment

- Full backend pytest did not complete within the 10 minute command budget.
- Runtime DB incompleteness is now blocking by design and may expose seed gaps outside targeted tests.

## Rollback strategy

- Revert the runtime repository/service wiring and test migrations together; do not keep a mixed `dict` and runtime-reference flow.
