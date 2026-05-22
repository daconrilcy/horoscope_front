<!-- Plan d'implementation genere pour CS-217. -->

# Implementation Plan

1. Capture baseline and preserve the pre-existing dirty file outside story scope.
2. Add immutable runtime contracts with explicit capability-to-payload validation.
3. Add a pure builder that projects planets, astral points, angles, and house cusps from existing runtime collections.
4. Wire `NatalResult.chart_objects` as an internal excluded field after historical collections are built.
5. Add targeted unit/integration/architecture tests.
6. Run story validation commands and update final evidence/status.

## No Legacy Position

`ChartObjectRuntimeData` is the only new contract owner. No shim, alias,
fallback, compatibility path, or public API projection is allowed.

## Rollback

Revert only the CS-217 files listed in the final diff; preserve unrelated dirty files.
