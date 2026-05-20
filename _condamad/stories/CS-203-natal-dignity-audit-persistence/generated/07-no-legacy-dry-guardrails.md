<!-- Guardrails No Legacy / DRY pour CS-203. -->

# No Legacy / DRY Guardrails

## Canonical Owners

- Dignity calculation: `backend/app/domain/astrology/dignities/**`.
- Chart result persistence: `backend/app/services/chart/result_service.py`.
- Audit upsert: `DignityReferenceRepository.upsert_chart_planet_dignity_result`.
- Public projection: `backend/app/services/chart/json_builder.py`.

## Forbidden Implementation

- No calculator import from audit persistence code.
- No local doctrine constants.
- No fallback when audit references are missing.
- No audit-table read for public payload construction.
- No frontend, API, migration or seed change.
- No compatibility alias, shim, duplicate repository or wrapper.

## Required Evidence

- Tests prove audit rows are written from precomputed dignity results.
- Tests prove score/breakdown/sect parity and idempotence.
- Scans classify every forbidden symbol hit.
- Forbidden path diffs remain empty.
