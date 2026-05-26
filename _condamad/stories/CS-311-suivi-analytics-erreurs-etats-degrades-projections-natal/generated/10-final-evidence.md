# Final Evidence - CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal

## Story status

- Validation outcome: PASS
- Final status: done
- Story key: `CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal`
- Source story: `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/00-story.md`
- Source brief: `_story_briefs/cs-311-suivi-analytics-erreurs-etats-degrades-projections-natal.md`
- Capsule path: `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal`
- Registry status: `done`

## Preflight

- Repository root: `C:\dev\horoscope_front`.
- Story registry row matched `CS-311`, target `Path`, and source brief.
- Resume logs under `_condamad/codex-runs` showed prior story writing/review/alignment phases.
- Existing implementation evidence was present with status `ready-to-review`.
- Fresh implementation review found two behavioral analytics issues and one repository documentation issue; all were fixed.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status is `done`. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Existing capsule file retained. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Existing traceability retained. |
| `generated/04-target-files.md` | yes | yes | PASS | Existing target map retained. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Existing validation plan retained. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Existing guardrail evidence retained. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Refreshed after implementation review/fix. |
| `generated/11-code-review.md` | yes | yes | PASS | Fresh implementation review verdict is `CLEAN`. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | `evidence/event-catalog.json` lists seven projection events. | Catalog reviewed after fix. | PASS |
| AC2 | `useAnalytics.ts` remains the analytics owner; orchestration calls `useAnalytics`. | Direct provider scan PASS; targeted Vitest PASS. | PASS |
| AC3 | Normal public projections emit `natal_projection_success`. | `natalInterpretation.test.tsx` success assertions PASS. | PASS |
| AC4 | Non-403 errors emit `natal_projection_api_error` with `public_error_code`. | API error test PASS. | PASS |
| AC5 | 403 `ApiError` emits `natal_projection_entitlement_denied`. | Entitlement test PASS. | PASS |
| AC6 | Missing chart data and empty projections emit `natal_projection_empty`. | Empty and missing-data tests PASS. | PASS |
| AC7 | Degraded no-time payloads emit `natal_projection_degraded` and not success. | Degraded test PASS. | PASS |
| AC8 | User retry emits one retry event for the projection in API error. | Retry test PASS. | PASS |
| AC9 | `sanitizeAnalyticsProps` drops sensitive keys before provider emission. | Redaction test PASS; sensitive scan contextualized. | PASS |
| AC10 | Observability limits are documented. | `observability-limits.md` present. | PASS |
| AC11 | Frontend quality gate passed. | `pnpm lint`, targeted Vitest, full Vitest, and static guards PASS. | PASS |
| AC12 | Evidence and tracker persisted. | Story validation and strict lint PASS after status update. | PASS |

## Implementation

- Added seven `/natal` projection analytics event names to the existing `useAnalytics` owner.
- Added central analytics payload redaction for sensitive keys before provider/noop emission.
- Instrumented projection started, success, API error, entitlement denied, empty, degraded-without-time, and user retry from `NatalInterpretation.tsx`.
- Fixed review finding: degraded-without-time no longer also emits `natal_projection_success`.
- Fixed review finding: retry analytics now tracks only projections currently in non-entitlement error, while still refetching all projection queries.
- Added repository-required French file comment and public helper docstrings in `useAnalytics.ts`.
- Kept projection API, backend entitlement decisions, projection display ownership, styles, package scripts, and dependencies unchanged.

## Files changed

- `frontend/src/hooks/useAnalytics.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/tests/useAnalytics.test.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/**`
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- `frontend/src/tests/useAnalytics.test.tsx`: redaction test for sensitive analytics keys.
- `frontend/src/tests/natalInterpretation.test.tsx`: projection analytics assertions for success, started, API error, entitlement denial, empty, degraded no-time, missing birth-data, and retry.
- Review-fix assertions prove degraded-without-time does not also emit success and retry analytics does not include unaffected projections.

## Commands run

| Command | Working directory | Result | Notes |
|---|---|---|---|
| `git status --short` | repo root | PASS | Resume/worktree preflight. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi` | `frontend` | PASS | 4 files, 54 tests. |
| `pnpm lint` | `frontend` | PASS | TypeScript lint/typecheck script passed. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run` | `frontend` | PASS | 116 files; 1276 passed; 8 skipped. |
| `rg -n 'plausible\|_paq\.push\|console\.debug\(' frontend\src\features frontend\src\components frontend\src\api` | repo root | PASS | Exit 1 means no matches. |
| `rg -n "fetch\(.*/v1/astrology/projections\|axios\(.*/v1/astrology/projections" frontend\src` | repo root | PASS | Exit 1 means no matches. |
| `rg -n "style=" frontend\src\features\natal-chart frontend\src\components\natal-interpretation -g "*.tsx"` | repo root | PASS | Exit 1 means no matches. |
| `rg -n "birth_date\|birth_time\|birth_place\|latitude\|longitude\|provider_response\|raw_runtime\|replay_snapshot\|prompt\|api_key\|password" src` | `frontend` | PASS_WITH_CONTEXT | Existing repository hits documented in `sensitive-key-scan.txt`. |
| `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5173 -TimeoutSec 5` | repo root | PASS | Existing local Vite server returned HTTP 200. |
| `condamad_story_validate.py 00-story.md` | repo root, venv active | PASS | Story status change valid. |
| `condamad_story_lint.py --strict 00-story.md` | repo root, venv active | PASS | Story lint valid. |
| `condamad_validate.py <CS-311 capsule>` | repo root, venv active | PASS | Capsule closure validation. |

## Commands skipped or blocked

- `pnpm test:e2e`: NOT_RUN. No route, auth, navigation, CSS, or browser-only behavior changed; Vitest, lint, static guards, and prior local startup cover the story surface.
- Backend pytest: NOT_RUN. No backend file, route, entitlement, DB, migration, or API contract changed.

## DRY / No Legacy evidence

- One analytics owner remains active: `frontend/src/hooks/useAnalytics.ts`.
- No duplicate analytics adapter, vendor call, legacy import, shim, alias, silent fallback, or dependency was added.
- Retry tracking is emitted only from the user retry action for projections in non-entitlement error.
- Frontend analytics does not change backend entitlement outcomes or projection API behavior.
- `RG-047` inline-style guard passed for touched natal TSX surfaces.

## Diff review

- Fresh review artifact: `generated/11-code-review.md`.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`, `frontend/src/api/astrologyProjections.ts`, `frontend/package.json`, `backend/**`, `docs/**`, and `_condamad/stories/regression-guardrails.md` were not modified.

## Final worktree status

- `git status --short` was checked after review/fix and before final response.
- Remaining modified files are the scoped CS-311 implementation, tests, story capsule, review evidence, and tracker row.

## Remaining risks

- None identified.

## Suggested reviewer focus

- Confirm the corrected analytics semantics: degraded-without-time is not double-counted as success, and retry analytics only tracks projections in API error.

## Feedback loop routing

- no-propagation: findings were local to CS-311 implementation and evidence.
