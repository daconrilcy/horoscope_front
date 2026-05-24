# Implementation Plan

## Initial repository findings

- Story path and brief source match `_condamad/stories/story-status.md`.
- Required generated capsule files were missing; `condamad_prepare.py` was run
  with the explicit CS-251 key and capsule validation passes.
- Existing public API guards already cover `chart_objects` and
  `ChartObjectRuntimeData`; CS-251 needs roadmap governance plus expanded raw
  runtime/OpenAPI checks.

## Proposed changes

- Add one canonical architecture document for product primitives and projection
  sequencing.
- Add one machine-readable evidence snapshot for primitive decisions.
- Extend existing backend tests for OpenAPI neutrality and public raw-runtime
  non-exposure.
- Persist validation, OpenAPI route proof, AC traceability and final evidence.

## Files to modify

- `docs/architecture/official-product-primitives-public-projections.md`
- `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/**`
- `_condamad/stories/story-status.md`

## Files to delete

- None in story scope.
- Cleanup only: remove the accidental helper-created duplicate capsule directory
  after verifying it is inside `_condamad/stories/`.

## Tests to add or update

- Update public contract compatibility test for additional forbidden raw runtime
  terms.
- Update API contract neutrality test to validate the CS-251 roadmap document,
  JSON snapshot, OpenAPI schemas and route inventory.

## Risk assessment

- Fixed-star exposure remains `needs-user-decision`; CS-257 must stay blocked
  until public/gated/rejected policy is selected.
- Full `pytest -q` may be affected by pre-existing dirty worktree changes from
  CS-246 through CS-250; record exact outcome.

## Rollback strategy

- Remove the CS-251 architecture document and evidence snapshot, then revert the
  two targeted test additions and capsule evidence updates.
