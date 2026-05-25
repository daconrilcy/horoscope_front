# Final Evidence - CS-298

## Preflight
- Repository root: `C:\dev\horoscope_front`.
- `.git`: present.
- Initial worktree: dirty with existing CS-295/CS-296/CS-297 replay snapshot changes; preserved.
- Story-status row verified for `CS-298` path and source brief before implementation.

## Story status
- Status: `done`.
- Source story: `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/00-story.md`.
- Tracker row: `_condamad/stories/story-status.md` verified as `done` with the source brief path on 2026-05-25.

## Capsule validation
- Capsule was missing required generated files.
- Repaired with `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --root . --repair-generated-only _condamad\stories\CS-298-replay-snapshot-v1-execution-audit`.
- PASS: `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-298-replay-snapshot-v1-execution-audit`.

## AC validation
| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Metadata GET records `replay_snapshot_v1.metadata_read` and returns audit event id. | API/unit tests and full suite PASS. | PASS |
| AC2 | Admin replay attempts and real `replay()` execution record success and failed audit events. | Unit tests and full suite PASS. | PASS |
| AC3 | Purge records success and failed audit events. | API/unit tests and full suite PASS. | PASS |
| AC4 | Expired, purged, missing and incomplete snapshots are refused before payload replay. | Unit tests and full suite PASS. | PASS |
| AC5 | Audit details are bounded and tests reject forbidden fields. | Non-leakage tests and scoped scan PASS_WITH_CLASSIFIED_HITS. | PASS |
| AC6 | Runtime and OpenAPI replay paths stay under admin audit namespace. | `app.routes`, `app.openapi()` and API tests PASS. | PASS |
| AC7 | AST guard blocks route-level provider execution and validates snapshot check ordering. | Architecture test PASS. | PASS |
| AC8 | Reproducibility note persisted. | Evidence file present. | PASS |
| AC9 | Evidence artifacts persisted under the CS-298 capsule. | Capsule validation PASS. | PASS |

## Files changed
- `backend/app/domain/audit/safe_details.py`
- `backend/app/services/replay_snapshot_v1_service.py`
- `backend/app/api/v1/routers/admin/audit.py`
- `backend/app/services/api_contracts/admin/audit.py`
- `backend/tests/api/admin/test_replay_snapshot_v1_api.py`
- `backend/tests/unit/test_replay_snapshot_v1_service_audit.py`
- `backend/app/tests/unit/test_backend_db_test_harness.py`
- `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/00-story.md`
- `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/generated/*`
- `_condamad/stories/CS-298-replay-snapshot-v1-execution-audit/evidence/*`

## Files deleted
- none.

## Tests added or updated
- Added `backend/tests/unit/test_replay_snapshot_v1_execution_audit.py`.
- Added `backend/tests/architecture/test_replay_snapshot_v1_execution_boundary.py`.
- Updated `backend/tests/unit/test_replay_snapshot_v1_execution_audit.py` during review/fix to prove real replay execution audit success and provider failure.
- Updated API/admin replay snapshot tests for metadata audit commits.
- Updated existing purge audit test for the CS-298 activity audit DTO.
- Updated exact architecture allowlists for API SQL and SQLite memory factories.

## Commands run
- PASS: `ruff format` on modified Python files.
- PASS: `ruff check .` from `backend`.
- PASS: targeted replay snapshot tests -> 23 passed.
- PASS: `python -B -m pytest -q --tb=short` from `backend` -> 3419 passed, 1 skipped, 1216 deselected.
- PASS review/fix: `ruff format .` from `backend` -> 1684 files left unchanged.
- PASS review/fix: `ruff check .` from `backend`.
- PASS review/fix: targeted CS-298/API/architecture tests -> 18 passed.
- PASS review/fix: `python -B -m pytest -q tests\unit tests\integration tests\api\admin --tb=short` from `backend` -> 828 passed, 215 deselected.
- PASS review/fix: `python -B -m pytest -q --tb=short` from `backend` -> 3421 passed, 1 skipped, 1216 deselected.
- PASS: OpenAPI admin-only replay path check.
- PASS: runtime absence check for `/replay_snapshot_v1`.
- PASS review/fix: app import/startup smoke check.
- PASS: `git diff --check`.
- PASS_WITH_CLASSIFIED_HITS: scoped sensitive scan found only tombstone `payload_enc = None` and existing masked audit export email fields.

## Commands skipped or blocked
- none.

## DRY / No Legacy evidence
- No public/support/B2B/frontend route added.
- No compatibility shim, alias, fallback path or duplicate provider executor added.
- Audit persistence remains through `AuditService.record_event`.
- Replay execution remains owned by `backend/app/ops/llm/replay_service.py`.
- Admin route delegates business rules to `ReplaySnapshotV1Service`.

## Diff review
- Reviewed scoped changes and guard failures from full suite.
- First full suite failure was limited to exact architecture allowlists; fixed and full suite reran green.
- Review/fix iteration 1 found that the real `backend/app/ops/llm/replay_service.py` execution path validated snapshots but did not record a
  `replay_snapshot_v1.replay_attempt` audit event around provider success or failure.
- Fixed by recording bounded real execution audit events through `AuditService.record_event`, preserving snapshot refusal before provider execution,
  and allowing only operational replay diff keys in audit sanitization.

## Final worktree status
- Worktree remains dirty.
- CS-298 changes are present alongside pre-existing CS-295/CS-296/CS-297 replay snapshot changes.
- No unrelated user changes were reverted.

## Remaining risks
- Aucun risque restant identifie.

## Suggested reviewer focus
- Final clean review already verified the real `replay()` execution success and provider failure audit path.
