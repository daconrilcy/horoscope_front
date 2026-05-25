# CS-297 Implementation Review

Verdict: CLEAN
Review date: 2026-05-25
Review type: implementation review and fix loop.

## Scope Reviewed

- Story: `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/00-story.md`.
- Source brief: `_story_briefs/cs-297-expose-internal-admin-replay-snapshot-v1-api.md`.
- Tracker row: `_condamad/stories/story-status.md`, row `CS-297`.
- Backend route and contracts:
  - `backend/app/api/v1/routers/admin/audit.py`
  - `backend/app/services/api_contracts/admin/audit.py`
  - `backend/app/services/replay_snapshot_v1_service.py`
- Tests and guardrails:
  - `backend/tests/api/admin/test_replay_snapshot_v1_api.py`
  - `backend/tests/architecture/test_admin_replay_snapshot_v1_public_exposure.py`
  - `backend/tests/unit/test_admin_endpoint_segmentation_contract.py`
  - `backend/tests/unit/test_replay_snapshot_v1_service_ownership.py`
- Evidence:
  - `evidence/openapi-before.json`
  - `evidence/openapi-after.json`
  - `evidence/routes-before.txt`
  - `evidence/routes-after.txt`
  - `evidence/access-control.txt`
  - `evidence/validation.txt`

## Iteration 1 Findings

- Finding 1: the implementation evidence referenced architecture coverage, but
  `backend/tests/architecture/test_admin_replay_snapshot_v1_public_exposure.py` was missing.
- Finding 2: `generated/11-code-review.md` still contained a pre-implementation drafting review, not an implementation review.
- Finding 3: the story status was inconsistent across artifacts: tracker `ready-to-review`, story file `ready-to-dev`.
- Finding 4: `evidence/access-control.txt` was required by the story but absent.
- Finding 5: the static `rg` validation in the story was too broad and matched the allowed admin route suffix.

## Fixes Applied

- Added the architecture guardrail test for runtime paths, OpenAPI methods and frontend/public-router absence.
- Added access-control evidence for unauthenticated, user and support denial.
- Corrected the static scan so runtime checks own the bare root path and `rg` owns public/client/support/API prefixes.
- Refreshed target-file, validation and final review evidence.
- Updated story and tracker status to `done` after fresh passing validation.

## Acceptance Criteria Review

- AC1/AC2: PASS. Runtime and OpenAPI expose exactly the admin audit replay snapshot paths.
- AC3: PASS. Metadata responses are contract-shaped and tested against forbidden sensitive fields.
- AC4: PASS. Replay attempt delegates to `ReplaySnapshotV1Service.start_replay_attempt`, returns `202` and commits audit metadata.
- AC5: PASS. Manual purge delegates to `ReplaySnapshotV1Service.purge_snapshot`, commits and returns `204`.
- AC6: PASS. Missing auth returns `401`; user and support roles return `403`; denied calls do not reach the replay service.
- AC7/AC8/AC9: PASS. Missing, expired and already purged states map to stable `404`/`410` errors.
- AC10: PASS. Runtime and static guards prove no public, support, client, frontend or root replay path.
- AC11: PASS. OpenAPI, route inventory, access-control and validation evidence are persisted.

## Validation Results

- PASS: `ruff format tests\architecture\test_admin_replay_snapshot_v1_public_exposure.py`.
- PASS: `ruff check tests\architecture\test_admin_replay_snapshot_v1_public_exposure.py`.
- PASS: `python -B -m pytest -q tests\api\admin\test_replay_snapshot_v1_api.py tests\architecture\test_admin_replay_snapshot_v1_public_exposure.py --tb=short` (`11 passed`).
- PASS: `ruff check .`.
- PASS: `python -B -m pytest -q tests\api\admin tests\architecture --tb=short` (`95 passed`).
- PASS: `python -B -m pytest -q --tb=short` (`3412 passed, 1 skipped, 1216 deselected`).
- PASS: CONDAMAD story validate and strict lint.
- PASS: runtime OpenAPI and `app.routes` guards for admin-only replay exposure.
- PASS: static negative scan for public/client/support/API replay paths.

## Fresh Review Verdict

CLEAN. No actionable implementation issue remains after iteration 1 fixes.

## Propagation Decision

No-propagation: findings were local CS-297 evidence and guardrail closure issues.

## Residual Risk

Aucun risque restant identifie.
