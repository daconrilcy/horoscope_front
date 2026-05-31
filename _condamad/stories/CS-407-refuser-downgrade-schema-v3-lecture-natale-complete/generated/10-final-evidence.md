# Final Evidence — CS-407-refuser-downgrade-schema-v3-lecture-natale-complete

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-407-refuser-downgrade-schema-v3-lecture-natale-complete
- Source story: `_condamad/stories/CS-407-refuser-downgrade-schema-v3-lecture-natale-complete/00-story.md`
- Source brief: `_story_briefs/cs-407-refuser-downgrade-schema-v3-lecture-natale-complete.md`
- Capsule path: `_condamad/stories/CS-407-refuser-downgrade-schema-v3-lecture-natale-complete`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `_condamad/run-state.json` dirty before implementation; left untouched.
- Story tracker: CS-407 row path and source brief matched the requested story and brief.
- CS-401 dependency: final evidence found with PASS review-ready state for `CS-401-refuser-padding-sources-vides`.
- Guardrails applied: `RG-150`, `RG-152`, `RG-155`, `RG-157`, `RG-022`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status synchronized to `ready-to-review`. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Prepared by CONDAMAD helper. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC14 classified. |
| `generated/04-target-files.md` | yes | yes | PASS | Prepared by CONDAMAD helper. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Validation commands executed or superseded by `--long` where required. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | No shim, alias or fallback downgrade added. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## Implementation

- Replaced the non-fallback complete V3 failure downgrade with an audit-only `natal_complete_schema_mismatch` rejection.
- Preserved `AstroResponseV3`, `AstroErrorResponseV3`, `free_short`, and explicit gateway fallback behavior.
- Added a focused schema guard test file and updated the legacy unit test that expected `complete -> v2`.
- Persisted evidence in `_condamad/stories/CS-407-refuser-downgrade-schema-v3-lecture-natale-complete/evidence/`.

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Non-fallback complete V2/V1 output rejected by schema guard. | Schema guard unit test. | PASS | |
| AC2 | Cause is `natal_complete_schema_mismatch`. | Schema guard unit test. | PASS | |
| AC3 | `request_id` stored in rejection reason and validation context. | Schema guard and updated legacy unit tests. | PASS | |
| AC4 | Rejected rows use audit-only workflow. | Public boundary integration test with `--long`. | PASS | |
| AC5 | `AstroErrorResponseV3` remains accepted. | Schema guard unit test. | PASS | |
| AC6 | Valid `AstroResponseV3` remains accepted. | Schema guard and stored-payload tests. | PASS | |
| AC7 | Explicit gateway fallback remains observable. | Schema guard unit test. | PASS | |
| AC8 | Downgrade constructors absent from bounded generation path. | Bounded anti-downgrade scan. | PASS | |
| AC9 | Narrative audit workflow is reused. | Stored-payload and updated legacy unit tests. | PASS | |
| AC10 | Rejected V2/V1 payloads are excluded from accepted persistence. | Stored-payload tests. | PASS | |
| AC11 | Quota remains acceptance-scoped. | Quota-on-acceptance tests. | PASS | |
| AC12 | `free_short` remains on the existing short path. | Schema guard unit test. | PASS | |
| AC13 | No public route/schema change. | Runtime OpenAPI introspection. | PASS | |
| AC14 | Evidence artifacts persisted. | Capsule final validation. | PASS | |

## Files changed

- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/unit/test_natal_interpretation_service_v3_schema_guard.py`
- `backend/app/tests/unit/test_natal_interpretation_service_v2.py`
- `_condamad/stories/CS-407-refuser-downgrade-schema-v3-lecture-natale-complete/**`
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- Added `backend/tests/unit/test_natal_interpretation_service_v3_schema_guard.py`.
- Updated `backend/app/tests/unit/test_natal_interpretation_service_v2.py` to assert the new mismatch rejection contract.

## Commands run

| Command | Working directory | Result |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py ... --story-key CS-407-refuser-downgrade-schema-v3-lecture-natale-complete` | repo root | PASS |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-407-refuser-downgrade-schema-v3-lecture-natale-complete` | repo root | PASS |
| `ruff format app\services\llm_generation\natal\interpretation_service.py tests\unit\test_natal_interpretation_service_v3_schema_guard.py app\tests\unit\test_natal_interpretation_service_v2.py` | `backend` | PASS |
| `ruff check .` | `backend` | PASS |
| `python -B -m pytest -q tests\unit\test_natal_interpretation_service_v3_schema_guard.py --tb=short` | `backend` | PASS, 5 passed |
| `python -B -m pytest -q tests\unit\test_natal_interpretation_stored_payload.py --tb=short` | `backend` | PASS, 10 passed |
| `python -B -m pytest -q tests\integration\test_natal_interpretation_rejected_public_boundary.py --tb=short --long` | `backend` | PASS, 8 passed |
| `python -B -m pytest -q tests\unit\test_natal_chart_long_quota_on_acceptance.py --tb=short` | `backend` | PASS, 4 passed |
| `python -B -m pytest -q app\tests\unit\test_natal_interpretation_service_v2.py::TestNatalInterpretationServiceSchemaVersion::test_complete_level_rejects_local_v2_downgrade --tb=short` | `backend` | PASS |
| `rg -n "AstroResponseV2\(\*\*full_output\)|AstroResponseV1\(\*\*full_output\)" app\services\llm_generation\natal\interpretation_service.py` | `backend` | PASS, exit 1 means no matches |
| `python -B -c "from app.main import app; schema=app.openapi(); ..."` | `backend` | PASS |
| `python -B -m pytest -q --tb=short` | `backend` | PASS, 3572 passed, 2 skipped, 1250 deselected |

## Commands skipped or blocked

- Initial integration command without `--long` selected 0 tests because `backend/conftest.py` deselects `tests/integration/**` by default. Re-run with `--long` passed.

## DRY / No Legacy evidence

- No shim, alias, compatibility route, fallback route, or duplicate accepted path was added.
- V1/V2 schema classes remain only for historical/short/fallback surfaces already owning them.
- The bounded anti-downgrade scan has zero matches in `interpretation_service.py`.

## Diff review

- `git diff --stat` reviewed for story surface.
- Existing unrelated dirty file: `_condamad/run-state.json`.
- Line-ending warnings reported by Git for modified Python files; no content issue found.

## Final worktree status

- Story changes are uncommitted and review-ready.
- `_condamad/run-state.json` remains a pre-existing unrelated modification.

## Remaining risks

- No known implementation risk after targeted and fast-suite validation.

## Suggested reviewer focus

- Verify the audit payload shape for `natal_complete_schema_mismatch` and the decision to keep gateway fallback V1 only when `GatewayMeta.fallback_triggered=True`.
