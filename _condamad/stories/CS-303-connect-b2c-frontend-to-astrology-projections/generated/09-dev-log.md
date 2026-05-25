# Dev Log

## Preflight

- Initial `git status --short`: clean.
- Story registry row confirmed: `CS-303` path and brief source matched.
- Capsule was incomplete; repaired with `condamad_prepare.py --repair-generated-only` and validated PASS.

## Search evidence

- Inspected `/natal` route owner, central API client, natal API hooks, interpretation component, disclaimer policy, backend projection public contracts, and targeted guardrails.
- Existing frontend architecture guard requires natal interpretation container under `features/natal-chart` and presentational children without API imports.

## Implementation notes

- Added canonical wrapper `frontend/src/api/astrologyProjections.ts`.
- Connected `/natal` interpretation surface to both B2C projections using existing `chartId`.
- Kept API/error normalization in feature/API owners; presentational component receives normalized render state only.
- Added CSS classes in `NatalInterpretation.css`; no inline styles.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `pnpm test -- astrologyProjectionsApi natalInterpretation --runInBand` | FAIL | Vitest does not support `--runInBand`; rerun without it. |
| `pnpm test -- astrologyProjectionsApi natalInterpretation` | PASS | Matched natal interpretation tests; API wrapper file was run separately. |
| `pnpm test -- natalChartApi` | PASS | API wrapper tests included. |
| `pnpm test -- component-architecture-guards natalInterpretation NatalChartPage natalChartApi` | PASS | Architecture, /natal, component, API targeted suite. |
| `pnpm lint` | PASS | TypeScript lint/typecheck script. |
| `pnpm test` | FAIL_WITH_LIMITATIONS | 18 unrelated failures in ShortcutCard, DashboardPage, DailyHoroscopePage, ConsultationsPage localization/flow tests. |
| `python -B -m pytest backend\tests\api\test_projection_openapi.py backend\tests\api\test_projection_endpoint.py backend\tests\api\test_projection_authorization.py -q --tb=short` | PASS | 8 backend projection API tests. |
| `python -B -c app.openapi/app.routes contract check` | PASS | Verified `/v1/astrology/projections` runtime route and OpenAPI. |
| targeted `rg` guard scans | PASS | Direct HTTP, inline style, forbidden internals, disclaimer ownership, `any`. |

## Issues encountered

- One backend OpenAPI check was first launched from `backend/` with an activation path relative to repo root; rerun correctly from repo root with venv active before `cd backend`.
- `pnpm test` created an untracked `frontend/pnpm-lock.yaml`; removed because project scripts use pnpm without committed frontend lock in this workspace.

## Decisions made

- No backend runtime changes: endpoint and schemas already exist and are validated by runtime checks.
- No new dependency, shim, fallback builder, generated client, or alternate route.

## Final `git status --short`

- See `generated/10-final-evidence.md`.
