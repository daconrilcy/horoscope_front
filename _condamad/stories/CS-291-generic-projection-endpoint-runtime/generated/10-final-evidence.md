# CS-291 Final Evidence

## Story status

- Story key: `CS-291-generic-projection-endpoint-runtime`
- Status: `done`
- Source story: `_condamad/stories/CS-291-generic-projection-endpoint-runtime/00-story.md`
- Source brief: `_story_briefs/cs-291-implement-generic-projection-endpoint.md`
- Story registry row: updated from `ready-to-review` to `done` on `2026-05-25` after clean implementation review.

## Preflight

- `.git` exists; initial `git status --short` showed a large pre-existing dirty worktree unrelated to CS-291.
- `story-status.md` row for CS-291 matched the target story path and brief source.
- Required generated capsule files were missing before implementation, so the target capsule was repaired.
- Applicable repository instructions from `AGENTS.md` were followed, including Python venv activation.

## Capsule validation

- `condamad_prepare.py --repair-generated-only _condamad\stories\CS-291-generic-projection-endpoint-runtime --root .`: PASS.
- `condamad_validate.py _condamad\stories\CS-291-generic-projection-endpoint-runtime`: PASS after final evidence format correction.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Route and registry registration files. | Runtime route assertion and OpenAPI route test. | PASS |
| AC2 | Public request/response schemas. | `app.openapi()` assertion and `openapi-after.json`. | PASS |
| AC3 | `ProjectionEndpointService._resolve_existing_chart`. | API chart_id test and service unit tests. | PASS |
| AC4 | `ProjectionEndpointService._calculate_chart`. | API birth_input test. | PASS |
| AC5 | `_build_projection` dispatches delivered builders directly. | Service unit dispatch test. | PASS |
| AC6 | `SUPPORTED_PROJECTION_TYPES` allowlist and controlled 403. | Authorization API test and endpoint-source scan. | PASS |
| AC7 | Entitlement resolver plan source and schema `extra=forbid`. | Service unit plan and client-plan rejection tests. | PASS |
| AC8 | `ProjectionPersistenceService.persist_from_builder` call. | Persistence API test and service unit assertion. | PASS |
| AC9 | CS-291 operation references public contracts only. | OpenAPI operation forbidden-token test. | PASS |
| AC10 | Only canonical route registered. | Runtime route assertion and forbidden route scan. | PASS |
| AC11 | CS-291 evidence folder populated. | Evidence file presence and capsule validation. | PASS |

## Files changed

- `backend/app/api/v1/routers/public/projections.py`
- `backend/app/api/v1/routers/registry.py`
- `backend/app/services/api_contracts/public/projections.py`
- `backend/app/services/projections/__init__.py`
- `backend/app/services/projections/projection_endpoint_service.py`
- `backend/tests/api/test_projection_endpoint.py`
- `backend/tests/api/test_projection_authorization.py`
- `backend/tests/api/test_projection_persistence_endpoint.py`
- `backend/tests/api/test_projection_openapi.py`
- `backend/tests/unit/services/test_projection_endpoint_service.py`
- `backend/tests/unit/domain/astrology/test_structured_facts_v1_builder.py`
- `backend/tests/unit/domain/astrology/test_beginner_summary_v1_builder.py`
- `backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/converge-api-v1-route-architecture/router-root-audit.md`
- `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md`
- `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/openapi-before.json`
- `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/openapi-after.json`
- `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/validation.txt`
- `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/source-checklist.md`
- `_condamad/stories/CS-291-generic-projection-endpoint-runtime/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-291-generic-projection-endpoint-runtime/generated/09-dev-log.md`
- `_condamad/stories/CS-291-generic-projection-endpoint-runtime/generated/10-final-evidence.md`
- `_condamad/stories/story-status.md`

## Files deleted

- None.

## Tests added or updated

- `backend/tests/api/test_projection_endpoint.py`
- `backend/tests/api/test_projection_authorization.py`
- `backend/tests/api/test_projection_persistence_endpoint.py`
- `backend/tests/api/test_projection_openapi.py`
- `backend/tests/unit/services/test_projection_endpoint_service.py`
- `backend/tests/unit/domain/astrology/test_structured_facts_v1_builder.py`
- `backend/tests/unit/domain/astrology/test_beginner_summary_v1_builder.py`
- `backend/tests/unit/domain/astrology/test_client_interpretation_projection_v1_builder.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`

## Commands run

- `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --repair-generated-only _condamad\stories\CS-291-generic-projection-endpoint-runtime --root .`: PASS.
- `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-291-generic-projection-endpoint-runtime`: PASS after evidence format correction.
- `ruff format <changed python files>`: PASS.
- `python -B -m pytest -q tests/api/test_projection_endpoint.py tests/api/test_projection_authorization.py tests/api/test_projection_persistence_endpoint.py tests/api/test_projection_openapi.py tests/unit/services/test_projection_endpoint_service.py --tb=short`: PASS, 12 passed.
- `ruff check .`: PASS.
- Runtime `app.routes` assertion for `/v1/astrology/projections`: PASS.
- Runtime `app.openapi()` assertion for `/v1/astrology/projections`: PASS.
- Forbidden alternate route `rg` scan: PASS, no matches.
- `python -B -m pytest -q`: PASS, 3378 passed, 1 skipped, 1211 deselected.
- API architecture guard subset: PASS, 3 passed.
- Targeted projection guard subset: PASS, 57 passed.
- Forbidden internal surface endpoint-source `rg` scan: PASS, no matches.
- Uvicorn local startup on `127.0.0.1:8011` with `/openapi.json`: PASS.
- Uvicorn local startup on `127.0.0.1:8012` with `/openapi.json`: PASS.
- Scoped `git diff --check` on tracked CS-291 files: PASS.

## Commands skipped or blocked

- Frontend checks: not applicable; no frontend files were touched.

## DRY / No Legacy evidence

- No alternate projection route path was added.
- No B2B, admin, internal, frontend, migration, prompt/provider or generated client surface was touched.
- Public builders are reused directly; no duplicate projection builder was introduced.
- Optional persistence goes through `ProjectionPersistenceService.persist_from_builder`; no route-local persistence write was added.

## Diff review

- Scoped diff review was performed for CS-291 paths.
- The worktree had many pre-existing unrelated dirty files; CS-291 review scope is limited to the files listed in this evidence.
- OpenAPI before/after artifacts show the new public command route is present after implementation.
- Implementation review/fix cycle found and resolved stale projection guard tests, service HTTP mapping, router audit evidence and SQL boundary evidence.

## Final worktree status

- `.git` exists.
- Final worktree remains dirty because of pre-existing unrelated changes plus CS-291 changes.
- CS-291 status row is synchronized to `done`.

## Remaining risks

- Existing repository worktree contained many unrelated dirty files before CS-291; review should scope diffs to the changed files listed above.
- No residual CS-291 implementation risk identified after fresh full pytest and guardrail review.

## Suggested reviewer focus

- None; fresh implementation review is clean.

## Feedback loop routing

- no-propagation: validation corrections were local evidence/test-scope issues, now fixed in CS-291 artifacts.
