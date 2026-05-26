# No Legacy / DRY Guardrails

## Story-local guardrails

- Manual QA profiles remain synthetic and non-sensitive.
- Evidence lives under the CS-310 capsule, not in application source comments.
- `/natal` rendering remains owned by `frontend/src/pages/NatalChartPage.tsx`, `frontend/src/features/natal-chart/NatalInterpretation.tsx`, and `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`.
- Projection HTTP calls remain owned by `frontend/src/api/astrologyProjections.ts`.
- Backend projection contracts remain unchanged.
- No new route, client, wrapper, shim, alias, fallback display, package, migration, or duplicate QA runner is introduced.
- No inline `style` attribute is added in touched TSX surfaces.

## Regression guardrails

- `RG-047`: targeted inline-style scan on `/natal` TSX surfaces plus `pnpm lint`.
- Story-local sensitive-surface scan: prompt, provider, replay, admin, debug, internal payload, and raw runtime terms must not be visible in public `/natal` owners.
- Story-local direct-client scan: no component-level direct `fetch` or `axios` to `/v1/astrology/projections`.

## Evidence

- `evidence/profile-set.json` proves synthetic non-sensitive profile coverage.
- `evidence/manual-qa-ledger.json` proves one traced outcome per profile.
- `evidence/sensitive-surface-ledger.json` records the sensitive-surface result.
- Static scans and validation commands are recorded in `evidence/validation.txt`.
