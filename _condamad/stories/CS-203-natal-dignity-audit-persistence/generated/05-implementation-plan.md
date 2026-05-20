<!-- Plan d'implementation CONDAMAD pour CS-203. -->

# Implementation Plan

## Architecture Finding

`ChartResultRepository.create` already returns the persisted `ChartResultModel`
with its database id. `DignityReferenceRepository` already owns the audit-table
upsert and resolves planet/profile/system/reference ids.

## Selected Approach

1. Add a narrow `dignity_audit_mapper` module that converts precomputed
   `PlanetDignityResult` values into `ChartPlanetDignityResultInput`.
2. Call the mapper/upsert from `ChartResultService.persist_trace` after
   `chart_results` creation.
3. Add service tests for row count, score/breakdown parity, sect payload,
   idempotence and explicit failure behavior.
4. Capture persistent before/after and validation evidence.

## No Legacy Stance

No fallback, compatibility alias, doctrinal constant, calculator import, public
payload read from the audit table, migration or seed change is allowed.

## Rollback

Remove the mapper import/call and added tests/evidence. Existing repository
upsert behavior remains unchanged.
