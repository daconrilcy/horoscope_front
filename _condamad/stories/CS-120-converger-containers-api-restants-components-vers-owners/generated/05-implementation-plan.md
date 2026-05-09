<!-- Plan d'implementation vivant pour CS-120. -->

# Implementation Plan - CS-120

## Current Finding

The story is closure-ready: it identifies exactly seven batches, requires
before/after evidence, and has deterministic guards. The implementation surface
is frontend-only.

## Approach

1. Persist before inventory for the current E-010 hits.
2. Delegate frontend implementation to `condamad-frontend-dev` with write scope
   limited to `frontend/**`.
3. Move each API-owning component to its canonical owner and repoint consumers.
4. Delete old component owner files and stale allowlist rows.
5. Run targeted tests, guards, scans and lint.
6. Persist after inventory, migration map and final evidence.
7. Run review and fix loop until clean.

## No Legacy Stance

No compatibility export, wrapper, fallback, alias or broad exception is allowed.
An unresolved old path must become a blocker, not a limitation.

## Rollback Strategy

Because this story changes imports and file locations without contract changes,
rollback is a scoped revert of CS-120 touched frontend files and story evidence.
