# Implementation Plan

## Current architecture finding

- The entitlement note is historical and guarded as non-runtime truth.
- Its old `backend/docs` location looks canonical and should be removed.

## Selected target approach

- Move the retained historical note to `docs/architecture/`.
- Remove the stale backend docs ownership row.
- Keep the parity test active for OpenAPI paths, SQLAlchemy tables and status.

## Files to modify

- `docs/architecture/entitlements-canonical-platform.md`
- `backend/docs/ownership-index.md`
- `backend/app/tests/unit/test_entitlement_docs_runtime_parity.py`

## Tests to add or update

- Update `test_entitlement_docs_runtime_parity.py` to read the new path and assert old-path absence.

## Deletion candidates

- Old path only: `backend/docs/entitlements-canonical-platform.md`.

## Risk assessment

- Runtime/API drift is covered by the existing OpenAPI/table assertions.

## Rollback strategy

- Restore the old path only if `docs/architecture/` is rejected by user decision.
