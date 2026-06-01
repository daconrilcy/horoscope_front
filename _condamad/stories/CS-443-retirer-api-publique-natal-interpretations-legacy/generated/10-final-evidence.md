# Final Evidence - CS-443-retirer-api-publique-natal-interpretations-legacy

## Story status

- Story key: `CS-443-retirer-api-publique-natal-interpretations-legacy`
- Validation outcome: PASS
- Ready for review: yes
- Implementation review outcome: CLEAN
- Story status synchronized: `done`
- Capsule path: `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `00-story.md`
- Initial `git status --short`: `_condamad/run-state.json` dirty before implementation.
- Pre-existing dirty files: `_condamad/run-state.json`, out of scope.
- AGENTS.md instructions considered: user-provided `AGENTS.md` content for this repository.
- Capsule generated: repaired missing generated files with `condamad_prepare.py --repair-generated-only`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status updated to `ready-to-review`. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated during capsule repair. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC10 traced. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated during capsule repair. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Story-specific commands followed with `--long` where required. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | No-legacy evidence recorded below. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## Implementation summary

- Removed the historical public natal interpretation router from canonical FastAPI registration and deleted its public route module.
- Kept `/v1/theme-natal/readings` as the only public product-action surface for nominal frontend reads/actions.
- Removed frontend production calls to `/v1/natal/interpretation`, `/v1/natal/interpretations*`, and `/v1/natal/pdf-templates`.
- Added runtime/OpenAPI architecture guard coverage and persisted route/OpenAPI before/after snapshots.

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Removed public router registration and file. | Runtime route assertion and architecture guard PASS. | PASS | No 410 facade kept. |
| AC2 | Deleted historical list/get/delete/pdf public router. | Runtime prefix assertion and route snapshot PASS. | PASS | |
| AC3 | Removed route from loaded app. | OpenAPI assertions and `openapi-after.json` PASS. | PASS | |
| AC4 | Modern public route remains `/v1/theme-natal/readings`. | TestClient public-read accepted/rejected tests PASS. | PASS | |
| AC5 | No bounded public mapping symbols remain. | Production mapping scan PASS. | PASS | |
| AC6 | Frontend production client has no historical URL calls. | Production URL scan and Vitest suites PASS. | PASS | |
| AC7 | Visible delete removed; PDF uses product actions. | `natalInterpretation.test.tsx` and lint PASS. | PASS | |
| AC8 | `route-consumption-audit.md` added. | Capsule/evidence review PASS. | PASS | |
| AC9 | Before/after snapshots added. | Snapshot files exist and were generated from loaded app. | PASS | |
| AC10 | Reintroduction guard added. | Architecture guard and scans PASS. | PASS | |

## Files changed

- Backend: `backend/app/api/v1/routers/registry.py`, deleted `backend/app/api/v1/routers/public/natal_interpretation.py`.
- Backend tests/guards: architecture guard, evaluation marker, product-action integration tests, and public-read integration tests.
- Frontend: natal-chart API client, natal interpretation menus/section, and `natalInterpretation.test.tsx`.
- Evidence: `route-consumption-audit.md`, `evidence/**`, generated traceability/final evidence.

## Files deleted

- `backend/app/api/v1/routers/public/natal_interpretation.py`

## Tests added or updated

- Updated `backend/tests/integration/test_theme_natal_public_api_product_actions.py`.
- Rewrote `backend/tests/integration/test_theme_natal_public_reads.py`.
- Updated `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`.
- Updated `frontend/src/tests/natalInterpretation.test.tsx`.
- Review fix: updated stale backend tests so removed public routes are asserted absent, not preserved as a `410 Gone` facade.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `condamad_prepare.py --repair-generated-only ...` | repo root | PASS | 0 | Missing generated files repaired. |
| `condamad_validate.py ...` | repo root | PASS | 0 | Capsule valid before implementation. |
| `ruff format <modified backend files>` | `backend` | PASS | 0 | One file reformatted. |
| `python -B -m pytest --long -q tests/integration/... --tb=short` | `backend` | PASS | 0 | 12 passed. |
| `python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py --tb=short` | `backend` | PASS | 0 | 12 passed. |
| Runtime `app.routes` / `app.openapi()` assertions | `backend` | PASS | 0 | Removed paths absent; modern path present. |
| `ruff check .` | `backend` | PASS | 0 | All checks passed. |
| `pnpm --dir frontend test -- ...` | repo root | PASS | 0 | 4 files / 136 tests. |
| `pnpm --dir frontend lint` | repo root | PASS | 0 | TypeScript lint configs passed. |
| Production forbidden scans | repo root | PASS | 1 | `rg` no-match exit 1 is expected. |
| Review/fix backend pytest suite. Exact command in `evidence/validation.txt`. | `backend` | PASS | 0 | 38 passed after stale-test correction. |
| Review/fix backend targeted `ruff format`. Exact command in `evidence/validation.txt`. | `backend` | PASS | 0 | One test file reformatted. |
| `ruff check .` | `backend` | PASS | 0 | All checks passed after review fix. |
| `pnpm --dir frontend test -- natalChartApi.test.tsx natalInterpretation.test.tsx natalPublicDomGuard.test.tsx NatalChartPage.test.tsx` | repo root | PASS | 0 | 4 files / 136 tests after review fix. |
| `pnpm --dir frontend lint` | repo root | PASS | 0 | TypeScript lint remains clean after review fix. |
| Runtime route/OpenAPI absence assertion | `backend` | PASS | 0 | Removed paths absent; modern path present. |
| `condamad_story_validate.py` and `condamad_story_lint.py --strict` | repo root | PASS | 0 | Story contract still valid after review evidence update. |

## Commands skipped or blocked

- Full backend suite skipped: targeted integration, architecture, runtime, and lint checks cover the story surface.
- Full frontend suite skipped: targeted story suites and frontend lint cover the touched surface.
 
## Diff review

- `git diff --stat` reviewed for the story surface.
- `git diff --check` PASS with CRLF warnings only.

## Validation

- `condamad_validate.py`: PASS.
- Backend targeted integration tests with `--long`: PASS, 12 passed.
- Backend architecture guard: PASS, 12 passed.
- Runtime `app.routes` and `app.openapi()` assertions: PASS.
- `ruff format` targeted files: PASS; `ruff check .`: PASS.
- Frontend targeted Vitest suites: PASS, 4 files / 136 tests.
- `pnpm --dir frontend lint`: PASS.
- Forbidden production URL and mapping scans: PASS, no matches.
- Review/fix validation: PASS, 38 backend tests after converting stale 410 facade tests to absence guards.
- Story validation and strict lint: PASS after final review evidence update.

## Skipped or limited checks

- Full backend suite was not run; targeted backend tests, architecture guard, runtime checks, and `ruff check .` were run for the story surface.
- Full frontend test suite was not run; targeted story suites plus frontend lint were run.
- Local dev servers were not left running; FastAPI app import/runtime route checks and Vite/Vitest tooling executed successfully.

## DRY / No Legacy evidence

- No public route remains mounted for `POST /v1/natal/interpretation`.
- No public route remains mounted under `/v1/natal/interpretations`.
- Public OpenAPI omits historical natal interpretation and PDF-template paths.
- Bounded production scans have zero hits for historical public URLs and old public mapping symbols.
- No 410 compatibility route, redirect, wrapper, or mounted fallback was kept for the removed public API.
- Backend tests no longer preserve the removed public routes as nominal `410 Gone` compatibility facades.

## Final worktree status

- Pre-existing dirty file kept out of scope: `_condamad/run-state.json`.
- Story changes are limited to the implementation/evidence files listed above.

## Remaining risks

- `frontend/src/api/natal-chart/index.ts` returns an empty history list until a dedicated modern public list contract exists; this is the chosen no-legacy disposition for removed history endpoints.
- External consumers of the deleted public endpoints now receive no route; this is expected because the story forbids a compatibility facade.

## Suggested reviewer focus

- Review the frontend history/template disposition and confirm no modern list/PDF-template contract is expected in this story.
- Review `test_legacy_natal_generation_inventory_guard.py` runtime/OpenAPI guard strength.

## Feedback loop routing

- `no-propagation`: no durable guardrail or skill update was needed. The Windows case-insensitive capsule-path incident was corrected locally and did not affect final code state.
- Review/fix `no-propagation`: stale test correction is local to CS-443 and does not require a durable registry or skill update.
