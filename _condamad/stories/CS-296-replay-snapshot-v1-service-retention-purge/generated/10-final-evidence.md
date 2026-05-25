# CS-296 final evidence

## Story status

- Story key: `CS-296-replay-snapshot-v1-service-retention-purge`
- Status: `done`
- Source: `_story_briefs/cs-296-implement-replay-snapshot-v1-service-retention-purge.md`
- Tracker row: `_condamad/stories/story-status.md` updated to `done` after clean implementation review.

## Preflight

- Story key: `CS-296-replay-snapshot-v1-service-retention-purge`
- Status: `done`
- Source: `_story_briefs/cs-296-implement-replay-snapshot-v1-service-retention-purge.md`
- Tracker row matched `CS-296`, path and source brief before implementation.
- Pre-existing CS-295/backend dirty worktree was present and not reverted.

## Capsule validation

- Required generated files were initially missing.
- `condamad_prepare.py` created a temporary `cs-296` capsule; generated files were copied to the canonical capsule and temporary capsule removed.
- `condamad_validate.py _condamad\stories\CS-296-replay-snapshot-v1-service-retention-purge`: PASS before implementation evidence updates.
- Final evidence was reformatted to satisfy the capsule contract.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Canonical `ReplaySnapshotV1Service`; observability/replay delegate decisions; operations filter `replay_snapshot_v1` rows | Ownership pytest | PASS |
| AC2 | `create_snapshot` retention 30 days | Retention pytest | PASS |
| AC3 | expired metadata returns `expired` | Metadata pytest | PASS |
| AC4 | controlled metadata states | Metadata pytest | PASS |
| AC5 | automatic purge deletes expired `replay_snapshot_v1` rows only and keeps non-v1 rows untouched | Integration purge pytest | PASS |
| AC6 | manual purge outcomes `success/not_found/expired/already_purged` | Manual purge pytest | PASS |
| AC7 | call logs/releases unchanged and no narrative/diagnostics service references | Non-cascade pytest | PASS |
| AC8 | Manual and automatic purge audit details are bounded; AuditService events stay payload-free | Audit pytest and integration purge pytest | PASS |
| AC9 | no API/frontend/OpenAPI/routes exposure | Runtime guards | PASS |
| AC10 | evidence files, traceability and story-status updated | Capsule validation | PASS |

## Files changed

Application:
- `backend/app/services/replay_snapshot_v1_service.py`
- `backend/app/domain/audit/safe_details.py`
- `backend/app/domain/llm/runtime/observability_service.py`
- `backend/app/ops/llm/replay_service.py`

Architecture guards:
- `backend/app/tests/unit/test_backend_db_test_harness.py`
- `backend/app/tests/unit/test_backend_services_structure_guard.py`
- `backend/tests/unit/test_replay_snapshot_v1_ownership.py`

Tests:
- `backend/tests/unit/test_replay_snapshot_v1_service_ownership.py`
- `backend/tests/unit/test_replay_snapshot_v1_service_retention.py`
- `backend/tests/unit/test_replay_snapshot_v1_service_metadata.py`
- `backend/tests/unit/test_replay_snapshot_v1_service_manual_purge.py`
- `backend/tests/unit/test_replay_snapshot_v1_service_audit.py`
- `backend/tests/integration/test_replay_snapshot_v1_service_purge.py`
- `backend/tests/integration/test_replay_snapshot_v1_service_non_cascade.py`

Evidence:
- `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/source-checklist.md`
- `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/service-ownership.txt`
- `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/purge-non-cascade.txt`
- `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/runtime-surface-status.txt`
- `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/evidence/validation.txt`

## Files deleted

- No application or test files deleted.
- Temporary generated capsule `_condamad/stories/cs-296` deleted after copying generated files to the canonical capsule.

## Tests added or updated

- Added five unit tests for service ownership, retention, metadata, manual purge and audit.
- Added two integration tests for automatic purge and non-cascade.
- Updated one CS-295 ownership guard to expect the CS-296 service owner.
- Updated existing backend architecture allowlists for the approved service and classified SQLite secondary test factories.

## Commands run

- `ruff format <changed python files>`: PASS.
- `ruff check <changed python files>`: PASS.
- `ruff check .`: PASS.
- Targeted CS-296 pytest suite after review fixes: PASS, 12 passed, 2 deselected.
- Nearby CS-295 replay regression suite: PASS, 9 passed, 1 deselected.
- `python -B -m pytest -q backend\tests\unit backend\tests\integration --tb=short`: PASS, 806 passed, 215 deselected.
- `python -B -m pytest -q --tb=short`: PASS, 3309 passed, 1 skipped, 1216 deselected.
- `app.openapi()` replay_snapshot_v1 absence: PASS.
- `app.routes` replay_snapshot_v1 absence: PASS.
- `rg -n "replay_snapshot_v1" backend\app\api frontend\src`: PASS: no matches.
- `condamad_story_validate.py` target story: PASS after final status update.
- `condamad_story_lint.py --strict` target story: PASS after final status update.

## Commands skipped or blocked

- No required validation skipped.
- A mistaken full pytest attempt was launched from `backend/` with a missing relative venv activation; it was superseded by the final root-run full pytest PASS.

## DRY / No Legacy evidence

- One canonical lifecycle service owns create, metadata read, automatic purge and manual purge.
- Service operations reject non-v1 snapshot rows before metadata read or purge.
- No public API, frontend, generated client or OpenAPI route was added.
- No duplicate replay snapshot table or model was added.
- Existing CS-295 `LlmReplaySnapshotModel` remains the storage owner.
- Manual purge uses tombstone metadata to support `already_purged`; automatic purge physically deletes only expired `replay_snapshot_v1` rows.
- Automatic purge returns `ReplaySnapshotBulkPurgeAuditDetails` and can record a bounded `AuditService` event when a `request_id` is supplied.

## Review/fix iterations

- Iteration 1 findings fixed:
  - Service operations did not restrict reads and purge to `snapshot_type == replay_snapshot_v1`.
  - `purge_expired` returned no bounded automatic purge audit details.
- Fresh re-review after fixes: CLEAN.

## Diff review

- Scoped diff reviewed with `git diff --stat -- <story paths>` and `git diff --name-only -- <story paths>`.
- Expected story files only for CS-296 plus existing guard updates needed by the broader test suite.
- Pre-existing CS-295 changes remain in worktree and are outside this story.

## Final worktree status

- `.git` present.
- Final `git status --short` includes pre-existing CS-295 changes plus CS-296 files and updates.
- New CS-296 files are untracked until the user/orchestrator stages them.

## Remaining risks

- No scheduled job was added; story scoped only internal service methods.
- Manual purge has no public route by design.

## Feedback loop routing

- No propagation to AGENTS or guardrail registry required. The validation mistake is recorded in evidence; no reusable project rule change is needed because AGENTS already requires root venv activation discipline.
- Review/fix findings were local to CS-296 implementation and tests; no reusable rule propagation required.
