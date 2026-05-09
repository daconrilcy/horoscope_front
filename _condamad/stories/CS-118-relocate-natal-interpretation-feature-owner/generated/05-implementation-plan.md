# Implementation Plan - CS-118

## Sufficiency Gate

PASS. The story is full-closure and defines exact files, exact stale allowlist
entries, required before/after/no-shim artifacts, deterministic guards and
required validation commands.

## Frontend Assignment

`condamad-frontend-dev` worker owns `frontend/**` for the move and tests. Main
session owns capsule files, evidence, review, status and final triage.

## Planned Changes

1. Capture before ownership evidence.
2. Move the container, CSS and persona selector to
   `frontend/src/features/natal-chart/**`.
3. Rewire `NatalChartPage` and tests to the feature owner.
4. Remove exact natal entries from `COMPONENT_API_IMPORT_EXCEPTIONS`.
5. Update `component-architecture` guard to reject old paths and preserve
   presentational API-free children.
6. Persist after and no-shim evidence.
7. Run targeted tests, lint, scans and diff review.

## No Legacy Stance

Delete old paths. No wrapper, alias, fallback, re-export or broad allowlist is
allowed.
