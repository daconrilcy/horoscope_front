# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Admin replay snapshot routes are registered. | `backend/app/api/v1/routers/admin/audit.py` registers GET, POST replay-attempt and DELETE under `/v1/admin/audit/replay_snapshot_v1`. | `python -B -m pytest -q tests\api\admin\test_replay_snapshot_v1_api.py --tb=short`; `routes-after.txt`. | PASS |
| AC2 | OpenAPI exposes admin replay paths only. | Routes reuse existing admin audit router; no registry or public router added. | Runtime OpenAPI test in `test_replay_snapshot_v1_api.py`; `openapi-before.json` / `openapi-after.json`. | PASS |
| AC3 | Metadata response is redacted. | `AdminReplaySnapshotV1MetadataResponse` exposes metadata, version labels and provenance refs only. | API test checks forbidden fields absent: raw prompt, birth data, coordinates, direct identifiers, secrets, encrypted bytes. | PASS |
| AC4 | Replay attempt is controlled. | `ReplaySnapshotV1Service.start_replay_attempt` verifies available metadata, records an audit event and returns only `replay_attempt_id`. | API test `test_admin_replay_attempt_is_accepted_and_audited`; service audit tests in full suite. | PASS |
| AC5 | Manual purge is audited. | DELETE handler calls `ReplaySnapshotV1Service.purge_snapshot`, commits service audit and returns 204. | API test `test_admin_manual_purge_returns_204_and_commits_audit`; full suite service audit test. | PASS |
| AC6 | Non-admin access is denied. | All handlers use `require_admin_user`; no parallel auth gate added. | API test covers missing auth 401, user 403 and support 403. | PASS |
| AC7 | Missing snapshot states are covered. | `raise_unavailable_replay_snapshot` maps `not_found` to 404. | Parametrized API state test. | PASS |
| AC8 | Expired snapshot states are covered. | `raise_unavailable_replay_snapshot` maps `expired` to 410. | Parametrized API state test. | PASS |
| AC9 | Purged snapshot states are covered. | `raise_unavailable_replay_snapshot` maps `already_purged` to 410. | Parametrized API state test. | PASS |
| AC10 | Public replay paths are absent. | Only admin audit route contains `replay_snapshot_v1`; storage/security guards updated to allow only CS-297 admin paths. | Runtime route/OpenAPI test; `rg` negative scan for `/v1/replay_snapshot_v1`, `/v1/public/replay_snapshot_v1`, `/v1/support/replay_snapshot_v1`, `/api/replay_snapshot_v1`. | PASS |
| AC11 | Story evidence artifacts are persisted. | Evidence files under `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/`; generated traceability and final evidence updated. | `condamad_validate.py` PASS after evidence update. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
