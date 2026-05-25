# Final Evidence — CS-266-openapi-internal-public-exposure-guards

## Story status

- Validation outcome: passed
- Ready for review: yes
- Story key: CS-266-openapi-internal-public-exposure-guards
- Source story: `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md`
- Capsule path: `_condamad/stories/CS-266-openapi-internal-public-exposure-guards`
- Tracker status: `done`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story/status alignment: `CS-266` row matched the requested story path and source brief.
- Initial `git status --short`: repository dirty before this story; unrelated CS-256..CS-265 and backend projection files were already modified/untracked.
- AGENTS.md considered: root `AGENTS.md` from prompt and workspace.
- Capsule generated/repaired: yes, via `condamad_prepare.py --repair-generated-only`.
- Capsule validation before implementation: PASS.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Story source preserved. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Repaired by capsule helper. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Updated with AC1-AC7 evidence. |
| `generated/04-target-files.md` | yes | yes | PASS | Present. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Present. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Present. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Updated for review handoff. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `test_api_contract_neutrality.py` serializes `app.openapi()` and rejects the exact internal projection token set. | Architecture pytest PASS; direct OpenAPI token command PASS. | PASS | Runtime OpenAPI is the source of truth. |
| AC2 | `test_api_openapi_contract.py` uses `TestClient` on protected `admin`, `ops`, and `b2b` samples. | Integration pytest with `--long` PASS. | PASS | `/v1/internal` is absent, so no unprotected internal mount exists. |
| AC3 | Runtime route inventory maps public prefixes and protected families from `app.routes`. | Integration pytest PASS; `/openapi.json` route command PASS. | PASS | No new route was added. |
| AC4 | OpenAPI before/after snapshots persisted under `evidence/`. | Snapshot comparison command PASS; before equals after. | PASS | Confirms no public API surface delta. |
| AC5 | Forbidden token guard is automated in pytest and public-surface `rg` scan. | Public router/API-contract scan returned no matches. | PASS | Broad backend scan contains expected internal implementation/doc/test hits, so it is not used as public exposure evidence. |
| AC6 | Added backend OpenAPI boundary doc and ownership-index entry. | Architecture doc assertion PASS; docs ownership test PASS. | PASS | Documentation is now guarded. |
| AC7 | Evidence artifacts and traceability updated. | `condamad_validate.py` PASS after evidence update. | PASS | Story registry synchronized. |

## Files changed

- `backend/tests/architecture/test_api_contract_neutrality.py`
- `backend/app/tests/integration/test_api_openapi_contract.py`
- `backend/docs/openapi-public-internal-boundary.md`
- `backend/docs/ownership-index.md`
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/generated/11-code-review.md`
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/evidence/openapi-before.json`
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/evidence/openapi-after.json`
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/evidence/validation.txt`
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/generated/10-final-evidence.md`
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- Added OpenAPI forbidden internal projection token guard in `backend/tests/architecture/test_api_contract_neutrality.py`.
- Added route inventory and unauthenticated protected-family checks in `backend/app/tests/integration/test_api_openapi_contract.py`.
- Existing docs ownership guard updated through `backend/docs/ownership-index.md`.

## Commands run

| Command | Working directory | Result | Evidence summary |
|---|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --repair-generated-only _condamad\stories\CS-266-openapi-internal-public-exposure-guards --root .` | repo root | PASS | Missing generated capsule files repaired. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-266-openapi-internal-public-exposure-guards` | repo root | PASS | Capsule valid before implementation. |
| `python -B -c "... app.openapi() ... openapi-before.json"` | `backend` | PASS | Baseline OpenAPI snapshot persisted. |
| `ruff format tests\architecture\test_api_contract_neutrality.py app\tests\integration\test_api_openapi_contract.py` | `backend` | PASS | Modified Python tests formatted. |
| `ruff check .` | `backend` | PASS | Ruff lint passed. |
| `python -B -m pytest -q tests\architecture\test_api_contract_neutrality.py --tb=short` | `backend` | PASS | 19 passed. |
| `python -B -m pytest -q app\tests\integration\test_api_openapi_contract.py --long --tb=short` | `backend` | PASS | 3 passed. |
| `python -B -m pytest -q tests\architecture\test_api_contract_neutrality.py app\tests\integration\test_api_openapi_contract.py --long --tb=short` | `backend` | PASS | 22 passed. |
| `python -B -m pytest -q app\tests\unit\test_backend_docs_ownership.py --tb=short` | `backend` | PASS | 3 passed. |
| `python -B -m pytest -q --tb=short` | `backend` | PASS | 3247 passed, 1 skipped, 1186 deselected. |
| `python -B -c "... assert '/openapi.json' in app.routes ..."` | `backend` | PASS | Runtime route inventory includes OpenAPI. |
| `python -B -c "... assert 'ChartObjectRuntimeData' not in app.openapi() ..."` | `backend` | PASS | Runtime OpenAPI token absence checked. |
| `rg -n <tokens> .\backend\app\api\v1\routers\public .\backend\app\services\api_contracts --glob "!admin/**" --glob "!ops/**" --glob "!b2b/**"` | repo root | PASS | Exit 1, no public-surface matches. |
| `python -B -c "... openapi-after.json ... assert before == after"` | `backend` | PASS | After snapshot persisted and equal to before. |

## Commands skipped or blocked

- Full integration suite with `--long` was not run; the story touches only OpenAPI contract guards and one targeted integration test file. The full fast backend suite passed without `--long`.

## DRY / No Legacy evidence

- No compatibility route, alias, fallback, shim, serializer, migration, or frontend path was added.
- Reused existing OpenAPI architecture and integration test owners instead of adding parallel guard modules.
- Public API behavior unchanged: OpenAPI before/after snapshots are identical.
- Public-surface forbidden-token scan has no matches.

## Diff review

- `git diff --stat -- <story paths>` reviewed.
- `git diff --check -- <story paths>` PASS.
- No unrelated files were intentionally modified; pre-existing dirty worktree remains outside this story.

## Final worktree status

- Story-owned changes are limited to backend OpenAPI tests/docs, CS-266 evidence, and the CS-266 status row.
- Existing unrelated dirty/untracked files from other CS stories and projection work remain present.

## Remaining risks

- Broad `rg` over all `backend` still finds forbidden tokens in internal domain code, guarded docs, and tests. This is expected because the story forbids public OpenAPI exposure, not internal implementation vocabulary.
- Protected-route assertions sample representative mounted families; they do not prove every historical admin endpoint has perfect authorization semantics.

## Suggested reviewer focus

- Review whether the representative protected route samples are sufficient for the current public/internal boundary, especially the intentionally absent `/v1/internal` family.

## Feedback loop routing

- no-propagation: the only validation failure was a local docs ownership index omission, fixed by adding the new document to the existing guard.
