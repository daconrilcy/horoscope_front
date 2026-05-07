# Implementation Plan - CS-085

## Current architecture finding

The landing cluster already uses a `--landing-*` semantic namespace, premium tokens and design-system guard tests. The remaining work is a bounded CSS/token migration with persistent before/after evidence.

## Selected approach

1. Capture before scans for colors, typography, radius/elevation/fallbacks, No Legacy vocabulary and page-scoped namespaces.
2. Migrate repeated landing literals to existing tokens or documented `--landing-*` owners.
3. Document any new or changed landing owners in `token-namespace-registry.md` and typography decisions in `typography-roles.md`.
4. Add or adjust a deterministic anti-return guard in `design-system-guards.test.ts`.
5. Capture after scans and run required frontend/story validations.

## Frontend subagent assignment

Frontend implementation is delegated to `condamad-frontend-dev` with ownership limited to `frontend/**`.

## No Legacy stance

No compatibility, alias, fallback, migration-only namespace, broad exception or accepted limitation is allowed.

## Rollback strategy

Revert only CS-085-owned frontend and capsule evidence changes if validation reveals a blocker; preserve pre-existing dirty files.
